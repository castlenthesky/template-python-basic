# my_project

## Quickstart
This project uses `uv` as to handle the virtual environment configuration, and package management. If you don't have `uv` you can install it by running:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once `uv` has been installed, you can run the application with

```bash
uv run src/main.py
```

## Repository Structure
```
my_project/
├── .assets/ # dagster asset materialization target (local, symlink, or containered)
├── src/
│   ├── asset_definitions/  # dagster asset definitions
│   ├── api/ 
│   └── main.py
├── .env
├── .coveragerc
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
Standards for our organization involve materializing assets to the `.assets` directory in the root of a project. These can be mapped out of containers and into whatever functional directory you want. Also, on local development the `.asset` folders can be symlinked together across dagster-projects to simulate a production environment with shared storage between containers.