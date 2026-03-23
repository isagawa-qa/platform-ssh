"""L5: Tests."""
import pytest
def test_connect(mock_ssh_interface): assert mock_ssh_interface.client is not None
def test_execute(mock_ssh_interface):
    r=mock_ssh_interface.execute("echo hi"); assert r["passed"]; assert r["stdout"]=="hello"
def test_package(mock_ssh_interface):
    from validators.package_validator import PackageValidator
    assert len(PackageValidator(mock_ssh_interface,["bash"]).validate())==1
def test_batch(mock_ssh_interface):
    from validators.package_validator import PackageValidator
    from roles.ssh_batch_executor import SSHBatchExecutor
    e=SSHBatchExecutor(mock_ssh_interface,[PackageValidator(mock_ssh_interface,["bash"])])
    e.execute_all(); assert e.get_results()["total"]>=1
