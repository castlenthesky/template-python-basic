import os

from dotenv import load_dotenv

load_dotenv()


def main(*args, **kwargs):
    return os.getenv("MY_VAR", "default_value")


if __name__ == "__main__":
    main()
