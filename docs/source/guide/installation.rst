.. _guide_installation:

Installation
============

Adapter Installation
--------------------
Install the latest Aurora DSQL Django adapter release via :command:`pip`

.. code-block:: sh

    pip install aurora-dsql-django

You may also install a specific version

.. code-block:: sh

    pip install aurora-dsql-django==1.0.0-rc.2


Additional Dependencies
-----------------------
Aurora DSQL Django adapter needs boto3 to work. Follow the Boto3 [installation guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)
to install Boto3


Configuration
-------------
Before you can begin using the Aurora DSQL Django adapter, you should set up authentication
credentials. Credentials for your AWS account can be found in the
`IAM Console <https://console.aws.amazon.com/iam/home>`_. You can
create or use an existing user. Go to manage access keys and
generate a new set of keys.

If you have the `AWS CLI <http://aws.amazon.com/cli/>`_
installed, then you can use it to configure your credentials file:

.. code-block:: sh

    aws configure

Alternatively, you can create the credential file yourself. By default,
its location is at ``~/.aws/credentials``:

.. code-block:: sh

    [default]
    aws_access_key_id = YOUR_ACCESS_KEY
    aws_secret_access_key = YOUR_SECRET_KEY

You may also want to set a default region. This can be done in the
configuration file. By default, its location is at ``~/.aws/config``

.. code-block:: sh

    [default]
    region=us-east-1

Alternatively, you can pass a ``region_name`` when creating the driver.

This sets up credentials for the default profile as well as a default
region to use when creating connections.