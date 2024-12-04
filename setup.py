# Copyright 2024 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with
# the License. A copy of the License is located at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
import os
import re
import setuptools

ROOT = os.path.join(os.path.dirname(__file__), 'aurora_dsql_django')
VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.a-z\-]+)['"]''')
requires = ['boto3>=1.35.74,<2',
            'botocore>=1.35.74,<2']


def get_version():
    init = open(os.path.join(ROOT, '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


setuptools.setup(
    name='aurora_dsql_django',
    version=get_version(),
    description='Django adapter for Aurora DSQL',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Amazon Web Services',
    packages=setuptools.find_packages(),
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ]
)
