import os
from dotenv import load_dotenv

load_dotenv()

config = {
  'ENV_VARIABLE_VALUE': os.getenv('CONFIG_TEST') or '.ENV FILE NOT CONFIGURED FOR TEST'
}
