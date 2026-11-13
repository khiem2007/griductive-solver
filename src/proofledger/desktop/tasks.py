import multiprocessing as mp
from dataclasses import dataclass

from proofledger.contracts.messages import PublicSnapshot
from proofledger.reasoning.inference import Analysis, analyze


@dataclass(frozen=True)
class WorkerFailure:
    message: str


def _compute(sender, snapshot: PublicSnapshot, pure: bool):
    """Analyze one public snapshot in a child process and serialize its outcome."""
    try:
        sender.send(analyze(snapshot, pure))
    except Exception as exc:
        sender.send(WorkerFailure(f"{type(exc).__name__}: {exc}"))
    finally:
        sender.close()


class ReasoningTask:
    """At most one isolated process, fed only an immutable public snapshot."""

    def __init__(self):
        """Create a spawn context and an idle worker lifecycle."""
        self._context = mp.get_context("spawn")
        self._process = None
        self._receiver = None

    @property
    def busy(self) -> bool:
        """Report whether an analysis process is currently owned by this task."""
        return self._process is not None

    def start(self, snapshot: PublicSnapshot, pure: bool = True):
        """Cancel stale work and start analysis of an immutable public snapshot."""
        self.cancel()
        self._receiver, sender = self._context.Pipe(duplex=False)
        self._process = self._context.Process(target=_compute, args=(sender, snapshot, pure), daemon=True)
        try:
            self._process.start()
        except Exception:
            self.cancel()
            raise
        finally:
            sender.close()

    def poll(self) -> Analysis | WorkerFailure | None:
        """Return a completed result or failure without blocking the UI thread."""
        if self._process is None:
            return None
        if self._receiver.poll():
            try:
                result = self._receiver.recv()
            except (EOFError, OSError) as exc:
                result = WorkerFailure(f"Analysis process ended without a result: {exc}")
            self.cancel()
            return result
        if not self._process.is_alive():
            self.cancel()
            return WorkerFailure("Analysis process exited unexpectedly; no verdict was inferred")
        return None

    def cancel(self):
        """Terminate and release any active analysis process and pipe."""
        if self._process is not None:
            if self._process.pid is not None:
                if self._process.is_alive():
                    self._process.terminate()
                self._process.join(timeout=1)
                self._process.close()
            self._process = None
        if self._receiver is not None:
            self._receiver.close()
            self._receiver = None
