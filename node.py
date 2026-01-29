from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from numpy.random import Generator

class StateCategory(Enum):
    AWAIT_EVENT = auto()
    AWAIT_ACTION = auto()
    FINAL = auto()


@dataclass
class Node:

    # static configuration
    # ------------
    id: int = field(init=True, repr=True)
    name: str = field(init=True, repr=True)
    capacity: int = field(init=True, repr=True)
    policy: str = field(init=True, repr=True)
    # ------------

    # Dynamic state 
    # ------------
    inventory: int
    backorders: int
    remaining_time: int
    category: StateCategory = StateCategory.AWAIT_EVENT
    # ------------
    
    # Methods
    # ------------
    def __post_init__(self) -> None:
        """
        Validate initial state.
        """
        assert 0 <= self.inventory <= self.capacity
        assert self.backorders >= 0
        assert self.remaining_time >= 0

    # Prevent modification of static fields
    def __setattr__(self, name, value):
        if hasattr(self, name) and name in ("id", "capacity", "policy"):
            raise AttributeError(f"{name} is read-only and cannot be modified after initialization")
        super().__setattr__(name, value)

    def set_state(
        self,
        inventory: int,
        backorders: int,
        remaining_time: int,
        category: StateCategory,
    ) -> None:
        """
        Update the node MDP state.
        """
        assert 0 <= inventory <= self.capacity
        assert backorders >= 0
        assert remaining_time >= 0

        self.inventory = inventory
        self.backorders = backorders
        self.remaining_time = remaining_time
        self.category = category

    # Event update (stochastic)
    # -------------------------------
    def modify_state_with_event(self, rng: Generator, demand: Optional[int] = None) -> None:
        """
        Process an exogenous event (e.g., demand arrival, replenishment).
        Moves node from AWAIT_EVENT -> AWAIT_ACTION.
        """
        assert self.category == StateCategory.AWAIT_EVENT, "Not expecting an event right now."

        if demand is None:
            demand = rng.integers(low=0, high=10)  

        # Update inventory and backorders
        fulfilled = min(demand, self.inventory)
        self.inventory -= fulfilled
        self.backorders += demand - fulfilled

        # Advance time
        self.remaining_time -= 1

        # Move to action state or final
        if self.remaining_time <= 0:
            self.category = StateCategory.FINAL
        else:
            self.category = StateCategory.AWAIT_ACTION


    # Action update (deterministic)
    # -------------------------------
    def modify_state_with_action(self, action: int) -> float:
        """
        Apply an action (e.g., place order, ship inventory).
        Returns cost or negative reward.
        Moves node from AWAIT_ACTION -> AWAIT_EVENT or FINAL.
        """
        assert self.category == StateCategory.AWAIT_ACTION, "Not expecting an action right now."
        assert self.remaining_time > 0, "Simulation already finished."

        cost = 0.0

        if action > 0:
            order_qty = min(action, self.capacity - self.inventory)
            self.inventory += order_qty
            cost += 1.0 * order_qty 

        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.category = StateCategory.FINAL
        else:
            self.category = StateCategory.AWAIT_EVENT

        return cost


