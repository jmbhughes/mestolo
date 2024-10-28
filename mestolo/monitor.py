from queue import Empty

import networkx as nx
from dash import Dash, Input, Output, State, callback, dcc, html

from .visualize import create_plotly_graph


def create_app(refresh_rate, monitor_queue):
    app = Dash()
    app.layout = html.Div([
        dcc.Store(id='old-node-graph'),
        dcc.Graph(id='live-node-graph'),
        # dcc.Store(id='previous-graph'),
        dcc.Interval(
            id='interval-component',
            interval=refresh_rate * 1000,  # in milliseconds
            n_intervals=0
        ),
    ])

    @callback(Output('live-node-graph', 'figure'),
                  Input('interval-component', 'n_intervals'),
                  State('old-node-graph', 'figure')
                  )
    def update_node_graph(n, old_node_graph):
        if old_node_graph is None:
            old_node_graph = create_plotly_graph(nx.DiGraph())

        try:
            nx_graph = monitor_queue.get(block=False)
        except Empty:
            nx_graph = None

        if nx_graph is None:
            new_fig = old_node_graph
        else:
            new_fig = create_plotly_graph(nx_graph)
        return new_fig

    return app
