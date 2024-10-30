import networkx as nx
import plotly.express as px
import plotly.graph_objects as go

from .chef import NodeState
from .db import EdgesDB, NodeDB, create_session

NODE_STATE_COLORS = {
    NodeState.PLANNED: px.colors.qualitative.Plotly[1],  # #EF553B
    NodeState.SCHEDULED: px.colors.qualitative.Plotly[2],  # #00CC96
    NodeState.COOKING: px.colors.qualitative.Plotly[3], # #AB63FA
    NodeState.COOKED: px.colors.qualitative.Plotly[4],  # #FFA15A
    NodeState.UNKNOWN: px.colors.qualitative.Plotly[5] # #19D3F3
}

def create_networkx_graph_from_db():
    graph = nx.DiGraph()

    session = create_session()
    node_entries = session.query(NodeDB).where(NodeDB.state!=NodeState.COOKED).all()

    for node in node_entries:
        constraint = node.to_ingredient_constraint()
        graph.add_node(constraint)
        graph.nodes[constraint]['state'] = node.state
        graph.nodes[constraint]['pos'] = (node.posx, node.posy)

    edge_entries = session.query(EdgesDB).where(EdgesDB.active).all()
    for edge in edge_entries:
        source = session.query(NodeDB).where(NodeDB.id == edge.source).one().to_ingredient_constraint()
        sink = session.query(NodeDB).where(NodeDB.id == edge.sink).one().to_ingredient_constraint()
        if source in graph.nodes and sink in graph.nodes:
            graph.add_edge(source, sink)

    return graph


def create_plotly_graph(nx_graph: nx.Graph) -> go.Figure:
    edge_x = []
    edge_y = []
    for edge in nx_graph.edges():
        x0, y0 = nx_graph.nodes[edge[0]]['pos']
        x1, y1 = nx_graph.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines+markers',
        marker=dict(
            symbol="arrow",
            size=15,
            angleref="previous",
        ),
    )

    node_x = []
    node_y = []
    node_color = []
    node_name = []
    for node in nx_graph.nodes():
        x, y = nx_graph.nodes[node]['pos']
        state = nx_graph.nodes[node].get('state', NodeState.UNKNOWN)
        node_x.append(x)
        node_y.append(y)
        node_color.append(NODE_STATE_COLORS[state])
        node_name.append(node.name)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(color=node_color, size=16),
        text=node_name,
    )

    fig = go.Figure(
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.add_trace(edge_trace)
    fig.add_trace(node_trace)
    fig.update_layout(
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1])
    )
    return fig
