import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, project_root)

from ssh_utils import run_ssh_command
from gpu_parser import parse_gpu_process_mapping


def test_gpu_mapping_gpu1():
    gpu_cmd = "nvidia-smi --query-gpu=index,uuid --format=csv,noheader"
    apps_cmd = "nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader"
    index_out = run_ssh_command("GPU1", gpu_cmd)
    apps_out = run_ssh_command("GPU1", apps_cmd)
    mapping = parse_gpu_process_mapping(index_out, apps_out)
    print("\n\n","="*5 + " GPU1 Mapping " + "="*5)
    print(mapping)
    print("="*23)
    assert len(mapping) == 3
