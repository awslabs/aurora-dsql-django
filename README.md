# Aurora DSQL adapter for Django

<a href="https://pypi.org/project/aurora-dsql-django"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/aurora-dsql-django?style=for-the-badge"></a>

This is the adapter for enabling development of Django applications using Aurora DSQL.

## Requirements

### Boto3

Aurora DSQL Django adapter needs boto3 to work. Follow the Boto3 [installation guide](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) to install Boto3

### Required Python versions

aurora_dsql_django requires Python 3.8 or later. 

Please see the link below for more details to install Python:

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
is shown below:

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
                'aws_profile': 'user aws custom profile name',
                # (optional) Default is 900 seconds i.e., 15 mins 
                'expires_in': <token expiry time in seconds>,
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

Assuming that you have Python installed, set up your environment and install the dependencies
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

Please use these community resources for getting help:
* Open a support ticket with [AWS Support](http://docs.aws.amazon.com/awssupport/latest/user/getting-started.html).
* If you think you may have found a bug, please open an [issue](https://github.com/awslabs/aurora-dsql-django/issues/new).

## Known Issues and Solutions

### 1. When running migrations with the following Django Contrib Apps, you may encounter not-null constraint errors
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions']
```

Error Message:

```
django.db.utils.IntegrityError: null value in column "name" of relation "django_content_type" violates not-null constraint
```

#### Solution: Allow null values for the following columns
- ```name``` from the table ```django_content_type```
    - Locate the installed django library in the site-packages folder (within the venv folder)
    - Navigate to
        ```
        venv/lib/python3.13/site-packages/django/contrib/contenttypes/migrations/0001_initial.py
        ```
    - Modify the ```name``` field by adding ```null=True``` under ```migrations.CreateModel(name="ContentType")```  and save your change
        ```
        #0001_initial.py

        # From
        ("name", models.CharField(max_length=100)),
        
        # To
        ("name", models.CharField(max_length=100, null=True)),
        ```

- ```last_login``` from the table ```auth_user```

    - Navigate to
        ```
        venv/lib/python3.13/site-packages/django/contrib/auth/migrations/0001_initial.py
        ```
     - Modify the ```last_login``` field by adding ```null=True``` under ```migrations.CreateModel(name="User")``` and save your change

        ```
        # 0001_initial.py
        
        # From
        (
            "last_login",
            models.DateTimeField(
                default=timezone.now, verbose_name="last login"
            ),
        ),

        # To   
        (
            "last_login",
            models.DateTimeField(
                default=timezone.now, verbose_name="last login", null=True
            ),
        ),
        ```
 

### 2. Null is used as the primary key during insertion for tables related to Django Contrib Apps 

#### Solution: Ensure auto primary key generation is enabled 
- Add the attribute ```'ENABLE_ID_GENERATION_FOR_AUTO_FIELDS': True``` to DATABASES
- Ensure the ```DEFAULT_AUTO_FIELD``` in ```settings.py``` is set to either ```django.db.models.BigAutoField``` or ```django.db.models.AutoField``` 

Note: This will automatically generate a default value for the AutoField and BigAutoField which can be used for the primary key. 
    

``` 
#settings.py

DATABASES = {
    'default': {
        'HOST': <HOST>,
        'USER': <USER_NAME>,
        'NAME': 'postgres',
        'ENGINE': 'aurora_dsql_django',
        'ENABLE_ID_GENERATION_FOR_AUTO_FIELDS': True,
        'OPTIONS': {
            'sslmode': 'verify-full',
            'region': 'us-east-1'
        }
    }
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```


### 3. DeclareCursor is not supported

#### Solution: Disable Server Side Cursors
- Add the attribute ```'DISABLE_SERVER_SIDE_CURSORS': True``` to DATABASES in ```settings.py```. Note: ```DISABLE_SERVER_SIDE_CURSORS``` should be at the same level as ```OPTIONS```, not within it
```
#settings.py

DATABASES = {
    'default': {
        'HOST': <HOST>,
        'USER': <USER_NAME>,
        'NAME': 'postgres',
        'ENGINE': 'aurora_dsql_django',
        'DISABLE_SERVER_SIDE_CURSORS': True, # Fixes unsupported statement: DeclareCursor 
        'OPTIONS': {
            'sslmode': 'verify-full',
            'region': 'us-east-1'
        }
    }
}
```



## Opening Issues

If you encounter a bug with the Aurora DSQL Django adapter, we would like to hear about it. Please search the [existing issues](https://github.com/awslabs/aurora-dsql-django/issues) and see if others are also experiencing the issue before opening a new issue. When opening a new issue please follow the template.

The GitHub issues are intended for bug reports and feature requests. For help and questions with using Aurora DSQL Django adapter, please make use of the resources listed in the [Getting Help](https://github.com/awslabs/aurora-dsql-django#getting-help) section. Keeping the list of open issues lean will help us respond in a timely manner.

## License

This library is licensed under the Apache 2.0 License.
