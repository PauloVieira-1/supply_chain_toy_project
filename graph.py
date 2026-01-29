import networkx as nx
import plotly.graph_objects as go
from typing import List, Tuple
import math


# =====================================================
# Helper: shorten edge so it touches node circle edge
# =====================================================
def shorten_edge(x0, y0, x1, y1, r):
    """
    Shorten a line so it starts/ends at the circle boundary.
    r = node radius (same for all nodes)
    """
    dx = x1 - x0
    dy = y1 - y0
    dist = math.sqrt(dx**2 + dy**2)

    if dist == 0:
        return x0, y0, x1, y1

    ux = dx / dist
    uy = dy / dist

    # Move start and end inward by radius
    return (
        x0 + ux * r,
        y0 + uy * r,
        x1 - ux * r,
        y1 - uy * r,
    )


# =====================================================
# Main visualization function
# =====================================================
def create_graph_window(
    nodes: List,
    connections: List[Tuple],
    title: str = "Supply Chain Network",
):
    """
    Interactive supply chain graph using NetworkX + Plotly.
    Arrows connect to node edges (not centers) and render behind nodes.
    """

    NODE_RADIUS = 0.06  # controls visual spacing / arrow offset

    G = nx.DiGraph()

    # Add nodes with metadata
    for node in nodes:
        G.add_node(
            node.id,
            label=node.name,
            inventory=node.inventory,
            backorders=node.backorders,
            remaining_time=node.remaining_time,
        )

    # Add directed edges
    for src, tgt in connections:
        G.add_edge(src.id, tgt.id)

    # Layout
    pos = nx.spring_layout(G, seed=42)

    # -----------------------
    # Build edge traces
    # -----------------------
    edge_x, edge_y = [], []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        xs, ys, xe, ye = shorten_edge(x0, y0, x1, y1, NODE_RADIUS)

        edge_x += [xs, xe, None]
        edge_y += [ys, ye, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=2, color="black"),
        hoverinfo="none",
    )

    # -----------------------
    # Build node traces (on top)
    # -----------------------
    node_x, node_y, hover_text, labels = [], [], [], []

    for node_id in G.nodes():
        x, y = pos[node_id]
        data = G.nodes[node_id]

        node_x.append(x)
        node_y.append(y)
        labels.append(data["label"])
        hover_text.append(
            f"<b>{data['label']}</b><br>"
            f"Inventory: {data['inventory']}<br>"
            f"Backorders: {data['backorders']}<br>"
            f"Remaining time: {data['remaining_time']}"
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=labels,
        textposition="bottom center",
        hovertext=hover_text,
        hoverinfo="text",
        marker=dict(
            size=40,
            color="dodgerblue",
            line=dict(width=2, color="black"),
        ),
    )

    # -----------------------
    # Arrow heads (annotations)
    # -----------------------
    annotations = []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        xs, ys, xe, ye = shorten_edge(x0, y0, x1, y1, NODE_RADIUS)

        annotations.append(
            dict(
                ax=xs,
                ay=ys,
                x=xe,
                y=ye,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1.2,
                arrowwidth=2,
                arrowcolor="black",
            )
        )

    # -----------------------
    # Final figure
    # -----------------------
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            showlegend=False,
            hovermode="closest",
            annotations=annotations,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    fig.show()
