# Database Setup

This folder contains a minimal standalone script for verifying a local MySQL
connection using `mysql-connector-python`.

## Files

- `config.cnf`: Connection settings (host, port, user, password, database)
- `connect.py`: Simple connection test script
- `01_create_tables_mysql.sql`: MySQL schema (creates database + tables)
- `02_seed_data_mysql.sql`: Seed data inserts
- `setup.py`: Programmatic setup (creates database + inserts data)

## Usage

1. Edit `config.cnf` with your MySQL credentials.
2. Install the driver:

```bash
pip install mysql-connector-python
```

3. Run the connection test:

```bash
python connect.py
```

4. Run the full setup (creates DB + inserts data):

```bash
python setup.py
```
