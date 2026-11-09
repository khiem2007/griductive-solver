from proofledger.contracts.values import Outcome
from proofledger.investigation.coordinator import Investigation


class AutoPilot:
    """Clock-driven policy with no GUI dependency or speculative move queue."""

    def __init__(self, interval: float = 0.65):
        self.interval = interval
        self.running = False
        self.due = 0.0
        self.reason = ""

    def stop(self, reason: str = "Paused"):
        self.running = False
        self.reason = reason

    def start(self, investigation: Investigation, now: float) -> bool:
        if investigation.public.solved:
            self.stop("Every identity is resolved")
            return False
        if investigation.analysis is None:
            self.stop("Wait for evidence analysis")
            return False
        if investigation.analysis.inconsistent:
            self.stop("Evidence conflicts; automation cannot proceed")
            return False
        self.running, self.due, self.reason = True, now, "Running"
        return True

    def tick(self, investigation: Investigation, now: float) -> Outcome | None:
        if not self.running or now < self.due or investigation.analysis is None:
            return None
        move = investigation.hint()
        if move is None:
            self.stop("No further verdict follows from the available evidence")
            return None
        result = investigation.submit(*move)
        self.due = now + self.interval
        if result != Outcome.ACCEPTED:
            self.stop(f"Deduction stopped: {result.value}")
        elif investigation.public.solved:
            self.stop("Every identity is resolved")
        return result
