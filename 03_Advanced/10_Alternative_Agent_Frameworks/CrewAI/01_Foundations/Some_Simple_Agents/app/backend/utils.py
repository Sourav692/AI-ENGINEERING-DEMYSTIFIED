import io
import sys
import queue
import asyncio


def safe_sse(text: str) -> str:
    """Escape newlines so they fit in a single SSE data line."""
    return str(text).replace("\r", "").replace("\n", "\\n")


class QueueWriter(io.TextIOBase):
    """Redirect stdout/stderr into a queue for SSE streaming."""

    def __init__(self, q: queue.Queue):
        self._q = q

    def write(self, s: str) -> int:
        if s and s.strip():
            self._q.put(s.strip())
        return len(s)

    def flush(self):
        pass


def capture_to_queue(q: queue.Queue):
    """Context manager that redirects stdout+stderr into q."""

    class _Ctx:
        def __enter__(self):
            self._old_out = sys.stdout
            self._old_err = sys.stderr
            writer = QueueWriter(q)
            sys.stdout = writer
            sys.stderr = writer

        def __exit__(self, *_):
            sys.stdout = self._old_out
            sys.stderr = self._old_err

    return _Ctx()


async def sse_stream(q: queue.Queue):
    """Async generator that drains a sync queue and yields SSE lines.

    Puts items via run_in_executor so the event loop stays unblocked.
    Terminates when '__DONE__' sentinel is found; next item is the final result.
    """
    loop = asyncio.get_event_loop()
    while True:
        item = await loop.run_in_executor(None, q.get)
        if item == "__DONE__":
            final = await loop.run_in_executor(None, q.get)
            yield f"data: [FINAL] {safe_sse(final)}\n\n"
            break
        yield f"data: {safe_sse(item)}\n\n"


SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}
