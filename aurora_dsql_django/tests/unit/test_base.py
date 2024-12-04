import unittest
from unittest.mock import patch, MagicMock
from aurora_dsql_django.base import get_aws_connection_params, DatabaseWrapper
from botocore.exceptions import BotoCoreError


class TestAuroraDSQLBackend(unittest.TestCase):

    def setUp(self):
        self.base_params = {
            "host": "test-host",
            "region": "us-west-2",
            "user": "test-user",
            "name": "test-db"
        }

    @patch('aurora_dsql_django.base.boto3.session.Session')
    def test_get_aws_connection_params_without_profile(self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.generate_db_connect_auth_token.return_value = "test-token"

        result = get_aws_connection_params(self.base_params.copy())

        mock_session.assert_called_once_with()
        mock_session.return_value.client.assert_called_once_with(
            "dsql", region_name="us-west-2")
        mock_client.generate_db_connect_auth_token.assert_called_once_with(
            "test-host", "us-west-2")
        self.assertEqual(result["password"], "test-token")
        self.assertNotIn("region", result)

    @patch('aurora_dsql_django.base.boto3.session.Session')
    def test_get_aws_connection_params_with_admin_user(self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.generate_db_connect_admin_auth_token.return_value = "admin-token"
        self.base_params["user"] = "admin"
        result = get_aws_connection_params(self.base_params.copy())

        mock_session.assert_called_once_with()
        mock_session.return_value.client.assert_called_once_with(
            "dsql", region_name="us-west-2")
        mock_client.generate_db_connect_admin_auth_token.assert_called_once_with(
            "test-host", "us-west-2")
        self.assertEqual(result["password"], "admin-token")
        self.assertNotIn("region", result)
        self.base_params["user"] = "test-user"

    @patch('aurora_dsql_django.base.boto3.session.Session')
    def test_get_aws_connection_params_with_admin_user_and_expires_in(
            self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.generate_db_connect_admin_auth_token.return_value = "admin-token-with-expires-in"
        self.base_params["user"] = "admin"
        self.base_params["expires_in"] = 10
        result = get_aws_connection_params(self.base_params.copy())

        mock_session.assert_called_once_with()
        mock_session.return_value.client.assert_called_once_with(
            "dsql", region_name="us-west-2")
        mock_client.generate_db_connect_admin_auth_token.assert_called_once_with(
            "test-host", "us-west-2", 10)
        self.assertEqual(result["password"], "admin-token-with-expires-in")
        self.assertNotIn('expires_in', result)
        self.assertNotIn("region", result)
        self.base_params["user"] = "test-user"
        self.base_params["expires_in"] = None

    @patch('aurora_dsql_django.base.boto3.session.Session')
    def test_get_aws_connection_params_with_non_admin_user_and_expires_in(
            self, mock_session):
        mock_client = MagicMock()
        mock_session.return_value.client.return_value = mock_client
        mock_client.generate_db_connect_auth_token.return_value = "test-token-with-expires-in"
        self.base_params["expires_in"] = 10000

        result = get_aws_connection_params(self.base_params.copy())

        mock_session.assert_called_once_with()
        mock_session.return_value.client.assert_called_once_with(
            "dsql", region_name="us-west-2")
        mock_client.generate_db_connect_auth_token.assert_called_once_with(
            "test-host", "us-west-2", 10000)
        self.assertEqual(result["password"], "test-token-with-expires-in")
        self.assertNotIn('expires_in', result)
        self.assertNotIn("region", result)
        self.base_params["expires_in"] = None

    @patch('aurora_dsql_django.base.boto3.session.Session')
    def test_get_aws_connection_params_with_profile(self, mock_session):
        params = self.base_params.copy()
        params["aws_profile"] = "test-profile"

        get_aws_connection_params(params)

        mock_session.assert_called_once_with(profile_name="test-profile")

    @patch('aurora_dsql_django.base.boto3.session.Session')
    def test_get_aws_connection_params_error_handling(self, mock_session):
        mock_session.return_value.client.side_effect = BotoCoreError()

        with self.assertRaises(BotoCoreError):
            get_aws_connection_params(self.base_params.copy())

    def test_database_wrapper_data_types(self):
        wrapper = DatabaseWrapper({})
        self.assertEqual(wrapper.data_types['BigAutoField'], "uuid")
        self.assertEqual(wrapper.data_types['AutoField'], "uuid")
        self.assertEqual(wrapper.data_types['DateTimeField'], "timestamptz")

    def test_database_wrapper_data_types_suffix(self):
        wrapper = DatabaseWrapper({})
        self.assertEqual(
            wrapper.data_types_suffix['BigAutoField'],
            "DEFAULT gen_random_uuid()")
        self.assertEqual(wrapper.data_types_suffix['SmallAutoField'], "")
        self.assertEqual(
            wrapper.data_types_suffix['AutoField'],
            "DEFAULT gen_random_uuid()")

    @patch('aurora_dsql_django.base.get_aws_connection_params')
    def test_database_wrapper_get_connection_params(self, mock_get_aws_params):
        mock_get_aws_params.return_value = {
            "password": "test-token", "port": 5432}

        # Mock the super().get_connection_params() call
        with patch('django.db.backends.postgresql.base.DatabaseWrapper.get_connection_params') as mock_super:
            mock_super.return_value = {"user": "test-user", "name": "test-db"}

            wrapper = DatabaseWrapper({})
            result = wrapper.get_connection_params()

        # Check that get_aws_connection_params was called
        mock_get_aws_params.assert_called_once()

        # Check the final result
        self.assertEqual(result, {"password": "test-token", "port": 5432})
        self.assertNotIn("user", result)
        self.assertNotIn("name", result)

        # Verify that super().get_connection_params() was called
        mock_super.assert_called_once()

    def test_check_constraints(self):
        wrapper = DatabaseWrapper({})
        # This should not raise any exception
        wrapper.check_constraints()
        wrapper.check_constraints(table_names=['table1', 'table2'])

    def test_disable_constraint_checking(self):
        wrapper = DatabaseWrapper({})
        result = wrapper.disable_constraint_checking()
        self.assertTrue(result)

    def test_enable_constraint_checking(self):
        wrapper = DatabaseWrapper({})
        # This should not raise any exception
        wrapper.enable_constraint_checking()

    def test_constraint_checks_disabled(self):
        wrapper = DatabaseWrapper({})
        with wrapper.constraint_checks_disabled():
            # This context manager should not raise any exception
            pass


if __name__ == '__main__':
    unittest.main()
