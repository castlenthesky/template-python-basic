import os

from main import main


def test_main():
    os.environ["MY_VAR"] = "123"

    assert main() == "123"
