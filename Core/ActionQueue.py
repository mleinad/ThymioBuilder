
from collections import deque

class ActionQueue:
    """
    Simple behavior-planner that stores robot actions as a queue.
    Actions:
        F  -> forward
        B  -> backward
        TR -> turn right
        TL -> turn left
        PB -> push block (or custom)
    """

    def __init__(self):
        self.actions = deque()   # FIFO queue

    # ---- Add actions ----
    def add(self, action: str):
        """Append a single action string."""
        self.actions.append(action)

    def add_sequence(self, seq):
        """Append multiple actions."""
        for action in seq:
            self.actions.append(action)

    # ---- Query ----
    def has_next(self) -> bool:
        return len(self.actions) > 0

    def peek(self):
        """Return next action without removing it."""
        if not self.actions:
            return None
        return self.actions[0]

    # ---- Consume ----
    def next(self):
        """Pop and return next action (FIFO)."""
        if not self.actions:
            return None
        return self.actions.popleft()

    # ---- Reset ----
    def clear(self):
        self.actions.clear()

    # ---- Debug / Utility ----
    def print_queue(self):
        """Print the full queue without consuming it."""
        if not self.actions:
            print("[Empty Queue]")
        else:
            print(" -> ".join(self.actions))



    def __len__(self):
        return len(self.actions)
