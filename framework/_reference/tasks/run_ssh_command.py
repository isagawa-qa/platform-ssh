"""L3: Atomic SSH command."""
def run_ssh_command(ssh, cmd, expected_exit=0):
    r=ssh.execute(cmd); r["passed"]=r["exit_code"]==expected_exit; return r
