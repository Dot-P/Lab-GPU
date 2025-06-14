import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import types
from unittest import mock

# create a minimal paramiko stub if paramiko is missing
if 'paramiko' not in sys.modules:
    paramiko_stub = types.ModuleType('paramiko')
    class AutoAddPolicy:  # noqa: D401
        """Placeholder policy class."""
        pass
    class SSHClient:
        pass
    paramiko_stub.AutoAddPolicy = AutoAddPolicy
    paramiko_stub.SSHClient = SSHClient
    sys.modules['paramiko'] = paramiko_stub

import paramiko

from ssh_utils import run_ssh_command


def test_run_ssh_command_success():
    mock_client = mock.MagicMock()
    stdout_mock = mock.MagicMock()
    stdout_mock.read.return_value = b"out"
    stderr_mock = mock.MagicMock()
    stderr_mock.read.return_value = b"err"
    mock_client.exec_command.return_value = (None, stdout_mock, stderr_mock)

    with mock.patch.object(paramiko, "SSHClient", return_value=mock_client):
        result = run_ssh_command("example.com", "echo test")

    assert result == "outerr"
    mock_client.connect.assert_called_once_with(
        hostname="example.com",
        timeout=5,
        allow_agent=True,
        look_for_keys=True,
    )
    mock_client.load_system_host_keys.assert_called_once()
    mock_client.set_missing_host_key_policy.assert_called_once()
    mock_client.close.assert_called_once()


def test_run_ssh_command_ls_gpu1():
    mock_client = mock.MagicMock()
    stdout_mock = mock.MagicMock()
    stdout_mock.read.return_value = b"file1\nfile2\n"
    stderr_mock = mock.MagicMock()
    stderr_mock.read.return_value = b""
    mock_client.exec_command.return_value = (None, stdout_mock, stderr_mock)

    with mock.patch.object(paramiko, "SSHClient", return_value=mock_client):
        result = run_ssh_command("GPU1", "ls")

    assert result == "file1\nfile2\n"
    mock_client.connect.assert_called_once_with(
        hostname="GPU1",
        timeout=5,
        allow_agent=True,
        look_for_keys=True,
    )
    mock_client.load_system_host_keys.assert_called_once()
    mock_client.set_missing_host_key_policy.assert_called_once()
    mock_client.close.assert_called_once()
