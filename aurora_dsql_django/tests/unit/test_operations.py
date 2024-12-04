import unittest
from aurora_dsql_django.operations import DatabaseOperations


class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        # DatabaseOperations usually requires a connection object, but for these tests,
        # we can pass None as we're only checking static attributes and methods
        self.ops = DatabaseOperations(None)

    def test_cast_data_types(self):
        expected_cast_data_types = {
            "AutoField": "uuid",
            "BigAutoField": "uuid",
            "SmallAutoField": "smallint",
        }
        self.assertEqual(self.ops.cast_data_types, expected_cast_data_types)

    def test_deferrable_sql(self):
        self.assertEqual(self.ops.deferrable_sql(), "")

    def test_deferrable_sql_no_arguments(self):
        # Ensure the method doesn't accept any arguments
        with self.assertRaises(TypeError):
            self.ops.deferrable_sql(True)

    def test_inheritance(self):
        from django.db.backends.postgresql.operations import DatabaseOperations as PostgreSQLDatabaseOperations
        self.assertIsInstance(self.ops, PostgreSQLDatabaseOperations)

    def test_overridden_attributes(self):
        from django.db.backends.postgresql.operations import DatabaseOperations as PostgreSQLDatabaseOperations
        postgresql_ops = PostgreSQLDatabaseOperations(None)

        # Check that we've actually overridden some attributes
        self.assertNotEqual(
            self.ops.cast_data_types,
            postgresql_ops.cast_data_types)

    def test_cast_data_types_autofield(self):
        self.assertEqual(self.ops.cast_data_types['AutoField'], 'uuid')

    def test_cast_data_types_bigautofield(self):
        self.assertEqual(self.ops.cast_data_types['BigAutoField'], 'uuid')

    def test_cast_data_types_smallautofield(self):
        self.assertEqual(
            self.ops.cast_data_types['SmallAutoField'],
            'smallint')


if __name__ == '__main__':
    unittest.main()
