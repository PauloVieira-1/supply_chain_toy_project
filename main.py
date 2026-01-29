from dataclasses import dataclass, field
from enum import Enum, auto
from numpy.random import Generator
from numpy import random as rnd
from node import Node, StateCategory
from graph import create_graph_window


class StateCategory(Enum):
    AWAIT_EVENT = auto()
    AWAIT_ACTION = auto()
    FINAL = auto()

class State:
    """
    Represents the MDP state of a node in a supply chain simulation.
    """ 
    capacity: int
    inventory: int
    backorders: int
    remaining_time: int
    category: StateCategory


# Helper functions 

def get_random_id(rng: Generator, low: int = 1, high: int = 1000) -> int:
    return rng.integers(low=low, high=high)

def main() -> None:

    print("Node MDP State Management Example")
    # Example usage

    id_node = get_random_id(rnd.default_rng())

    node = Node(
        id=id_node,
        name="Node_A",
        capacity=100,
        policy="FIFO",
        inventory=50,
        backorders=10,
        remaining_time=5,
    )

    print(f"Initial State: {node}")

    # Update state
    node.set_state(
        inventory=60,
        backorders=5,
        remaining_time=4,
        category=StateCategory.AWAIT_ACTION,
    )

    print(f"Updated State: {node}")

    create_graph_window([node], title="Node Visualization")



if __name__ == "__main__":
    main()
