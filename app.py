import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import dash_bootstrap_components as dbc

# set plotly template
pio.templates.default = "plotly_white"


# Import data
results = pd.read_csv("data/model_results.csv")

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server


def create_figure(product_value=25, A_cost=1, B_cost=0.5):
    # assume glucose concentration of 100 g/kg to calculate final product concentration
    glucose_concentration = 100  # g/kg
    # assume product value is in units of $/g
    # assume additive concentrations in units of g/kg, and additive costs in units of $/g

    results["Product Concentration"] = results["Yield"] * glucose_concentration  # g/kg

    results["Product Value"] = results["Product Concentration"] * product_value  # $/kg
    results["Additive A Cost"] = results["Concentration A"] * A_cost  # $/g
    results["Additive B Cost"] = results["Concentration B"] * B_cost  # $/g
    results["Estimated Profit"] = (
        results["Product Value"]
        - results["Additive A Cost"]
        - results["Additive B Cost"]
    )

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=results["Estimated Profit"],
                x=results["Concentration B"],
                y=results["Concentration A"],
                zmin=0,
                zmax=5000,
                colorbar={
                    "title": "Estimated Profit/kg broth",
                    "tickprefix": "US$",
                    #     "dtick": 1.5,
                    #     "tickformatstops": [{"dtickrange": [0, 60]}],
                },
            )
        ],
    )

    fig.update_yaxes(title_text="Concentration B")
    fig.update_xaxes(title_text="Concentration A")

    fig.update_layout(
        title_text="How do Additive Concentrations Affect Potential Profit?",
        height=500,
    )
    return fig


app.layout = dbc.Container(
    children=[
        dbc.Card(
            children=[
                html.H1(
                    children="Interactive Techno-Economic Analysis",
                    style={
                        "marginTop": 15,
                        "marginLeft": 15,
                        "marginRight": 15,
                    },
                ),
                html.Div(
                    children="""
            This is an interactive analysis that considers the impact of additive costs and product value on the potential for profit.  Profit values appear binned because this is built on top of a random forest model fit to (dummy) experimental data. This model predicts yield given A and B concentrations during fermentation. Use the sliders to explore how product cost and additive concentration affects profit margin:
        """,
                    style={
                        "marginTop": 15,
                        "marginLeft": 15,
                        "marginRight": 15,
                    },
                ),
            ],
            style={"marginTop": 10, "marginBottom": 10},
        ),
        dbc.Card(
            children=[
                dcc.Graph(id="results", figure=create_figure()),
                html.Div(
                    children=[
                        "Product ($/g):",
                        dcc.Slider(0.5, 50, value=25, id="prod-val"),
                    ],
                    id="prod-val-label",
                    style={
                        "marginLeft": 15,
                        "marginRight": 15,
                    },
                ),
                html.Div(
                    children=[
                        "Additive A Cost ($/g):",
                        dcc.Slider(0.25, 25, value=2.5, id="add1-cost"),
                    ],
                    id="add1-cost-label",
                    style={
                        "marginLeft": 15,
                        "marginRight": 15,
                    },
                ),
                html.Div(
                    children=[
                        "Additive B Cost ($/g):",
                        dcc.Slider(0.25, 25, value=2.5, id="add2-cost"),
                    ],
                    id="add2-cost-label",
                    style={
                        "marginLeft": 15,
                        "marginRight": 15,
                    },
                ),
            ],
            style={"marginTop": 10, "marginBottom": 10},
        ),
    ]
)


@callback(
    Output(component_id="results", component_property="figure"),
    Input(component_id="prod-val", component_property="value"),
    Input(component_id="add1-cost", component_property="value"),
    Input(component_id="add2-cost", component_property="value"),
)
def remodel(prod_val, add1_cost, add2_cost):
    fig = create_figure(product_value=prod_val, A_cost=add1_cost, B_cost=add2_cost)
    return fig


if __name__ == "__main__":
    app.run(debug=True)
