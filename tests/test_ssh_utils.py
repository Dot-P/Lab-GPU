import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, project_root)

from ssh_utils import run_ssh_command

def test_run_ssh_command_ls_gpu1():
    result = run_ssh_command("GPU1", "ls")
    print("\n\n","="*5 + " GPU1 File " + "="*5)
    print(result)
    print("="*23)
    assert "findme.txt" in result
