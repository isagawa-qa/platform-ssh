"""L4: Batch executor."""
class SSHBatchExecutor:
    def __init__(self,ssh,validators=None): self.ssh=ssh; self.validators=validators or []; self.results=[]
    def execute_all(self):
        for v in self.validators:
            try: self.results.extend(v.validate())
            except Exception as e: self.results.append({"check":type(v).__name__,"passed":False,"evidence":str(e)})
        return self.results
    def get_results(self):
        return {"total":len(self.results),"passed":sum(1 for r in self.results if r["passed"]),"failed":sum(1 for r in self.results if not r["passed"]),"details":self.results}
