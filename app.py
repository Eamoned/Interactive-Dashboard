#######
# Objective: add authorization to your dashboard using dash_auth package
# Create a dashboard that takes in two or more
# input values and returns their product as the output.
######

# Perform imports here:
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input
import dash_auth # pip install dash-auth

# in order to register these username password pairs to your application for basic authorisation
# store username and PW combinations as a list inside a script which may, or may not be sufficient for your use case
USERNAME_PASSWORD_PAIRS = [['username', 'password'], ['jamesbond', '007']]

# Launch the application:
app = dash.Dash()
# here we pass in the application and our username and password pairs
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

# in order to deploy this app to Heroku we add the following code
server = app.server

# Create a Dash layout that contains input components
# and at least one output. Assign IDs to each component:

app.layout = html.Div([
                # this is the input
                dcc.RangeSlider(id='range-slider', min=-5, max=6, step = 1, marks={i: i for i in range(-5, 7)}, value=[-1, 1]),
                # this is the output
                html.H1(id='product-output')
], style={'width': '50%'})

# Create a Dash callback:

@app.callback(Output(component_id='product-output', component_property='children'),  # the paramter adusted inside this Div will be children which is essentially
                [Input('range-slider', 'value')])
def update_value(value_list): # the input 'wheels' goes into this function and the fuctions returns back the value for the chidren which is a .....
    return value_list[0]*value_list[1]


# Add the server clause:

if __name__=='__main__':
    app.run_server()
