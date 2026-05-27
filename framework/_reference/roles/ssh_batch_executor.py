"""L4: Batch executor."""
class SSHBatchExecutor:
    def __init__(self, ssh, validators=None):
        self.ssh = ssh
        self.validators = validators or []
        self.results = []

    def execute_all(self):
        for v in self.validators:
            try:
                self.results.extend(v.validate())
            except Exception as e:
                self.results.append({
                    "check": type(v).__name__,
                    "passed": False,
                    "evidence": str(e)
                })
        return self.results

    def get_results(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = sum(1 for r in self.results if not r["passed"])

        # Build by_framework grouping from enhanced results
        by_framework = {}
        for r in self.results:
            fw = r.get("framework")
            if fw:
                if fw not in by_framework:
                    by_framework[fw] = {"total": 0, "passed": 0, "failed": 0}
                by_framework[fw]["total"] += 1
                if r["passed"]:
                    by_framework[fw]["passed"] += 1
                else:
                    by_framework[fw]["failed"] += 1

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "by_framework": by_framework,
            "details": self.results
        }
