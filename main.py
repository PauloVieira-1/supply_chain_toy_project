from dataclasses import dataclass, field
from enum import Enum, auto
from numpy.random import Generator
from numpy import random as rnd
from node import Node, StateCategory
from graph import create_graph_window
from policy import BaseStockPolicy
from typing import List
import numpy as np


# Helper function to simulate an episode

def advance_time(pending_orders):
    arrived = 0
    new_pending = []

    for qty, lt in pending_orders:
        if lt <= 1:
            arrived += qty
        else:
            new_pending.append((qty, lt - 1))

    return arrived, new_pending


def simulate_episode(
    nodes: list,
    horizon: int = 5,
    assembly_requirement: list[int] = None
) -> None:

    if assembly_requirement is None:
        assembly_requirement = [1, 1, 1]

    sub_node = next((n for n in nodes if n.type == "SubAssembly"), None)
    raw_nodes = [n for n in nodes if n.type == "Raw Material"]

    # Pending orders per node: (quantity, remaining_lead_time)
    node_orders = {node.id: [] for node in nodes}

    print("\n=====================================")
    print("Starting Episode Simulation")
    print("=====================================\n")

    for t in range(horizon):
        print(f"\n--- Time Step {t} ---")
        print("----------------------")

        # =========================================================
        # 1. Orders arrive (lead time advances ONCE per period)
        # =========================================================
        for node in nodes:
            arrived, updated_orders = advance_time(node_orders[node.id])
            node.inventory += arrived
            node_orders[node.id] = updated_orders

        # =========================================================
        # 2. Subassembly demand and production
        # =========================================================
        if sub_node:
            final_demand = np.random.poisson(lam=5)

            part_demand = [
                final_demand * qty for qty in assembly_requirement
            ]

            received_parts = []

            for i, raw_node in enumerate(raw_nodes): # assumes backordering is allowed, no partial fulfillment or allocation
                requested = part_demand[i]
                supplied = min(requested, raw_node.inventory)
                raw_node.inventory -= supplied
                raw_node.backorders += requested - supplied
                received_parts.append(supplied)

            assemblies_possible = min(
                received_parts[i] // assembly_requirement[i]
                for i in range(len(raw_nodes))
            ) # No lead time because this is not too relevant for this example. Assumes immediate assembly.

            sub_node.inventory += assemblies_possible
            sub_node.backorders += max(0, final_demand - assemblies_possible)

            print(f"\nSubAssembly {sub_node.name}")
            print(f"Final demand: {final_demand}")
            print(f"Assemblies produced: {assemblies_possible}")
            print(f"Inventory: {sub_node.inventory}, Backorders: {sub_node.backorders}")

        # =========================================================
        # 3. Raw material demand, ordering, and state update
        # =========================================================
        for node in raw_nodes:
            print(f"\nNode {node.name} (Raw Material)")
            print(f"Before demand | Inventory: {node.inventory}, Backorders: {node.backorders}")

            # External stochastic demand
            demand = np.random.poisson(lam=5)

            # Fulfill backorders
            fulfill = min(node.inventory, node.backorders)
            node.inventory -= fulfill
            node.backorders -= fulfill

            # Fulfill current demand
            if demand <= node.inventory:
                node.inventory -= demand
            else:
                node.backorders += demand - node.inventory
                node.inventory = 0

            print(f"Demand: {demand}")
            print(f"After demand | Inventory: {node.inventory}, Backorders: {node.backorders}")

            # Ordering decision (uses inventory position)
            policy = BaseStockPolicy(
                node=node,
                target_inventory=50,
                safety_stock=10,
                price_per_unit=20.0
            )

            pending_orders = node_orders[node.id]
            order_quantity = policy.decide_order_quantity(pending_orders)

            print(f"Order placed: {order_quantity}")

            if order_quantity > 0:
                lead_time = np.random.randint(1, 4)
                pending_orders.append((order_quantity, lead_time))

            # Update node state
            remaining_time = horizon - t - 1
            category = (
                StateCategory.AWAIT_EVENT
                if remaining_time > 0
                else StateCategory.FINAL
            )

            node.set_state(
                inventory=node.inventory,
                backorders=node.backorders,
                remaining_time=remaining_time,
                category=category
            )

        print("\n----------------------")

    print("\n=====================================")
    print("Episode simulation completed.")
    print("=====================================")




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
