# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with
# the License. A copy of the License is located at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file.
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.

"""
This is a wrapper around the Django's base postgres database API.
In case of Aurora DSQL, password is a SigV4 token which must be rotated every
N seconds. This module extends the base wrapper to handle this case.
"""

import logging
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from django.db.backends.postgresql import base

from .creation import DatabaseCreation
from .features import DatabaseFeatures
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor

from uuid import uuid4

from django.db.models.fields import (
    AutoField,
    BigAutoField,
    Field,
)

def uuid_to_int32():
    return uuid4().int & 0x7FFFFFFF

def uuid_to_int64():
    return uuid4().int & 0x7FFFFFFFFFFFFFFF

def patch_autofield(field_class, generator):
    def __init__(self, *args, **kwargs):
        kwargs["blank"] = True
        Field.__init__(self, *args, **kwargs)
        self.default = generator
    
    field_class.__init__ = __init__
    field_class.validators = []
    field_class.db_returning = False

# patch AutoFields to get default value from generator functions
patch_autofield(AutoField, uuid_to_int32) 
patch_autofield(BigAutoField, uuid_to_int64)

logger = logging.getLogger(__name__)


def get_aws_connection_params(params):
    """
    Get connection parameters to establish a connection to the Aurora DSQL
    cluster. Uses AWS SDK to generate the password token and sets it in the
    connection parameters.

    Args:
        params (dict): Parameter dictionary that client sets in DATABASES variable

    Returns:
        dict: returns a dictionary of connection parameters
    """
    region = params.pop("region", None)
    hostname = params.get("host")
    user = params.get("user")
    sslmode = params.get("sslmode", None)
    sslrootcert = params.get("sslrootcert", None)
    if sslrootcert is None and sslmode == 'verify-full':
        params["sslrootcert"] = "system"
    expires_in = params.pop("expires_in", None)
    aws_profile = params.pop("aws_profile", None)

    try:
        session = boto3.session.Session(
            profile_name=aws_profile) if aws_profile else boto3.session.Session()
        client = session.client("dsql", region_name=region)

        # Set correct IAM Auth token
        is_admin = user == 'admin'
        has_expires_in = expires_in is not None
        if is_admin and has_expires_in:
            params["password"] = client.generate_db_connect_admin_auth_token(
                hostname, region, expires_in)
        elif is_admin and not has_expires_in:
            params["password"] = client.generate_db_connect_admin_auth_token(
                hostname, region)
        elif not is_admin and has_expires_in:
            params["password"] = client.generate_db_connect_auth_token(
                hostname, region, expires_in)
        else:
            params["password"] = client.generate_db_connect_auth_token(
                hostname, region)

        params.setdefault("port", 5432)

    except (BotoCoreError, ClientError) as e:
        logger.error("Failed to generate DB auth token: %s", str(e))
        raise

    return params


class DatabaseWrapper(base.DatabaseWrapper):
    """
    A wrapper class that adapts the Django base API for Aurora DSQL
    """
    vendor = "dsql"
    display_name = "Aurora DSQL"
    # Override some types from the postgresql adapter.
    data_types = dict(
        base.DatabaseWrapper.data_types,
        DateTimeField="timestamptz",
    )
    data_types_suffix = dict(
        base.DatabaseWrapper.data_types_suffix,
        BigAutoField="", # Default value auto generated from gen_rand_int64
        # For now skipping small int because uuid does not fit in a smallint?
        SmallAutoField="",
        AutoField="", # Default value auto generated from gen_rand_int32
    )

    SchemaEditorClass = DatabaseSchemaEditor
    creation_class = DatabaseCreation
    features_class = DatabaseFeatures
    ops_class = DatabaseOperations

    def get_connection_params(self):
        params = super().get_connection_params()
        return get_aws_connection_params(params)

    def check_constraints(self, table_names=None):
        """
        Override to do nothing since SET CONSTRAINTS is not supported.
        """

    def disable_constraint_checking(self):
        """
        Override to do nothing since SET CONSTRAINTS is not supported.
        """
        return True

    def enable_constraint_checking(self):
        """
        Override to do nothing since SET CONSTRAINTS is not supported.
        """
