# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

sitedropdownoptions = [
    {'label': 'All Sites', 'value': 'ALL'}
]

for r in spacex_df["Launch Site"].unique():
    sitedropdownoptions.append({'label': r, 'value': r},)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                  options=sitedropdownoptions,
                                  value='ALL',
                                  placeholder="Select a Launch Site here",
                                  searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, 
                                    #marks= {0: '0', 100: '100'},
                                    step=1000, value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):  
    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df['class']==1].groupby("Launch Site", as_index=False)['class'].sum()
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Total Success launches by Site')
        return fig
    else:
        # return the outcomes piechart for a selected site
        data = spacex_df[spacex_df['Launch Site']==entered_site][["class"]]  #
        data["outcome"] = data['class'].apply(lambda r: 'Failure' if r== 0 else 'Success')
        data["outcomecount"] = 1
        fig = px.pie(data, values='outcomecount', 
        names='outcome', 
        title=f'Launch success rate for {entered_site}')
        return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id="payload-slider", component_property="value"))
def get_success_payload_chart(entered_site, entered_payload):
    minp, maxp = entered_payload
    data = spacex_df[(spacex_df["Payload Mass (kg)"]>=minp) & (spacex_df["Payload Mass (kg)"]<=maxp)]
    if entered_site == 'ALL':
        fig = px.scatter(data, x="Payload Mass (kg)", y="class", color="Booster Version Category")
    else:
        data = data[spacex_df['Launch Site']==entered_site]
        fig = px.scatter(data, x="Payload Mass (kg)", y="class", color="Booster Version Category")

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
