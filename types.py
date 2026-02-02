from dataclasses import dataclass
from enum import Enum, auto


class StateCategory(Enum):
    AWAIT_EVENT = auto()
    AWAIT_ACTION = auto()
    FINAL = auto()

class State:
    capacity: int
    inventory: int
    backorders: int
    remaining_time: int
    category: StateCategory

class PolicyType(Enum):
    BASE_STOCK = auto()
    FIXED_ORDER = auto()
    MIN_MAX = auto()
