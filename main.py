from dataclasses import dataclass, field
from enum import Enum, auto
from numpy.random import Generator
from numpy import random as rnd
from node import Node, StateCategory
from graph import create_graph_window
from policy import BaseStockPolicy, FixedOrderPolicy, MinMaxPolicy
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
        # Step 1) Orders arrive (lead time advances ONCE per period)
        # =========================================================
        for node in nodes:
            arrived, updated_orders = advance_time(node_orders[node.id])
            node.inventory += arrived
            node_orders[node.id] = updated_orders

        # =========================================================
        # Step 2) Subassembly demand and production
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

            fulfilled = min(sub_node.backorders, assemblies_possible)
            sub_node.backorders -= fulfilled
            sub_node.inventory += assemblies_possible - fulfilled


            print(f"\nSubAssembly {sub_node.name}")
            print(f"Final demand: {final_demand}")
            print(f"Assemblies produced: {assemblies_possible}")
            print(f"Inventory: {sub_node.inventory}, Backorders: {sub_node.backorders}")

        # =========================================================
        # Step 3) Raw material demand, ordering, and state update
        # ========================================================
        for i, raw_node in enumerate(raw_nodes):
            print(f"\nNode {raw_node.name} (Raw Material)")
            print(f"Before demand | Inventory: {raw_node.inventory}, Backorders: {raw_node.backorders}")

            # Demand comes from subassembly(s)
            demand_from_sub = final_demand * assembly_requirement[i]

            # Optional: add external demand
            external_demand = np.random.poisson(lam=2)  # adjust or remove if not needed
            total_demand = demand_from_sub + external_demand

            # Fulfill backorders first
            fulfill = min(raw_node.inventory, raw_node.backorders)
            raw_node.inventory -= fulfill
            raw_node.backorders -= fulfill

            # Fulfill new demand
            if total_demand <= raw_node.inventory:
                raw_node.inventory -= total_demand
            else:
                raw_node.backorders += total_demand - raw_node.inventory
                raw_node.inventory = 0


            print(f"Total demand: {total_demand}")
            print(f"After demand | Inventory: {raw_node.inventory}, Backorders: {raw_node.backorders}")

            # Ordering decision (uses inventory position)
            
            pending_orders = node_orders[raw_node.id]
            order_quantity = raw_node.policy.decide_order_quantity(pending_orders)

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

            raw_node.set_state(
                inventory=raw_node.inventory,
                backorders=raw_node.backorders,
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

    node_1 = Node(
        id=get_random_id(rnd.default_rng()),
        name="Node_A",
        capacity=100,
        type="Raw Material",
        inventory=50,
        backorders=10,
        remaining_time=5,
        holding_cost=1.0,
        policy=None,
        upstream_ids=[],
        downstream_ids=[3]
    )

    node_1.policy = BaseStockPolicy(node=node_1)
    node_1.policy.set_parameters(
        target_inventory=60,
        safety_stock=15,
        price_per_unit=22.0
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
        policy=None,
        upstream_ids=[],
        downstream_ids=[3]
    )

    node_2.policy = MinMaxPolicy(node=node_2)
    node_2.policy.set_parameters(
        min_inventory=20,
        max_inventory=80,
        price_per_unit=18.0
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
        policy=None,
        upstream_ids=[],
        downstream_ids=[3]
    )

    node_3.policy = FixedOrderPolicy(node=node_3)
    node_3.policy.set_parameters(
        order_quantity=30,
        price_per_unit=25.0
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
        policy=None,
        upstream_ids=[1,2,3],
        downstream_ids=[],
    )

    node_4.policy = BaseStockPolicy(node=node_4)
    node_4.policy.set_parameters(
        target_inventory=100,
        safety_stock=20,
        price_per_unit=30.0
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
