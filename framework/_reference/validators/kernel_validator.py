"""L2: Kernel Validator."""
class KernelValidator:
    def __init__(self,ssh): self.ssh=ssh
    def validate(self):
        v=self.ssh.execute("uname -r"); m=self.ssh.execute("lsmod | head -20")
        return [{"check":"kernel_version","passed":v["passed"],"evidence":v["stdout"]},{"check":"kernel_modules","passed":m["passed"],"evidence":m["stdout"]}]
