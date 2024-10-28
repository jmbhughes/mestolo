import networkx
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go

from .chef import NodeState

G = nx.random_geometric_graph(200, 0.125)



NODE_STATE_COLORS = {
    NodeState.PLANNED: px.colors.qualitative.Plotly[1],
    NodeState.SCHEDULED: px.colors.qualitative.Plotly[2],
    NodeState.COOKING: px.colors.qualitative.Plotly[3],
    NodeState.COOKED: px.colors.qualitative.Plotly[4],
    NodeState.UNKNOWN: px.colors.qualitative.Plotly[5]
}

def create_plotly_graph(nx_graph: networkx.Graph) -> go.Figure:
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
