from dataclasses import dataclass, field
from enum import Enum, auto
from numpy.random import Generator
from numpy import random as rnd
from node import Node, StateCategory
from graph import create_graph_window
from policy import Policy


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



def simulate_episode(node: Node, policy: Policy, horizon: int = 5):
    """
    Simulate a single episode for the node using a base-stock policy.
    """
    incoming_orders = []  # list of tuples: (quantity, remaining_lead_time)

    for t in range(horizon):
        print(f"Time {t} | Current State: {node}")

        # Decide order quantity based on inventory + pending orders
        order_quantity = policy.decide_order_quantity(incoming_orders)
        print(f"Decided Order Quantity: {order_quantity}")

        # Place order with random lead time (1-3)
        lead_time = rnd.randint(1, 4)
        if order_quantity > 0:
            incoming_orders.append((order_quantity, lead_time))

        # Process incoming orders
        for i, (qty, time) in enumerate(incoming_orders):
            if time <= 0:
                node.inventory += qty
                incoming_orders[i] = (0, 0)  # mark as received
            else:
                incoming_orders[i] = (qty, time - 1)

        # Simulate stochastic demand
        demand = rnd.poisson(lam=5)
        sales = min(demand, node.inventory)
        node.inventory -= sales
        node.backorders = max(0, node.backorders + demand - sales)

        # Update Node state
        remaining_time = horizon - t - 1
        category = StateCategory.AWAIT_EVENT if remaining_time > 0 else StateCategory.FINAL
        node.set_state(
            inventory=node.inventory,
            backorders=node.backorders,
            remaining_time=remaining_time,
            category=category
        )

    print(f"Final State: {node}")




# Helper functions 

def get_random_id(rng: Generator, low: int = 1, high: int = 1000) -> int:
    return rng.integers(low=low, high=high)

def main() -> None:

    print("Node MDP State Management Example")
    # Example usage

    id_node = get_random_id(rnd.default_rng())

    node_1 = Node(
        id=id_node,
        name="Node_A",
        capacity=100,
        policy="FIFO",
        inventory=50,
        backorders=10,
        remaining_time=5,
        holding_cost=1.0
    )

    node_2 = Node(
        id=get_random_id(rnd.default_rng()),
        name="Node_B",
        capacity=150,
        policy="LIFO",
        inventory=80,
        backorders=5,
        remaining_time=5,
        holding_cost=1.5
    )

    node_3 = Node(
        id=get_random_id(rnd.default_rng()),
        name="Node_C",
        capacity=200,
        policy="Base-Stock",
        inventory=120,
        backorders=0,
        remaining_time=5,
        holding_cost=2.0
    )

    print(f"Initial Node State: {node_1}")
    print(f"Initial Node State: {node_2}")
    print(f"Initial Node State: {node_3}")

    nodes = [node_1, node_2, node_3]
    connections = [
        (nodes[0], nodes[1]),
        (nodes[1], nodes[2]),
    ]
    create_graph_window(nodes, connections, title="Supply Chain Network")


if __name__ == "__main__":
    main()
