"""L2: Service Validator."""
class ServiceValidator:
    def __init__(self,ssh,svcs=None): self.ssh=ssh; self.expected=svcs or []
    def validate(self):
        return [{"check":f"service_{s}","passed":self.ssh.execute(f"systemctl is-active {s}")["stdout"].strip()=="active","evidence":self.ssh.execute(f"systemctl is-active {s}")["stdout"]} for s in self.expected]
