from dataclasses import dataclass
from enum import Enum, auto
from node import Node
import numpy as np


@dataclass
class BaseStockPolicy:
    """
    Base-stock (safety-stock) policy for a Node.
    Orders enough to reach a target inventory + safety stock.
    """
    node: Node
    target_inventory: int  # desired inventory level
    safety_stock: int      # extra buffer
    price_per_unit: float  # for profit evaluation

    def decide_order_quantity(self, pending_orders: list[tuple[int, int]]) -> int:
        """
        Decide order quantity based on current inventory + pending orders.
        """
        total_pending = sum(qty for qty, _ in pending_orders)
        base_stock_level = self.target_inventory + self.safety_stock
        order_quantity = max(0, base_stock_level - (self.node.inventory + total_pending))
        return min(order_quantity, self.node.capacity - self.node.inventory)

    def evaluate(self, state: Node, demand_lambda: float = 5.0) -> float:
        """
        Estimate expected profit for this policy in the given state.
        """
        # Simulate expected demand
        expected_demand = np.random.poisson(lam=demand_lambda)
        sales = min(state.inventory, expected_demand)
        revenue = sales * self.price_per_unit
        holding_cost = (state.inventory - sales) * state.h
        backorder_cost = state.backorders * state.h
        return revenue - holding_cost - backorder_cost


class FixedOrderPolicy:
    """
    Fixed order quantity policy for a Node.
    Always orders a fixed quantity each time.
    The order quantity is limited by available capacity.
    """
    node: Node
    order_quantity: int    # fixed order quantity
    price_per_unit: float  # for profit evaluation

    def decide_order_quantity(self, pending_orders: list[tuple[int, int]]) -> int:
        """
        Decide order quantity based on fixed amount.
        """
        available_capacity = self.node.capacity - self.node.inventory - sum(qty for qty, _ in pending_orders)
        return min(self.order_quantity, max(0, available_capacity))

    def evaluate(self, state: Node, demand_lambda: float = 5.0) -> float:
        """
        Estimate expected profit for this policy in the given state.
        """
        # Simulate expected demand
        expected_demand = np.random.poisson(lam=demand_lambda)
        sales = min(state.inventory, expected_demand)
        revenue = sales * self.price_per_unit
        holding_cost = (state.inventory - sales) * state.h
        backorder_cost = state.backorders * state.h
        return revenue - holding_cost - backorder_cost
    
class MinMaxPolicy:
    """
    Min-max inventory policy for a Node.
    Orders up to a maximum level when inventory falls below a minimum threshold.
    """
    node: Node
    min_inventory: int     # minimum inventory threshold
    max_inventory: int     # maximum inventory level
    price_per_unit: float  # for profit evaluation

    def decide_order_quantity(self, pending_orders: list[tuple[int, int]]) -> int:
        """
        Decide order quantity based on min-max levels.
        """
        total_pending = sum(qty for qty, _ in pending_orders)
        inventory_position = self.node.inventory + total_pending

        if inventory_position >= self.max_inventory:
            return 0

        if inventory_position < self.min_inventory:
            order_quantity = self.max_inventory - inventory_position
            return min(order_quantity, self.node.capacity - self.node.inventory - total_pending)            
            
        return 0
    
    def evaluate(self, state: Node, demand_lambda: float = 5.0) -> float:
        """
        Estimate expected profit for this policy in the given state.
        """
        # Simulate expected demand
        expected_demand = np.random.poisson(lam=demand_lambda)
        sales = min(state.inventory, expected_demand)
        revenue = sales * self.price_per_unit
        holding_cost = (state.inventory - sales) * state.h
        backorder_cost = state.backorders * state.h
        return revenue - holding_cost - backorder_cost
