import paramiko


def run_ssh_command(host: str, command: str) -> str:
    """Execute a command on a remote host via SSH and return its output.

    Parameters
    ----------
    host : str
        Remote host name or IP address.
    command : str
        Command to run on the remote host.

    Returns
    -------
    str
        Combined stdout and stderr output from the command.
    """
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=host,
            timeout=5,
            allow_agent=True,
            look_for_keys=True,
        )
        _, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        return out + err
    finally:
        client.close()
