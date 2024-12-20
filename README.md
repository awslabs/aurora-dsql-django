# Aurora DSQL adapter for Django

This is the adapter for enabling development of Django applications using Aurora DSQL.

## Requirements

### Boto3

Aurora DSQL Django adapter needs boto3 to work. Follow the Boto3 [installation guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) to install Boto3

### Required Python versions

aurora_dsql_django requires Python 3.8 or later. 

Please see the link below for more detail to install Python:

* [Python Installation](https://www.python.org/downloads/)

### AWS credentials

Aurora DSQL Django adapter generates the IAM db auth token for every connection.
DB auth token is generated using AWS credentials. You must have configured valid
AWS credentials to be able to use the adapter. If not the connection to the 
cluster will not succeed.

## Getting Started

First, install the adapter using pip:

```pip install aurora_dsql_django```

### Define Aurora DSQL as the Engine for the Django App

Change the ``DATABASES`` variable in ``settings.py`` of your Django app. An example
is show below

```python
   DATABASES = {
        'default': {
            'HOST': '<your_cluster_id>.dsql.<region>.on.aws',
            'USER': 'admin', # or another user you have defined
            'NAME': 'postgres',
            'ENGINE': 'aurora_dsql_django',
            'OPTIONS': {
                'sslmode': 'require',
                'region': 'us-east-2',
                # (optional) Defaults to 'default' profile if nothing is set
                'aws_profile': 'user aws custom profile name' 
                # (optional) Default is 900 seconds i.e., 15 mins 
                'expires_in': <token expiry time time in seconds> 
                # (optional) If sslmode is 'verify-full' then use sslrootcert
                # variable to set the path to server root certificate
                # If no path is provided, the adapter looks into system certs
                # NOTE: Do not use it with 'sslmode': 'require'
                'sslrootcert': '<root certificate path>'
            }
        }
    }
```

For more info follow the [Aurora DSQL with Django example](examples/pet-clinic-app/README.md)

## Development

### Setup

Assuming that you have Python installed, set up your environment and installed the dependencies
like this instead of the `pip install aurora-dsql-django` defined above:

```
$ git clone https://github.com/awslabs/aurora-dsql-django
$ cd aurora-dsql-django
$ python -m venv venv
...
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install -e .
```

### Running Tests

You can run the unit tests with this command:

```
$ pytest --cov=aurora_dsql_django aurora_dsql_django/tests/unit/ --cov-report=xml
```

You can run the integration tests with this command:
```
$ export CLUSTER_ENDPOINT=<your cluster endpoint>
$ export DJANGO_SETTINGS_MODULE=aurora_dsql_django.tests.test_settings
$ pytest -v aurora_dsql_django/tests/integration/
```

### Documentation 

Sphinx is used for documentation. You can generate HTML locally with the following:

```
$ pip install -r requirements-docs.txt
$ pip install -e .
$ cd docs
$ make html
```

## Getting Help

Please use these community resources for getting help.
* Open a support ticket with [AWS Support](http://docs.aws.amazon.com/awssupport/latest/user/getting-started.html).
* If you think you may have found a bug, please open an [issue](https://github.com/awslabs/aurora-dsql-django/issues/new).

## Opening Issues

If you encounter a bug with the Aurora DSQL Django adapter, we would like to hear about it. Please search the [existing issues](https://github.com/awslabs/aurora-dsql-django/issues) and see if others are also experiencing the issue before opening a new issue. When opening a new issue please follow the template.

The GitHub issues are intended for bug reports and feature requests. For help and questions with using Aurora DSQL Django adapter, please make use of the resources listed in the [Getting Help](https://github.com/awslabs/aurora-dsql-django#getting-help) section. Keeping the list of open issues lean will help us respond in a timely manner.

## License

This library is licensed under the Apache 2.0 License.
