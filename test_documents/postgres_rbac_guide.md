# PostgreSQL Role-Based Access Control Architecture
To implement principle of least privilege:
1. Create read-only role: `CREATE ROLE read_only_app;`
2. Grant schema usage: `GRANT USAGE ON SCHEMA public TO read_only_app;`
3. Restrict administrative superuser connections from application pools.
Always enforce connection encryption via TLS with certificate validation.