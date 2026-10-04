# UUID/security migration

This release changes every application primary key and all application foreign keys to UUID v4. The project did not contain an Alembic migration history, so **do not run `Base.metadata.create_all()` against a production database and expect an integer schema to be converted**.

## Existing database

1. Back up the database.
2. Stop the application.
3. Provision a new database/schema using the new models (`python -m app.main` or your normal startup command).
4. Run `python seed.py` to create the three allowed classes and meal types.
5. Migrate legacy data with an explicit integer→UUID mapping for every legacy primary key and foreign key. Preserve the mappings for users, students, meal types, schedules, sessions, batches, devices, and response records.
6. Map legacy `students.class_name` to exactly one of `Anita B`, `Ada Lab`, or `Lovelace`; rows with any other value must be corrected before import.
7. Legacy users do not contain the new `first_name`, `last_name`, or `user_name` fields. Supply those values during import; usernames must be unique.
8. Choose the existing account that will become the single `SUPER_ADMIN` explicitly. Do not infer this from row order.
9. Reissue email-verification and refresh tokens after migration. Existing sessions must not be trusted.
10. Run the test suite and a read-only integrity check before switching application traffic.

For PostgreSQL, use a transaction where possible and keep the old database/schema until the application has passed its smoke tests. Because the old project had no migration framework, this repository deliberately does not contain a destructive automatic migration that could silently invent a Super Admin or silently discard legacy class data.

## Fresh database

```bash
python seed.py
```

Then start the API and create the first Super Admin through:

```text
POST /api/v1/auth/setup/first-super-admin
```

The endpoint is available only while no Super Admin exists.

## Required UUID invariant

After migration, every primary key and application foreign key must be UUID. The test suite includes a metadata-level assertion covering all application tables.
