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
