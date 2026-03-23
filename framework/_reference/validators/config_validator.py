"""L2: Config Validator."""
import os as _os
class ConfigValidator:
    def __init__(self,ssh,checks=None): self.ssh=ssh; self.checks=checks or []
    def validate(self):
        results=[]
        for c in self.checks:
            r=self.ssh.execute("grep -q '"+c["pattern"]+"' "+c["file"])
            results.append({"check":"config_"+_os.path.basename(c["file"]),"passed":r["passed"],"evidence":c["pattern"]+" in "+c["file"]})
        return results
