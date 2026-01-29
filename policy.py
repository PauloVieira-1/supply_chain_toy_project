from dataclasses import dataclass
from node import Node
import numpy as np


@dataclass
class Policy:
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
