from node import Node
import tkinter as tk
from random import randint
from typing import List
from numpy.random import default_rng



class NodeGUI:
    """
    Visual representation of a Node for a supply chain simulation.
    Node is drawn as a circle with label; supports drag-and-drop.
    """
    def __init__(self, canvas: tk.Canvas, node, x: int, y: int):
        self.node = node
        self.canvas = canvas
        self.radius = 30

        # Draw circle representing node
        self.oval_id = canvas.create_oval(
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius,
            fill="skyblue"
        )

        # Draw text label with node name
        self.text_id = canvas.create_text(x, y, text=f"{node.name}")

        # Bind mouse drag events
        self.canvas.tag_bind(self.oval_id, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.text_id, "<B1-Motion>", self.drag)

        # Bind click to show node details
        self.canvas.tag_bind(self.oval_id, "<Button-1>", self.show_info)
        self.canvas.tag_bind(self.text_id, "<Button-1>", self.show_info)

    def drag(self, event):
        x, y = event.x, event.y
        # Move circle and text together
        self.canvas.coords(
            self.oval_id,
            x - self.radius, y - self.radius,
            x + self.radius, y + self.radius
        )
        self.canvas.coords(self.text_id, x, y)

    def show_info(self, event):
        print(f"Node {self.node.id}: inventory={self.node.inventory}, "
              f"backorders={self.node.backorders}, remaining_time={self.node.remaining_time}")

def create_graph_window(nodes: List, title: str = "Supply Chain Nodes"):
    """
    Create a tkinter window and visualize nodes as draggable circles.
    Args:
        nodes: List of Node objects
        title: Window title
    """
    root = tk.Tk()
    root.title(title)
    canvas = tk.Canvas(root, width=600, height=600, bg="white")
    canvas.pack()

    # Random initial positions
    node_guis = []
    for node in nodes:
        x, y = randint(50, 550), randint(50, 550)
        gui_node = NodeGUI(canvas, node, x, y)
        node_guis.append(gui_node)

    root.mainloop()
