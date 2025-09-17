import unittest
from aurora_dsql_django.features import DatabaseFeatures
from django.db.models.fields import AutoField, BigAutoField
from unittest.mock import patch, MagicMock
from django.db.models.fields import NOT_PROVIDED

class TestDatabaseFeatures(unittest.TestCase):

    def setUp(self):
        # DatabaseFeatures usually requires a connection object, but for these tests,
        # we can pass None as we're only checking static attributes
        self.features = DatabaseFeatures(None)

    def test_can_rollback_ddl(self):
        self.assertFalse(self.features.can_rollback_ddl)

    def test_supports_forward_references(self):
        self.assertTrue(self.features.supports_forward_references)

    def test_supports_foreign_keys(self):
        self.assertFalse(self.features.supports_foreign_keys)

    def test_can_create_inline_fk(self):
        self.assertFalse(self.features.can_create_inline_fk)

    def test_can_clone_databases(self):
        self.assertFalse(self.features.can_clone_databases)

    def test_can_defer_constraint_checks(self):
        self.assertFalse(self.features.can_defer_constraint_checks)

    def test_supports_deferrable_unique_constraints(self):
        self.assertFalse(self.features.supports_deferrable_unique_constraints)

    def test_has_native_json_field(self):
        self.assertFalse(self.features.has_native_json_field)

    def test_can_introspect_materialized_views(self):
        self.assertFalse(self.features.can_introspect_materialized_views)

    def test_uses_savepoints(self):
        self.assertFalse(self.features.uses_savepoints)

    def test_can_release_savepoints(self):
        self.assertFalse(self.features.can_release_savepoints)

    def test_can_rename_index(self):
        self.assertTrue(self.features.can_rename_index)

    def test_inheritance(self):
        from django.db.backends.postgresql.features import DatabaseFeatures as PostgreSQLDatabaseFeatures
        self.assertIsInstance(self.features, PostgreSQLDatabaseFeatures)

    def test_overridden_attributes(self):
        from django.db.backends.postgresql.features import DatabaseFeatures as PostgreSQLDatabaseFeatures
        postgresql_features = PostgreSQLDatabaseFeatures(None)

        # Check that we've actually overridden some attributes
        self.assertNotEqual(
            self.features.can_rollback_ddl,
            postgresql_features.can_rollback_ddl)
        self.assertNotEqual(
            self.features.supports_foreign_keys,
            postgresql_features.supports_foreign_keys)
        self.assertNotEqual(
            self.features.can_clone_databases,
            postgresql_features.can_clone_databases)
        self.assertNotEqual(
            self.features.has_native_json_field,
            postgresql_features.has_native_json_field)

class TestAutoFieldDefaults(unittest.TestCase):
    
    @patch('aurora_dsql_django.base.boto3.session.Session')
    def setUp(self, _):
        # Setup a mock session to trigger patch_autofield in base.py which checks 
        # for the flag ENABLE_ID_GENERATION_FOR_AUTO_FIELDS to enable the feature"""
        pass
    
    def test_autofield_generates_32bit_integers(self):
        field = AutoField()
        value = field.default()
        
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 2147483647)  # Max 32-bit signed int
    
    def test_bigautofield_generates_64bit_integers(self):
        field = BigAutoField()
        value = field.default()
        
        self.assertIsInstance(value, int)
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 9223372036854775807)  # Max 64-bit signed int
    
    def test_values_are_unique(self):
        auto_field = AutoField()
        big_field = BigAutoField()
        
        auto_values = [auto_field.default() for _ in range(10)]
        big_values = [big_field.default() for _ in range(10)]
        
        self.assertEqual(len(auto_values), len(set(auto_values)))
        self.assertEqual(len(big_values), len(set(big_values)))

if __name__ == '__main__':
    unittest.main()
