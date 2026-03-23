"""L1: SSH Interface."""
import time

class SSHInterface:
    def __init__(self, hc, retries=3, timeout=10):
        self.host=hc.get("host"); self.port=hc.get("port",22)
        self.username=hc.get("username"); self.key_path=hc.get("key_path")
        self.retries=retries; self.timeout=timeout; self.client=None
    def connect(self):
        import paramiko
        for i in range(self.retries):
            try:
                self.client=paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(self.host,port=self.port,username=self.username,key_filename=self.key_path,timeout=self.timeout)
                return self
            except Exception:
                if i==self.retries-1: raise
                time.sleep(2**i)
    def execute(self, cmd):
        if not self.client: raise RuntimeError("Not connected")
        _,o,e=self.client.exec_command(cmd,timeout=self.timeout)
        ec=o.channel.recv_exit_status()
        return {"command":cmd,"stdout":o.read().decode().strip(),"stderr":e.read().decode().strip(),"exit_code":ec,"passed":ec==0}
    def close(self):
        if self.client: self.client.close(); self.client=None
    def __enter__(self): return self.connect()
    def __exit__(self,*a): self.close()
