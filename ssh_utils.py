import os
import paramiko
from paramiko.proxy import ProxyCommand
from paramiko.config import SSHConfig


class SSHSession:
    """Maintain a persistent SSH session for running multiple commands.

    Parameters
    ----------
    host_alias : str
        SSH config alias (e.g., ``"GPU1"``) or direct hostname/IP.
    """

    def __init__(self, host_alias: str):
        self.host_alias = host_alias
        self.client: paramiko.SSHClient | None = None

    # ------------------------------------------------------------------
    def __enter__(self):
        """Establish the SSH connection using ``~/.ssh/config`` settings."""
        ssh_config = SSHConfig()
        config_path = os.path.expanduser("~/.ssh/config")
        if os.path.exists(config_path):
            with open(config_path) as f:
                ssh_config.parse(f)
        cfg = ssh_config.lookup(self.host_alias)

        hostname = cfg.get("hostname", self.host_alias)
        port = int(cfg.get("port", 22))
        username = cfg.get("user", None)
        identityfile = cfg.get("identityfile", None)
        proxy_cmd = cfg.get("proxycommand", None)

        proxy_sock = ProxyCommand(proxy_cmd) if proxy_cmd else None

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=hostname,
            port=port,
            username=username,
            key_filename=identityfile,
            timeout=5,
            allow_agent=True,
            look_for_keys=True,
            sock=proxy_sock,
        )
        return self

    # ------------------------------------------------------------------
    def run(self, command: str) -> str:
        """Execute a command on the active SSH session."""
        if self.client is None:
            raise RuntimeError("SSH session is not connected")
        _, stdout, stderr = self.client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        return out + err

    # ------------------------------------------------------------------
    def __exit__(self, exc_type, exc, tb):
        if self.client is not None:
            self.client.close()
            self.client = None

def run_ssh_command(host_alias: str, command: str) -> str:
    """Execute a single command on a remote host.

    This is a convenience wrapper around :class:`SSHSession` for backwards
    compatibility.  Each invocation opens a new session, runs the command, and
    then closes the connection.
    """
    with SSHSession(host_alias) as session:
        return session.run(command)
