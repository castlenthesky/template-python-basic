# some_file.py
import os
import sys
import pytest

# NOTE: path[0] is reserved for script path (or '' in REPL)
# NOTE: Use path.insert to have your directory evaluated
# before other places in module heirarchy
script_dir = os.path.dirname( __file__ )
mymodule_dir = os.path.join( script_dir, '..', 'src' )
sys.path.insert( 1, mymodule_dir )

import main

def test_answer():
    assert main.get_env_variable_example() == 'Hello World'
