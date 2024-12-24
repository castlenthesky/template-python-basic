this project is scaffolding using `uv`. You can setup and run your environment by running `uv run src/main.py`. uv will setup a virtual environment, install dependencies, and run the code for you.

`setup.py` used to be the place where you put your installation script.
Since it is a python script, you can run arbitrary code inside of it. This is seen increasinly as a security risk and is subsequently being stripped out of `setup.py` and put into other configuration files such as pyproject.toml. 

`setup.cfg` houses the metadata about the project

`tests`
[This video](https://www.youtube.com/watch?v=DhUpxWjOhME&t=805s) has a lot of good details about test configuration.