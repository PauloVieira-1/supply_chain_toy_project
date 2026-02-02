# policy.py
from dataclasses import dataclass, field
from node import Node
import numpy as np
from typing import List, Tuple


@dataclass
class BasePolicy:
    """
    Abstract base class for inventory policies.
    All policies should inherit from this.
    """
    node: Node

    def decide_order_quantity(self, pending_orders: List[Tuple[int, int]]) -> int:
        raise NotImplementedError

    def evaluate(self, state: Node, demand_lambda: float = 5.0) -> float:
        raise NotImplementedError

    def set_parameters(self, **kwargs):
        raise NotImplementedError


@dataclass
class BaseStockPolicy(BasePolicy):
    """
    Base-stock policy with safety stock.
    Orders enough to reach target inventory + safety stock.
    """
    target_inventory: int = 50
    safety_stock: int = 10
    price_per_unit: float = 20.0

    def set_parameters(self, target_inventory: int = None, safety_stock: int = None, price_per_unit: float = None):
        if target_inventory is not None:
            self.target_inventory = target_inventory
        if safety_stock is not None:
            self.safety_stock = safety_stock
        if price_per_unit is not None:
            self.price_per_unit = price_per_unit

    def decide_order_quantity(self, pending_orders: List[Tuple[int, int]]) -> int:
        total_pending = sum(qty for qty, _ in pending_orders)
        base_stock_level = self.target_inventory + self.safety_stock
        order_quantity = max(0, base_stock_level - (self.node.inventory + total_pending))
        return min(order_quantity, self.node.capacity - self.node.inventory)

    def evaluate(self, state: Node, demand_lambda: float = 5.0) -> float:
        expected_demand = np.random.poisson(lam=demand_lambda)
        sales = min(state.inventory, expected_demand)
        revenue = sales * self.price_per_unit
        holding_cost = (state.inventory - sales) * state.h
        backorder_cost = state.backorders * state.h
        return revenue - holding_cost - backorder_cost


@dataclass
class MinMaxPolicy(BasePolicy):
    """
    Min-max inventory policy.
    Orders up to max_inventory when below min_inventory.
    """
    min_inventory: int = 20
    max_inventory: int = 80
    price_per_unit: float = 20.0

    def set_parameters(self, min_inventory: int = None, max_inventory: int = None, price_per_unit: float = None):
        if min_inventory is not None:
            self.min_inventory = min_inventory
        if max_inventory is not None:
            self.max_inventory = max_inventory
        if price_per_unit is not None:
            self.price_per_unit = price_per_unit

    def decide_order_quantity(self, pending_orders: List[Tuple[int, int]]) -> int:
        total_pending = sum(qty for qty, _ in pending_orders)
        inventory_position = self.node.inventory + total_pending

        if inventory_position >= self.max_inventory:
            return 0
        if inventory_position < self.min_inventory:
            order_quantity = self.max_inventory - inventory_position
            return min(order_quantity, self.node.capacity - self.node.inventory - total_pending)
        return 0

    def evaluate(self, state: Node, demand_lambda: float = 5.0) -> float:
        expected_demand = np.random.poisson(lam=demand_lambda)
        sales = min(state.inventory, expected_demand)
        revenue = sales * self.price_per_unit
        holding_cost = (state.inventory - sales) * state.h
        backorder_cost = state.backorders * state.h
        return revenue - holding_cost - backorder_cost


@dataclass
class FixedOrderPolicy(BasePolicy):
    """
    Fixed order quantity policy.
    Always orders a fixed quantity up to available capacity.
    """
    order_quantity: int = 30
    price_per_unit: float = 20.0

    def set_parameters(self, order_quantity: int = None, price_per_unit: float = None):
        if order_quantity is not None:
            self.order_quantity = order_quantity
        if price_per_unit is not None:
            self.price_per_unit = price_per_unit

    def decide_order_quantity(self, pending_orders: List[Tuple[int, int]]) -> int:
        inventory_position = self.node.inventory + sum(qty for qty, _ in pending_orders)
        available_capacity = self.node.capacity - inventory_position
        return min(self.order_quantity, max(0, available_capacity))

    def evaluate(self, state: Node, demand_lambda: float = 5.0) -> float:
        expected_demand = np.random.poisson(lam=demand_lambda)
        sales = min(state.inventory, expected_demand)
        revenue = sales * self.price_per_unit
        holding_cost = (state.inventory - sales) * state.h
        backorder_cost = state.backorders * state.h
        return revenue - holding_cost - backorder_cost
