
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, callback, dash_table, dcc, html

from .db import create_session
from .visualize import create_networkx_graph_from_db, create_plotly_graph

recipe_data = {'recipe1': 100, 'recipe2': 30, 'recipe3': 50}
column_names = ['id', 'schedule_time', 'current_priority', 'recipe', 'node']
schedule_columns =[{'name': v, 'id': v} for v in column_names]

def create_app(menu, monitor_queue, schedule_queue):
    recipe_names = sorted(list(menu.recipes.keys()))
    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = html.Div([
        dcc.Graph(id='live-node-graph'),
        dash_table.DataTable(id='schedule',
                             data=pd.DataFrame({name: [] for name in column_names}).to_dict('records'),
                             columns=schedule_columns),
        #dbc.Table(id='schedule'),
        dcc.Dropdown(recipe_names, recipe_names[0], id='recipe-dropdown'),
        dbc.Row(id='recipe-stats', className="mb-4"),
        dcc.Interval(
            id='interval-component',
            interval=menu.refresh_delay * 1000,  # in milliseconds
            n_intervals=0
        ),
    ])

    @callback(
        Output('schedule', 'data'),
        Input('interval-component', 'n_intervals'),
    )
    def update_schedule(n):
        # query = session.query(ScheduledIngredientDB).filter(ScheduledIngredientDB.active).all()
        query = "SELECT * FROM scheduled_ingredient WHERE active = true"
        df = pd.read_sql_query(query, create_session().connection())
        return df.to_dict('records')
    #
    # @callback(
    #     Output('schedule', 'children'),
    #     Input('interval-component', 'n_intervals'),
    # )
    # def update_schedule(n):
    #     try:
    #         df = schedule_queue.get(block=False)
    #     except Empty:
    #         print("NO SCHEDULE")
    #         df = pd.DataFrame({"names": [], "scheduled": [], "priority": []})
    #
    #     table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)
    #     return table

    @callback(Output('recipe-stats', 'children'),
              Input('recipe-dropdown', 'value'))
    def update_recipe_stats(recipe_name):
        card_content = [
            dbc.CardHeader("Currently running"),
            dbc.CardBody(
                [
                    html.P(
                        f"{recipe_data[recipe_name]}",
                        className="card-text",
                    ),
                ]
            ),
        ]
        return [dbc.Col(dbc.Card(card_content, color="success", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="warning", inverse=True)),
                dbc.Col(dbc.Card(card_content, color="danger", inverse=True))]

    @callback(Output('live-node-graph', 'figure'),
                  Input('interval-component', 'n_intervals'),
                  )
    def update_node_graph(n):
        nx_graph = create_networkx_graph_from_db()
        return create_plotly_graph(nx_graph)

    return app
