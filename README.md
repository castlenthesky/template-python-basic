# my_project

## Quickstart
This project uses `uv` as to handle the virtual environment configuration, and package management. If you don't have `uv` you can install it by running:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once `uv` has been installed, use the following command to create the virtual environment and install necessary dependencies:

```bash
uv sync
```

## Repository Structure
```
my_project/
├── src/
│   └── main.py
├── .env
├── .coveragerc
├── pyproject.toml
└── README.md
```