# Development

Preparation
===============
1) Change into the `backend` directory.
1) Create a virtual environment:
    ```
    python -m venv .venv39
    ```
1) Activate it:
    On Windows via:
    ```
    .venv39/Scripts/activate
    ```
    On Linux/MacOS:
    ```
    source .venv39/bin/activate
    ```
1) Install required packages: 
    ```
    pip install .
    pip install "uvicorn[standard]"
    ```
1) Create a folder config in the root directory of this project.
1) In the config folder, create a file `config.ini`. For all configuration keys, please check `t4cclient/config.py`.
1) Also, you might place a `pubkey.pem` in the config folder for OAUTH.
1) Setup a PostgreSQL Database and set the config key `DATABASE_URL` in the format `postgresql://scott:tiger@localhost:5432/mydatabase`


Run the project
===============

```
uvicorn t4cclient.__main__:app
```

Database migrations
===============

To manually migrate the database (in most cases this is not necessary as the database is automatically migrated on startup): 
```
cd t4cclient
alembic upgrade head
```

To create an upgrade script automatically (this will compare the current database state with the models): 
```
cd t4cclient
alembic revision --autogenerate -m "Commit message"
```

# Docker

## Build the image

Please run: 
```
docker build -t t4c/client/backend .
```

## Run the Container

```
docker run \
    -v path/to/pubkey.pem:/backend/config # Mount the OAUTH public key
    -e CONFIG_KEY=CONFIG_VALUE # Mount every config variable as environment variables (see `t4cclient/core/config.py`)
    t4c/client/backend
```