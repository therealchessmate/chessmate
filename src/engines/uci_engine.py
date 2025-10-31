import subprocess, threading, queue, time, re, json
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Callable, Iterable, Union

class UCITimeout(Exception):
    pass

@dataclass(frozen=True)
class Score:
    kind: str   # "cp" or "mate"
    value: int  # centipawns or mate plies (signed)

class UCIEngine:
    """
    Thin UCI client with background reader and timeouts.
    Handles only engine I/O + standard UCI verbs.
    """

    def __init__(self, path: str, options: Optional[Dict[str, Union[str,int,bool]]] = None, read_buf: int = 1<<16):
        self.path = path
        self.proc: Optional[subprocess.Popen] = None
        self._q: "queue.Queue[str]" = queue.Queue(maxsize=read_buf)
        self._reader: Optional[threading.Thread] = None
        self._alive = False
        self.options = options or {}

    # ---- lifecycle ----
    def start(self) -> None:
        if self.proc: 
            return
        self.proc = subprocess.Popen(
            [self.path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True
        )
        self._alive = True
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

        # handshake
        self._send("uci")
        self._expect(lambda l: l.strip() == "uciok", timeout=5.0)
        for k, v in self.options.items():
            self.setoption(k, v)
        self.isready()

    def stop(self) -> None:
        if not self.proc: 
            return
        try:
            self._send("quit")
        except Exception:
            pass
        self._alive = False
        try:
            self.proc.terminate()
        except Exception:
            pass
        self.proc = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop()

    # ---- low-level I/O ----
    def _read_loop(self):
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            if not self._alive:
                break
            self._q.put(line.rstrip("\n"))
        self._alive = False

    def _send(self, cmd: str) -> None:
        if not self.proc or not self.proc.stdin:
            raise RuntimeError("Engine not started")
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def _expect(self, pred: Callable[[str], bool], timeout: float) -> List[str]:
        """Read until pred(line) is True or timeout. Returns captured lines."""
        end = time.time() + timeout
        buf: List[str] = []
        while time.time() < end:
            try:
                line = self._q.get(timeout=0.05)
            except queue.Empty:
                continue
            buf.append(line)
            if pred(line):
                return buf
        raise UCITimeout("Timeout waiting for engine output")

    def _read_until(self, stop_pred: Callable[[str], bool], timeout: float) -> List[str]:
        """Read until stop_pred(line) is True or timeout, accumulating all lines."""
        end = time.time() + timeout
        buf: List[str] = []
        while time.time() < end:
            try:
                line = self._q.get(timeout=0.05)
            except queue.Empty:
                continue
            buf.append(line)
            if stop_pred(line):
                return buf
        raise UCITimeout("Timeout while waiting for stop condition")

    # ---- UCI helpers ----
    def isready(self) -> None:
        self._send("isready")
        self._expect(lambda l: l.strip() == "readyok", timeout=5.0)

    def ucinewgame(self) -> None:
        self._send("ucinewgame")
        self.isready()

    def setoption(self, name: str, value: Union[str,int,bool]) -> None:
        if isinstance(value, bool):
            value = "true" if value else "false"
        self._send(f"setoption name {name} value {value}")

    def position_fen(self, fen: str, moves: Optional[List[str]] = None) -> None:
        if moves:
            self._send(f"position fen {fen} moves {' '.join(moves)}")
        else:
            self._send(f"position fen {fen}")

    def position_startpos(self, moves: Optional[List[str]] = None) -> None:
        if moves:
            self._send(f"position startpos moves {' '.join(moves)}")
        else:
            self._send("position startpos")

    # ---- Search commands ----
    def go_depth(self, depth: int, timeout: float = 30.0) -> Tuple[Score, List[str]]:
        """
        Search to an exact ply depth. Returns (Score, all_lines).
        Score is taken from the last 'info score ...' before 'bestmove'.
        """
        self._send(f"go depth {depth}")
        last_cp: Optional[int] = None
        last_mate: Optional[int] = None

        def stop_pred(line: str) -> bool:
            nonlocal last_cp, last_mate
            if " info " in line or line.startswith("info "):
                m = re.search(r"score\s+cp\s+(-?\d+)", line)
                if m: last_cp = int(m.group(1))
                m = re.search(r"score\s+mate\s+(-?\d+)", line)
                if m: last_mate = int(m.group(1))
            return line.startswith("bestmove ")

        lines = self._read_until(stop_pred, timeout=timeout)
        if last_mate is not None:
            return Score("mate", last_mate), lines
        if last_cp is None:
            # engines usually emit some score; default to 0 if not present
            return Score("cp", 0), lines
        return Score("cp", last_cp), lines

    def go_movetime(self, ms: int, timeout: float = 30.0) -> Tuple[Score, List[str]]:
        self._send(f"go movetime {ms}")
        # Reuse the same “read until bestmove” logic
        return self.go_depth(depth=1_000_000, timeout=timeout)  # depth is ignored by engine in movetime mode

    # ---- Optional custom hook (safe if engine unpatched) ----
    def eval_breakdown(self, timeout: float = 20.0) -> Optional[Dict]:
        """
        If your patched engine prints a line like:
          evalbreakdown {"mobility":12,"pawns":-3,"total":9}
        this returns that dict; otherwise returns None.
        """
        self._send("eval_breakdown")
        try:
            lines = self._expect(lambda l: l.startswith("evalbreakdown"), timeout=timeout)
        except UCITimeout:
            return None
        for l in reversed(lines):
            if l.startswith("evalbreakdown"):
                try:
                    return json.loads(l.split(" ", 1)[1])
                except Exception:
                    return None
        return None
