import sys
import os

# 1) Add project root to sys.path so `import ssh_utils` works
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, project_root)

from ssh_utils import run_ssh_command

def test_run_ssh_command_ls_gpu1():
    # 2) Use the SSH alias 'GPU1' defined in ~/.ssh/config
    result = run_ssh_command("GPU1", "ls")
    # 3) (Optionally) print for local debugging; pytest -s will show it
    print("\n\n","="*5 + " GPU1 File " + "="*5)
    print(result)
    print("="*23)
    # 4) Assert that the known file is listed
    assert "findme.txt" in result
