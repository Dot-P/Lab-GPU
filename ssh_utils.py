import os
import paramiko
from paramiko.proxy import ProxyCommand
from paramiko.config import SSHConfig

def run_ssh_command(host_alias: str, command: str) -> str:
    """
    Execute a command on a remote host via SSH using ~/.ssh/config settings.

    Parameters
    ----------
    host_alias : str
        SSH config alias (e.g., "GPU1") or direct hostname/IP.
    command : str
        Command to run on the remote host.

    Returns
    -------
    str
        Combined stdout and stderr output from the command.
    """
    # Parse the user's SSH config file
    ssh_config = SSHConfig()
    config_path = os.path.expanduser("~/.ssh/config")
    if os.path.exists(config_path):
        with open(config_path) as f:
            ssh_config.parse(f)
    cfg = ssh_config.lookup(host_alias)

    # Extract connection parameters, falling back to defaults
    hostname     = cfg.get("hostname", host_alias)
    port         = int(cfg.get("port", 22))
    username     = cfg.get("user", None)
    identityfile = cfg.get("identityfile", None)  # can be a list
    proxy_cmd    = cfg.get("proxycommand", None)

    # Create a proxy socket if a ProxyCommand is specified
    proxy_sock = ProxyCommand(proxy_cmd) if proxy_cmd else None

    # Initialize and configure the SSH client
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Establish the SSH connection with a 5-second timeout
        client.connect(
            hostname     = hostname,
            port         = port,
            username     = username,
            key_filename = identityfile,
            timeout      = 5,
            allow_agent  = True,
            look_for_keys= True,
            sock         = proxy_sock,
        )

        # Execute the command and collect output
        _, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        return out + err

    finally:
        # Ensure the connection is always closed
        client.close()
