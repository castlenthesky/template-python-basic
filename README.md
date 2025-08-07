# my_project

## Quickstart
This project uses `uv` as to handle the virtual environment configuration, and package management. If you don't have `uv` you can install it by running:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once `uv` has been installed, you can run the application with:

```bash
uv run src/main.py
```

OR install all dependencies/features with

```bash
uv sync
```

## Repository Structure
```
my_project/
├── src/
│   ├── api/                  # simple FastAPI example
│   ├── config/               # application settings and configuration
│   ├── dagster_definitions/  # example dagster asset definitions
│   └── main.py
├── .env
├── pyproject.toml
└── README.md
```


## Running the Docker Container
First, export or set the appropriate environmental variables:
```
export DB_PASSWORD="mydbpassword"
export DB_USER="mydbuser"
export DB_NAME="mydbname"
export DB_HOST="mydbhost"
export ACCESS_TOKEN_SECRET_KEY="mysecretkey"
```

Next, run the build command, and invoke the variables to pass to the container:
```
docker build --target=production \
             --secret id=DB_PASSWORD \
             --secret id=DB_USER \
             --secret id=DB_NAME \
             --secret id=DB_HOST \
             --secret id=ACCESS_TOKEN_SECRET_KEY \
             -f Dockerfile . -t my_project
```

## Dagster and Asset Materialization

After running `uv sync` you can launch dagster's service and web UI by running `dagster dev` inside of your virtual environment.

Dagster configuration is managed in the `pyproject.toml` file.