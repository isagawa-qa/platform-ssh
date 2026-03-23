"""L2: Package Validator."""
class PackageValidator:
    def __init__(self,ssh,pkgs=None): self.ssh=ssh; self.expected=pkgs or []
    def validate(self):
        return [{"check":f"package_{p}","passed":self.ssh.execute(f"rpm -q {p}")["passed"],"evidence":self.ssh.execute(f"rpm -q {p}")["stdout"]} for p in self.expected]
