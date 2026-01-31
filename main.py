from dataclasses import dataclass, field
from enum import Enum, auto
from numpy.random import Generator
from numpy import random as rnd
from node import Node, StateCategory
from graph import create_graph_window
from policy import Policy
from typing import List
import numpy as np


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



def simulate_episode(
    nodes: list,
    horizon: int = 5,
    assembly_requirement: list[int] = None  # e.g., [1,2,3] for Node 4
) -> None:
    """
    Simulate a single episode with subassembly support.

    - Raw Material nodes have their own stochastic demand and base-stock replenishment.
    - SubAssembly node consumes parts from raw material nodes according to assembly_requirement.
    """

    if assembly_requirement is None:
        assembly_requirement = [1, 1, 1]

    sub_node = next((n for n in nodes if n.type == "SubAssembly"), None)
    raw_nodes = [n for n in nodes if n.type == "Raw Material"]

    node_orders = {node.id: [] for node in nodes}  

    for t in range(horizon):
        print(f"\n--- Time Step {t} ---")

        # Process subassembly demand first
        if sub_node:
            # Generate stochastic demand for final product
            final_demand = np.random.poisson(lam=5)

            part_demand = [final_demand * qty for qty in assembly_requirement]
            received_parts = []

            for i, node in enumerate(raw_nodes):
                requested = part_demand[i]
                actual_supplied = min(requested, node.inventory)
                node.inventory -= actual_supplied
                node.backorders += requested - actual_supplied
                received_parts.append(actual_supplied)

            # Determine how many full assemblies can be made
            assemblies_possible = min(
                received_parts[i] // assembly_requirement[i] for i in range(len(raw_nodes))
            )

            sub_node.inventory += assemblies_possible
            sub_node.backorders += max(0, final_demand - assemblies_possible)

            print(f"\nNode {sub_node.name} at Time {t} (SubAssembly)")
            print(f"Final Demand: {final_demand}")
            print(f"Assemblies Possible: {assemblies_possible}")
            print(f"Inventory: {sub_node.inventory}, Backorders: {sub_node.backorders}")

        # Process raw material nodes 
        for node in raw_nodes:
            print(f"\nNode {node.name} at Time {t} (Raw Material)")
            print(f"Time {t} | Current State: {node}")

            # Decide order quantity using base-stock policy
            policy = Policy(
                node=node,
                target_inventory=50,
                safety_stock=10,
                price_per_unit=20.0
            )

            pending_orders = node_orders[node.id]
            order_quantity = policy.decide_order_quantity(pending_orders)
            print(f"Decided Order Quantity: {order_quantity}")

            # Place order with random lead time (1-3)
            if order_quantity > 0:
                lead_time = np.random.randint(1, 4)
                pending_orders.append((order_quantity, lead_time))

            # Process incoming orders
            updated_orders = []
            for qty, time_left in pending_orders:
                if time_left <= 0:
                    node.inventory += qty
                else:
                    updated_orders.append((qty, time_left - 1))
            node_orders[node.id] = updated_orders

            # External stochastic demand
            demand = np.random.poisson(lam=5)

            # Fulfill existing backorders first
            fulfill_from_inventory = min(node.inventory, node.backorders)
            node.inventory -= fulfill_from_inventory
            node.backorders -= fulfill_from_inventory

            # Fulfill current demand
            if demand <= node.inventory:
                node.inventory -= demand
            else:
                node.backorders += demand - node.inventory
                node.inventory = 0

            # Update Node state
            remaining_time = horizon - t - 1
            category = StateCategory.AWAIT_EVENT if remaining_time > 0 else StateCategory.FINAL
            node.set_state(
                inventory=node.inventory,
                backorders=node.backorders,
                remaining_time=remaining_time,
                category=category
            )

            print(f"After Demand {demand} | Updated State: {node}")

    print("Episode simulation completed.")



# Helper functions 

def get_random_id(rng: Generator, low: int = 1, high: int = 1000) -> int:
    return rng.integers(low=low, high=high)

def main() -> None:

    print("Node MDP State Management Example")

    id_node = get_random_id(rnd.default_rng())

    node_1 = Node(
        id=id_node,
        name="Node_A",
        capacity=100,
        type="Raw Material",
        inventory=50,
        backorders=10,
        remaining_time=5,
        holding_cost=1.0,
        upstream_ids=[],
        downstream_ids=[3]
    )

    node_2 = Node(
        id=get_random_id(rnd.default_rng()),
        name="Node_B",
        capacity=150,
        type="Raw Material",
        inventory=80,
        backorders=5,
        remaining_time=5,
        holding_cost=1.5,
        upstream_ids=[],
        downstream_ids=[3]
    )

    node_3 = Node(
        id=get_random_id(rnd.default_rng()),
        name="Node_C",
        capacity=200,
        type="Raw Material",
        inventory=120,
        backorders=0,
        remaining_time=5,
        holding_cost=2.0,
        upstream_ids=[],
        downstream_ids=[3]
    )

    node_4 = Node(
        id=get_random_id(rnd.default_rng()),
        name="Node_D",
        capacity=250,
        type="SubAssembly",
        inventory=150,
        backorders=20,
        remaining_time=5,
        holding_cost=2.5,
        upstream_ids=[1,2,3],
        downstream_ids=[],
    )

    print(f"Initial Node State: {node_1}")
    print(f"Initial Node State: {node_2}")
    print(f"Initial Node State: {node_3}")
    print(f"Initial Node State: {node_4}")

    nodes = [node_1, node_2, node_3, node_4]

    connections = [
        (nodes[0], nodes[3]),
        (nodes[1], nodes[3]),
        (nodes[2], nodes[3]),
        (nodes[3], nodes[0]),
    ]

    requirement = [2, 1, 3]  


    create_graph_window(nodes, connections, title="Supply Chain Network")

    simulate_episode(nodes, horizon=5, assembly_requirement=requirement)


if __name__ == "__main__":
    main()
