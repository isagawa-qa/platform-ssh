"""Fixtures."""
import sys,pytest
from pathlib import Path
from unittest.mock import MagicMock
sys.path.insert(0,str(Path(__file__).parent.parent))
class MockSSH:
    def __init__(self): self.client=MagicMock()
    def connect(self): return self
    def execute(self,cmd): return {"command":cmd,"stdout":"hello","stderr":"","exit_code":0,"passed":True}
    def close(self): pass
    def __enter__(self): return self.connect()
    def __exit__(self,*a): self.close()
@pytest.fixture
def mock_ssh_interface(): return MockSSH()
@pytest.fixture
def sample_host_config(): return {"host":"192.168.1.100","port":22,"username":"admin","key_path":"/key","variant":"rlc-pro"}


# --- Live target -------------------------------------------------------------
# Tests marked `live` run against a real SSH host named by environment:
#   SSH_TEST_HOST, SSH_TEST_PORT (default 22), SSH_TEST_USER, SSH_TEST_KEY
# Without a target they skip. With SSH_LIVE_REQUIRED=1 (CI) a missing or
# unreachable target is a failure, never a skip.
import os


def pytest_configure(config):
    config.addinivalue_line("markers", "live: needs a real SSH target (see SSH_TEST_* env vars)")


def _no_target(reason):
    if os.environ.get("SSH_LIVE_REQUIRED") == "1":
        pytest.fail(f"SSH_LIVE_REQUIRED=1 but {reason}", pytrace=False)
    pytest.skip(reason)


@pytest.fixture(scope="session")
def live_host_config():
    missing = [v for v in ("SSH_TEST_HOST", "SSH_TEST_USER", "SSH_TEST_KEY") if not os.environ.get(v)]
    if missing:
        _no_target("no live SSH target configured (" + ", ".join(missing) + " unset)")
    return {"host": os.environ["SSH_TEST_HOST"], "port": int(os.environ.get("SSH_TEST_PORT", "22")),
            "username": os.environ["SSH_TEST_USER"], "key_path": os.environ["SSH_TEST_KEY"]}


@pytest.fixture(scope="session")
def live_ssh(live_host_config):
    from ssh_interface import SSHInterface
    ssh = SSHInterface(live_host_config, retries=3, timeout=15)
    try:
        ssh.connect()
    except Exception as e:
        _no_target(f"cannot connect to {live_host_config['host']}:{live_host_config['port']} ({type(e).__name__}: {e})")
    yield ssh
    ssh.close()
