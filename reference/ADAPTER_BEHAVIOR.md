# Aurora DSQL Django Adapter Behavior

This document describes how the Aurora DSQL Django adapter modifies standard Django behavior to work with the features provided by Aurora DSQL.

## AutoField uses UUID instead of integers

**Behavior:** The Aurora DSQL adapter automatically converts Django's `AutoField` and `BigAutoField` to use UUID primary keys instead of auto-incrementing integers.

**Impact:** 
- All primary keys will be UUIDs (e.g. `8fcc0dd2-1d96-4428-a619-f0e43996dc19`) instead of integers (e.g. `1`, `2`, `3`)
- Sort order of primary keys is not predictable
- URLs, session data, etc. may contain UUID strings

**Why this is necessary:** Aurora DSQL does not support auto-incrementing sequences. UUID primary keys are recommended.

**Limitations:** This is a best-effort compatibility approach. Not all Django `contrib` apps are compatible with UUID primary keys. For new applications, customers are encouraged to use `UUIDField` directly instead of `AutoField` where possible.

## Server-side cursors automatically disabled

**Behavior:** The Aurora DSQL adapter automatically sets `DISABLE_SERVER_SIDE_CURSORS = True` for database connections unless otherwise configured.

**Impact:** Large querysets will load entirely into memory instead of streaming, which may affect memory usage for large datasets.

**Why this is necessary:** Aurora DSQL does not support server-side cursors (`DECLARE CURSOR` statements).

## Foreign key constraints are skipped during migrations

**Behavior:** The Aurora DSQL adapter automatically skips foreign key constraint creation and removal operations during migrations.

**Impact:** 
- Foreign key constraints are not enforced at the database level
- Applications must maintain referential integrity through Django model validation and application logic
- Existing migrations from non-DSQL databases will continue to work without modification

**Why this is necessary:** Aurora DSQL does not support foreign key constraints. This approach maintains compatibility with existing Django migrations while preventing constraint-related errors.

## Check constraints are skipped during migrations

**Behavior:** The Aurora DSQL adapter automatically skips check constraint creation and removal operations during migrations.

**Impact:**
- Check constraints are not enforced at the database level
- Applications must maintain data validation through Django model validation and application logic
- Existing migrations from non-DSQL databases will continue to work without modification

**Why this is necessary:** Aurora DSQL does not support table check constraints. This approach maintains compatibility with existing Django migrations while preventing constraint-related errors.

## Expression indexes are skipped during migrations

**Behavior:** The Aurora DSQL adapter automatically skips creation and removal of expression indexes during migrations.

**Impact:**
- Expression indexes (e.g., `Index(Upper('name'))`) are not created during migration operations
- Query performance may be affected for queries that would benefit from expression indexes
- Existing migrations containing expression indexes will execute without errors

**Why this is necessary:** Aurora DSQL does not support PostgreSQL expression indexes or operator classes. This approach maintains compatibility with existing Django migrations while preventing constraint-related errors.

