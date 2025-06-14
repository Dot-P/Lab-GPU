from typing import Dict, Optional
import subprocess

from ssh_utils import run_ssh_command

def parse_gpu_process_mapping(gpu_query_out: str, apps_query_out: str) -> Dict[int, Optional[int]]:
    """Parse nvidia-smi outputs and map GPU index to PID.

    Parameters
    ----------
    gpu_query_out : str
        Output from ``nvidia-smi --query-gpu=index,uuid --format=csv,noheader``.
    apps_query_out : str
        Output from ``nvidia-smi --query-compute-apps=gpu_uuid,pid --format=csv,noheader``.

    Returns
    -------
    Dict[int, Optional[int]]
        Mapping from GPU index to PID using that GPU. ``None`` means no process.
    """

    index_to_uuid: Dict[int, str] = {}
    for line in gpu_query_out.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            continue
        try:
            idx = int(parts[0])
        except ValueError:
            continue
        uuid = parts[1]
        index_to_uuid[idx] = uuid

    uuid_to_pid: Dict[str, int] = {}
    for line in apps_query_out.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if 'No running compute processes found' in line:
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 2:
            continue
        uuid = parts[0]
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        if uuid not in uuid_to_pid:
            uuid_to_pid[uuid] = pid

    mapping: Dict[int, Optional[int]] = {}
    for idx, uuid in index_to_uuid.items():
        mapping[idx] = uuid_to_pid.get(uuid)

    return mapping


def get_username_by_pid(host: str, pid: int) -> Optional[str]:
    """Return the username owning a process.

    Parameters
    ----------
    host : str
        Hostname or IP address of the remote machine.
    pid : int
        Target process ID.

    Returns
    -------
    Optional[str]
        Username of the process or ``None`` if it cannot be determined.
    """
    try:
        cmd = f"ps -o user= -p {pid}"
        result = run_ssh_command(host, cmd)
        return result.strip() if result.strip() else None
    except Exception:
        return None
