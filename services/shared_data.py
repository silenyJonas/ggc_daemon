# services/shared_data.py
import queue
import time
from dataclasses import dataclass

# Globální fronta zpráv
message_queue = queue.Queue()

@dataclass
class LogMessage:
    """Datová třída pro ukládání logovacích zpráv."""
    time: float
    status: str
    module: str
    message: str