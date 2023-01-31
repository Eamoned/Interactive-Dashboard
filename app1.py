import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import dash_table as dt
from plotly import tools
import numpy

####### MANUFACTURING & SUPPLIER DEFECTS ANALYSIS  #########################

md_all = pd.read_csv('MD_data.csv')


md_all["Month"] = pd.to_datetime(md_all["Date Raised"]).dt.strftime('%Y-%m')
supp_all = md_all[md_all['Root Cause Category']=='Supplier']
md_all = md_all[md_all['Root Cause Category']=='Process']

# Groupby for Date & Failure Mode (for heatmap)
df_fail = md_all.groupby(['Year','Month','Failure Mode']).sum().reset_index()
#print(df_fail.head())

# Groupby for Date & Location (for heatmap)
df_loc = md_all.groupby(['Year','Month','Location']).sum().reset_index()
#print(df_loc.head())


# Pivot table for Failure Modes
md_pivot1 = md_all.groupby(['Month','Failure Mode']).sum()['Qty']
md_pivot1 = md_pivot1.reset_index()

# table for Failure Mode Comments
table_md = md_all[['Month', 'Failure Mode', 'Failure Mode Comment', 'Qty']]

# Pivot table for Supplier Non-Conformance
supp_pivot1 = supp_all.groupby(['Month','Supplier','Part Number','Failure Mode']).sum()['Qty']
supp_pivot1 = supp_pivot1.reset_index()

#####################################################################################



############### Monthly Summaries Data  #############################################
summaries = pd.read_csv('monthly_summaries_data.csv')
#print(summaries.head())
summaries_2 = summaries[['Year', 'Series-C', 'Series-D', 'Series-E', 'Series-A', 'Series-B','Series-G']]
#print(summaries_2.head())
summaries_melt = summaries_2.melt(id_vars=['Year'], var_name='Product Family', value_name='Qty')
#print(summaries_melt)

######################################################################################


############################# CASE & CR SUMMARIES ###################################

cust_df = pd.read_csv('CaseCRSummary.csv')
#cust_df = pd.read_csv('CaseCRSummary_Dec2019.csv')
cust_df = cust_df.iloc[::-1] # reverse the rows  - earlier years first

# Filtered for Actual Complaints only
cust_comp = cust_df[cust_df['COMPLAINT / REQUEST?']=='Actual Complaint']

# Convert date from string to DateTime object
cust_comp['Case OPENED'] = pd.to_datetime(cust_comp['Case OPENED'])

# Create Date column
cust_comp["Date"] = pd.to_datetime(cust_comp["Case OPENED"]).dt.strftime('%Y-%m')

# For Customer Complaints Breakdown table
cust_table = cust_comp[['Case No','Case CLOSED','CR Closed', 'Family', 'Customer','Subject','EDR?']]

########################################################################################

app = dash.Dash()
server = app.server

# Summaries chart traces
series = ['Series-C', 'Series-D', 'Series-E', 'Series-A', 'Series-B', 'Series-G' ]
series_2 = ['MD', 'CustComplaints_All']
# MD Monthly Dropdown options
month_option = sorted(md_all['Month'].unique())
MnYr_option_cust = cust_comp['Mn/Yr'].unique()

# MD Failure Mode & Location Dropdown options
MD_trace = ['Failure Mode', 'Location']
# MD Years Dropdown options
year_option = sorted(md_all['Year'].unique())
# Case/Customer Years Dropdown Options
case_year_option = sorted(cust_df['Year'].unique())

# Create a Dash layout that contains a Graph component:
app.layout = html.Div([
        html.H1('Quality Performance Dashboard'),
        html.Div([dcc.Graph(id = 'Chart1',
                    figure = {'data': [
                            go.Scatter(x=summaries['Year'],
                                        y=summaries['ProdTotal'],
                                        mode='lines+markers')
                    ],
                    'layout':go.Layout(title='Production Totals',
                                        xaxis={'title':'Month/Year'},
                                        yaxis={'title': 'Total Product Quantity'}
                    )})


        ]),

        html.Div([dcc.Graph(id = "chart2",
                    figure = {'data':[
                            go.Scatter(x=summaries_2['Year'],
                                        y=summaries_2[item],
                                        mode='lines+markers',
                                        name= item) for item in series

                    ],
                    "layout":go.Layout(title="Product Production Totals",
                                        xaxis={'title':'Month/Year'},
                                        # xaxis=dict(title='Month/Year')
                                        yaxis={'title': 'Product Quantity'}
                    )})
        ]),

        html.Div([dcc.Graph(id='chart3',
                    figure = {'data':[
                            go.Heatmap(x=summaries_melt['Product Family'],
                                        y=summaries_melt['Year'],
                                        z=summaries_melt["Qty"],
                                        colorscale = "Jet" )
                    ],
                    "layout":go.Layout(title="Heatmap of Product Family Shipped",
                                        yaxis={'title':'Month/Year'},
                                        # xaxis=dict(title='Month/Year')
                                        xaxis={'title': 'Product Quantity'}
                    )})


        ],#style={'width': '25%', 'float':'left'}

        ),

        html.Div([dcc.Graph(id = "chart4",
                    figure = {'data':[
                            go.Scatter(x=summaries['Year'],
                                        y=summaries[item],
                                        mode='lines+markers',
                                        name= item) for item in series_2

                    ],
                    "layout":go.Layout(title="Manufacturing Performance",
                                        xaxis={'title':'Month/Year'},
                                        # xaxis=dict(title='Month/Year')
                                        yaxis={'title': 'Defects'}
                    )})
        ]),

        html.Div([dcc.Graph(id = 'Chart5',
                    figure = {'data': [
                            go.Scatter(x=summaries['Year'],
                                        y=summaries['MQD'],
                                        mode='lines+markers')
                    ],
                    'layout':go.Layout(title='MQD',
                                        xaxis={'title':'Month/Year'},
                                        yaxis={'title': 'Fails'}
                    )})


        ], style={'width': '33%', 'float':'left'}
        ),

        html.Div([dcc.Graph(id = 'Chart6',
                    figure = {'data': [
                            go.Scatter(x=summaries['Year'],
                                        y=summaries['NQC_inter_K'],
                                        mode='lines+markers')
                    ],
                    'layout':go.Layout(title='NQC Internal',
                                        xaxis={'title':'Month/Year'},
                                        yaxis={'title': '$K'}
                    )})


        ], style={'width': '33%', 'float':'left'}
        ),


        html.Div([dcc.Graph(id = 'Chart7',
                    figure = {'data': [
                            go.Scatter(x=summaries['Year'],
                                        y=summaries['NQC_exter_K'],
                                        mode='lines+markers')
                    ],
                    'layout':go.Layout(title='NQC External',
                                        xaxis={'title':'Month/Year'},
                                        yaxis={'title': '$K'}
                    )})


        ], style={'width': '33%', 'float':'left'}
        ),

        ## MANUFACTURING DEFECT ANALYSIS 
        html.Hr(),
        html.H2('Manufacturing Defect Analysis:'),
        html.Hr(),
      
        # Manufacturing Defects for Failure Mode & Location
        html.Div([
            dcc.Graph(id ='heatmap2'),
            dcc.Dropdown(
                    id='Heatmap Year Picker',
                    options=[{'label': yr, 'value': yr} for yr in year_option],
                    value=year_option[-1])

        ], style={'width': '100%', 'display': 'inline-block'}
        ),

          # Manufacturing defects for Failure mode or location
        html.Div([
                dcc.Graph(id='bar-3'),
                dcc.Dropdown(
                    id='bar trace',
                    options=[{'label': i, 'value': i} for i in MD_trace],
                    value='Failure Mode')
        ], style={'width': '100%', 'display': 'inline-block'}
        ),

        html.Div([
                dcc.Graph(id='bar-1'),
                dcc.Dropdown(
                    id='Month Picker',
                    options=[{'label': i.title(), 'value': i} for i in month_option],
                    value=month_option[-1])
        ], style={'width': '45%', 'float':'left'}
        ),

        html.Div([
                dcc.Graph(id='bar-2'),
                dcc.Dropdown(
                    id='Month Picker2',
                    options=[{'label': i.title(), 'value': i} for i in month_option],
                    value=month_option[-1])
        ], style={'width': '45%', 'float':'right'}
        ),

        
        html.Div([
                html.H3('Failure Mode Breakdown'),
                dcc.Dropdown(
                id='table1_dropdown',
                options=[{'label':month, 'value':month} for month in month_option],
                value = month_option[0]
                ),
                dt.DataTable(id='table1-container',
                columns=[{'id': col, 'name': col} for col in md_pivot1.columns.values])
        ], style={'width': '60%', 'display': 'inline-block'}
        ),
        html.Div([
                html.H3('Failure Details'),
                dcc.Dropdown(
                id='table2_dropdown',
                options=[{'label':month, 'value':month} for month in month_option],
                value = month_option[0]
                ),
                dt.DataTable(id='table2-container',
                columns=[{'id': col, 'name': col} for col in table_md.columns.values])
        ], style={'width': '75%', 'display': 'inline-block'}
        ),

        ## CUSTOMER COMPLAINTS ANALYSIS
        html.Hr(),
        html.H2('Customer Complaints & Returns Analysis:'),
        html.Hr(),
        #Cases v Actual Complaints Bar chart
        html.Div([
                dcc.Graph(id='bar-4'),
                dcc.Dropdown(
                    id='Year Picker',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value=year_option[-1])
        ], style={'width': '20%', 'float':'left'}
        ),

        ## Line chart of Cases, Complaints, EDR & LAC - Line Chart
        html.Div([
                dcc.Graph(id='Chart8'),
                dcc.Dropdown(
                    id='Chart Year Picker',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value=year_option[-1])
        ], style={'width': '80%', 'float':'right'}
        ),

        # Customer Complaints by Customer - Bar Chart
        html.Div([
                dcc.Graph(id='bar-5'),
                dcc.Dropdown(
                    id='Year Picker5',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value = year_option[-1])
        ], style={'width': '50%', 'float':'left'}
        ),

        # EDR by Customer - Bar Chart
        html.Div([
                dcc.Graph(id='bar-6'),
                dcc.Dropdown(
                    id='Year Picker6',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value = year_option[-1])
        ], style={'width': '50%', 'float':'right'}
        ),

        # Heatmap of Monthly Customer Complaints for Customers & Product Family - Heatmap
        html.Div([
            dcc.Graph(id ='heatmap3'),
            dcc.Dropdown(
                    id='Heatmap Year Picker3',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value=year_option[-1])
        ],style={'width': '100%', 'display': 'inline-block'}),

        # Complaints by Family & Customer - Bar Chart
        html.Div([
                dcc.Graph(id='bar-7'),
                dcc.Dropdown(
                    id='Year Picker7',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value = year_option[-1])
        ], style={'width': '100%', 'display': 'inline-block'}
        ),

        # Complaints for Product & Failure Mode - Bar chart
        html.Div([
                dcc.Graph(id='bar-9'),
                dcc.Dropdown(
                    id='Year Picker9',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value=year_option[-1])
        ], style={'width': '50%', 'float':'left'}
        ),

        # Complaints for Product & Sub-Failure Mode - Bar chart
        html.Div([
                dcc.Graph(id='bar-10'),
                dcc.Dropdown(
                    id='Year Picker10',
                    options=[{'label': yr, 'value': yr} for yr in case_year_option],
                    value=year_option[-1])
        ], style={'width': '50%', 'float':'right'}
        ),
        
        # Customer Complaints Detail breakdown - Table
        html.Div([
                html.H3('Customer Complaints Detail breakdown'),
                dcc.Dropdown(
                id='table4_dropdown',
                options=[{'label':month, 'value':month} for month in MnYr_option_cust],
                value = MnYr_option_cust[0]
                ),
                dt.DataTable(id='table4-container',
                columns=[{'id': col, 'name': col} for col in cust_table.columns.values])
        ], style={'width': '75%', 'display': 'inline-block'}
        ),


        ## SUPPLIER ANALYSIS
        html.Hr(),
        html.H2('Supplier Failure Analysis:'),
        html.Hr(),

        # Supplier & Failure Mode - Bar chart
        html.Div([
                dcc.Graph(id='bar-11'),
                dcc.Dropdown(
                    id='Month Picker3',
                    options=[{'label': i.title(), 'value': i} for i in month_option],
                    value=month_option[-1])
        ], style={'width': '45%', 'float':'left'}
        ),
        # Supplier & Failure Mode - Bar chart
        html.Div([
                dcc.Graph(id='bar-12'),
                dcc.Dropdown(
                    id='Month Picker4',
                    options=[{'label': i.title(), 'value': i} for i in month_option],
                    value=month_option[-1])
        ], style={'width': '45%', 'float':'right'}
        ),

        html.Div([
                html.H3('Supplier Non-Conformance Details'),
                dcc.Dropdown(
                id='table3_dropdown',
                options=[{'label':month, 'value':month} for month in month_option],
                value = month_option[0]
                ),
                dt.DataTable(id='table3-container',
                columns=[{'id': col, 'name': col} for col in supp_pivot1.columns.values])
        ], style={'width': '75%', 'display': 'inline-block'}
        ),

])

# Heatmap map of MD for Failure Mode & Location
@app.callback(Output(component_id='heatmap2', component_property='figure'),
            [Input(component_id='Heatmap Year Picker', component_property='value')])
def update_heatmap(select_year):

    filt_fail = df_fail[df_fail['Year'] == select_year]
    filt_loc = df_loc[df_loc['Year'] == select_year]

    trace1 = go.Heatmap(x = filt_fail["Failure Mode"],
                    y=filt_fail['Month'],
                    z=filt_fail["Qty"],  # this will be the color
                    colorscale = "Jet",
                    zmin=0, zmax=30) # min & max temps to keep all plots similar
    trace2 = go.Heatmap(x = filt_loc["Location"],
                    y=filt_loc['Month'],
                    z=filt_loc["Qty"],  # this will be the color
                    colorscale = "Jet",
                    zmin=0, zmax=30) # min & max temps to keep all plots similar

    fig = tools.make_subplots(rows=1, cols=2, subplot_titles=["Failure Mode", "Location"], shared_yaxes=True)
    # Pass in the coordinates of
    fig.append_trace(trace1,1,1) # trace 1 in row 1 column 1
    fig.append_trace(trace2,1,2) # trace 1 in row 1 column 2

    fig["layout"].update(title="Heatmap of Monthly Manufacturing Defects for Failure Mode & Location")  # call layout from fig object and run update command
    fig["layout"].update(yaxis=dict(title="Date"))
    fig["layout"].update(xaxis=dict(title="Failure Mode / Location"))

    return fig

# we want to connect the input fronm the dropdown menu and you want to grab that year picker value and put that value in the output for the graph
@app.callback(Output(component_id='bar-1', component_property='figure'),  #
            [Input(component_id='Month Picker', component_property='value')])
def update_figure(selected_month): # connects the dropdown to the actual figure - input to the figure
# Based off the selected month that's passed in as input we will filter our dataframe for that month and produce * traces for each continent

   # Data only selected for the selected year from dropdown
    filtered_df = md_all[md_all["Month"] == selected_month] # eg, ddataframe of 2019-01 only
    dfg = filtered_df.pivot_table(columns='Product', index='Failure Mode', aggfunc='sum', values='Qty')


    return {
        'data':[
                go.Bar(x=dfg.index,
                y=dfg[product],
                name=product) for product in dfg.columns],

        'layout':go.Layout(title='Manufacturing Defects by Failure Mode & Product',
                            barmode='stack'
        )
    }


@app.callback(Output(component_id='bar-2', component_property='figure'),  #
            [Input(component_id='Month Picker2', component_property='value')])
def update_figure(selected_month):

   # Data only selected for the selected year from dropdown
    filtered_df = md_all[md_all["Month"] == selected_month] # eg, ddataframe of 2019-01 only
    dfg2 = filtered_df.pivot_table(columns='Product', index='Location', aggfunc='sum', values='Qty')


    return {
        'data':[
                go.Bar(x=dfg2.index,
                y=dfg2[product],
                name=product) for product in dfg2.columns],


        'layout':go.Layout(title='Manufacturing Defects by Location & Product',
                        barmode='stack'
        )
    }

@app.callback(Output(component_id='bar-3', component_property='figure'),  #
            [Input(component_id='bar trace', component_property='value')])
def update_trace(selected_trace):
        dfg3 = md_all.pivot_table(columns=selected_trace, index='Month', aggfunc='sum', values='Qty')

        return {
                'data':[
                        go.Bar(x=dfg3.index,
                        y=dfg3[fail],
                        name=fail) for fail in dfg3.columns],

                'layout':go.Layout(title='Manufacturing Defects',
                                        barmode='stack'
                )
        }

# Failure Mode Breakdown table
@app.callback(Output(component_id='table1-container', component_property='data'),
    [Input(component_id='table1_dropdown', component_property='value')])
def display_table(mth):
    pivot1 = md_pivot1[md_pivot1.Month==mth]
    pivot1 = pivot1.sort_values('Qty', ascending=False)
    return pivot1.to_dict('records')

# Failure Mode Comment table
@app.callback(Output(component_id='table2-container', component_property='data'),
    [Input(component_id='table2_dropdown', component_property='value')])
def display_table(mth):
    table = table_md[table_md.Month==mth]
    table = table.sort_values('Failure Mode', ascending=False)
    return table.to_dict('records')
##################################

# Customer Complaints Analysis
# Chart summary of Complaints, cases, EDRs & LAC Complaints
@app.callback(Output(component_id='Chart8', component_property='figure'),
            [Input(component_id='Chart Year Picker', component_property='value')])
def update_figure(selected_year):

       chart7 = cust_df[cust_df["Year"] == selected_year]

       trace0 = chart7[chart7['COMPLAINT / REQUEST?']== 'Actual Complaint'].groupby('Mn/Yr', sort=False).count()['COMPLAINT / REQUEST?'].to_frame()
       trace1 = chart7[chart7['EDR?']== 'Y'].groupby('Mn/Yr', sort=False).count()['EDR?'].to_frame()
       trace2 = chart7.groupby('Mn/Yr', sort=False).count()['Case No'].to_frame()
       trace3 = chart7[chart7['Entity Responsible']== 'LAC'].groupby('Mn/Yr', sort=False).count()['Entity Responsible'].to_frame()


       trace = go.Scatter(
        x = trace0.index,
        y = trace0['COMPLAINT / REQUEST?'],
        mode = 'lines+markers',
        name = 'Actual Complaints'
       )
       trace1 = go.Scatter(
        x = trace1.index,
        y = trace1['EDR?'],
        mode = 'lines+markers',
        name = 'EDR'
       )
       trace2 = go.Scatter(
        x = trace2.index,
        y = trace2['Case No'],
        mode = 'lines+markers',
        name = 'Cases'
       )
       trace3 = go.Scatter(
        x = trace3.index,
        y = trace3['Entity Responsible'],
        mode = 'lines+markers',
        name = 'Complaint LAC'
       )

       return {
           'data': [trace, trace1, trace2, trace3],
           'layout':go.Layout(title='Cases, Actual Complaints, EDR & LAC Complaints')

       }

# Bar Graph Cases vs Complaints
@app.callback(Output(component_id='bar-4', component_property='figure'),  #
            [Input(component_id='Year Picker', component_property='value')])
def update_figure(selected_year): # connects the dropdown to the actual figure - input to the figure
   # Data only selected for the selected year from dropdown
    filtered_cust = cust_df[cust_df["Year"] == selected_year]
    filtered_cust = filtered_cust.groupby('COMPLAINT / REQUEST?').count().reset_index()[[ 'COMPLAINT / REQUEST?','Case No']]

    return {
        'data':[
                # go.Bar(x=filtered_cust['COMPLAINT / REQUEST?'],
                # y=filtered_cust['Case No'])],
                go.Pie(labels=filtered_cust['COMPLAINT / REQUEST?'], 
                        values=filtered_cust['Case No'],
                        hoverinfo='label+percent', textinfo='value')],

        'layout':go.Layout(title='Cases vs Actual Complaints',
                                margin = dict(t=30, l=15, r=0, b=0)
                               
                          

        )
    }

# Bar plot of Customer Complaints & Customer
@app.callback(Output(component_id='bar-5', component_property='figure'),  #
            [Input(component_id='Year Picker5', component_property='value')])
def update_trace(selected_year):
        filter_comp = cust_comp[cust_comp["Year"] == selected_year]
        df_5= filter_comp.pivot_table(columns='Customer', index='COMPLAINT / REQUEST?', aggfunc='count', values='Case No')
        df_5 = df_5.transpose()
        df_5 = df_5.sort_values(by=['Actual Complaint'],ascending=False).head(10) 
        df_5 = df_5.transpose()

        return {
                'data':[
                        go.Bar(x=df_5.index,
                        y=df_5[customer],
                        name=customer) for customer in df_5.columns],

                'layout':go.Layout(title='Customer & Customer Complaints',
                                        barmode='stack'
                )
        }

# Bar plot of EDR & Customers
@app.callback(Output(component_id='bar-6', component_property='figure'),
            [Input(component_id='Year Picker6', component_property='value')])
def update_trace(selected_year):

        filter_comp = cust_comp[(cust_comp["Year"] == selected_year) & (cust_comp['EDR?']=='Y')]
        df_6= filter_comp.pivot_table(columns='Customer', index='EDR?', aggfunc='count', values='Case No')
        #df_6 = df_6.transpose()
        #df_6 = df_6.sort_values(by=['Y'],ascending=False).head(10) 
        #df_6 = df_6.transpose()

        return {
                'data':[
                        go.Bar(x=df_6.index,
                        y=df_6[customer],
                        name=customer) for customer in df_6.columns],

                'layout':go.Layout(title='Customer & EDR',
                                        barmode='stack'
                )
        }

# Heatmap3 of Monthly Customer Complaints for Customers & Product Family
@app.callback(Output(component_id='heatmap3', component_property='figure'),
            [Input(component_id='Heatmap Year Picker3', component_property='value')])
def update_heatmap(selected_year):
    filter_comp = cust_comp[cust_comp["Year"] == selected_year]
    cust = filter_comp.groupby(['Year','Date','Customer'])['Case No'].count().reset_index()
    family = filter_comp.groupby(['Year','Date','Family'])['Case No'].count().reset_index()

    trace1 = go.Heatmap(x = cust["Customer"],
                    y=cust['Date'],
                    z=cust["Case No"],  # this will be the color
                    colorscale = "Jet",
                    zmin=0, zmax=8) # min & max temps to keep all plots similar
    trace2 = go.Heatmap(x = family["Family"],
                    y=family['Date'],
                    z=family["Case No"],  # this will be the color
                    colorscale = "Jet",
                    zmin=0, zmax=8) # min & max temps to keep all plots similar


    fig = tools.make_subplots(rows=1, cols=2, subplot_titles=["Customers", "Product Family"],shared_yaxes=True)
    fig.append_trace(trace1,1,1) # trace 1 in row 1 column 1
    fig.append_trace(trace2,1,2) # trace 1 in row 1 column 2

    fig["layout"].update(title="Heatmap of Monthly Customer Complaints for Custmers & Product Family")  # call layout from fig object and run update command
    fig["layout"].update(yaxis=dict(title="Date"))
    fig["layout"].update(xaxis=dict(title="Customers / Product Family"))

    return fig

# Bar plot of Complaints by Product Family & Customer
@app.callback(Output(component_id='bar-7', component_property='figure'),  #
            [Input(component_id='Year Picker7', component_property='value')])
def update_trace(selected_year):
        filter_comp = cust_comp[cust_comp["Year"] == selected_year]
        #df_7 = filter_comp.groupby('Customer').filter(lambda x : (x['Customer'].count()>1).any())
        #df_7 = df_7.pivot_table(columns='Customer', index='Family', aggfunc='count', values='Case No')
        df_7 = filter_comp.pivot_table(columns='Customer', index='Family', aggfunc='count', values='Case No')

        return {
                'data':[
                        go.Bar(x=df_7.index,
                        y=df_7[customer],
                        name=customer) for customer in df_7.columns],

                'layout':go.Layout(title='Complaints by Product Family & Customer',
                                        barmode='stack'
                )
        }


# Bar Graph Complaints for Product Family v Failure Mode
@app.callback(Output(component_id='bar-9', component_property='figure'),
            [Input(component_id='Year Picker9', component_property='value')])
def update_figure(selected_year):
   # Data only selected for the selected year from dropdown
    #filter_cust2 = cust_df[cust_df['COMPLAINT / REQUEST?']=='Actual Complaint']
    #filter_cust2 = filter_cust2[filter_cust2["Year"] == selected_year]
    filter_cust2 = cust_df[(cust_df['COMPLAINT / REQUEST?']=='Actual Complaint') & (cust_df['Year']== selected_year)] 
    filter_cust2 = filter_cust2.pivot_table(columns='Failure Mode', index='Family', aggfunc='count', values='Case No')

    return {
        'data':[
                go.Bar(x=filter_cust2.index,
                y=filter_cust2[mode],
                name=mode)for mode in filter_cust2.columns],

        'layout':go.Layout(title='Customer Complaints: Product Family v Failure Mode',
                                barmode='stack'

        )
    }

# Bar Graph Complaints for Product Family v Sub-Failure Mode
@app.callback(Output(component_id='bar-10', component_property='figure'),
            [Input(component_id='Year Picker10', component_property='value')])
def update_figure(selected_year):
   # Data only selected for the selected year from dropdown
    #filter_cust3 = cust_df[cust_df['COMPLAINT / REQUEST?']=='Actual Complaint']
    #filter_cust3 = filter_cust3[filter_cust3["Year"] == selected_year]
    filter_cust3 = cust_df[(cust_df['COMPLAINT / REQUEST?']=='Actual Complaint') & (cust_df['Year']==selected_year)]
    #filter_cust3 = filter_cust3.groupby('Sub Failure Mode').filter(lambda x : (x['Sub Failure Mode'].count()>1).any())
    filter_cust3 = filter_cust3.pivot_table(columns='Sub Failure Mode', index='Family', aggfunc='count', values='Case No')

    return {
        'data':[
                go.Bar(x=filter_cust3.index,
                y=filter_cust3[mode],
                name=mode)for mode in filter_cust3.columns],

        'layout':go.Layout(title='Customer Complaints: Product Family v Sub Failure Mode',
                                barmode='stack'

        )
    }

# Customer Complaints Detailed Breakdown - Table
@app.callback(Output(component_id='table4-container', component_property='data'),
    [Input(component_id='table4_dropdown', component_property='value')])
def display_table(mth):
    table = cust_comp[cust_comp['Mn/Yr']==mth]
    cust_table = table[['Case No','Case CLOSED','CR Closed', 'Family', 'Customer','Subject','EDR?']]
    return table.to_dict('records')




# Non-Conformance: Supplier & Failure Mode
@app.callback(Output(component_id='bar-11', component_property='figure'),  #
            [Input(component_id='Month Picker3', component_property='value')])
def update_figure(selected_month): 
   # Data only selected for the selected year from dropdown
    filtered_df = supp_all[supp_all["Month"] == selected_month] # eg, ddataframe of 2019-01 only
    dfg = filtered_df.pivot_table(columns='Failure Mode', index='Supplier', aggfunc='sum', values='Qty')


    return {
        'data':[
                go.Bar(x=dfg.index,
                y=dfg[fault],
                name=fault) for fault in dfg.columns],

        'layout':go.Layout(title='Non-Conformance: Supplier & Failure Mode',
                            barmode='stack'
        )
    }

# Non-Conformance: Product & Failure Mode
@app.callback(Output(component_id='bar-12', component_property='figure'),  
            [Input(component_id='Month Picker4', component_property='value')])
def update_figure(selected_month): 
   # Data only selected for the selected year from dropdown
    filtered_df = supp_all[supp_all["Month"] == selected_month] 
    dfg = filtered_df.pivot_table(columns='Failure Mode', index='Part Number', aggfunc='sum', values='Qty')


    return {
        'data':[
                go.Bar(x=dfg.index,
                y=dfg[fault],
                name=fault) for fault in dfg.columns],

        'layout':go.Layout(title='Non-Conformance: Part No. & Failure Mode',
                            barmode='stack'
        )
    }

# Supplier Non-Conformance Table 
@app.callback(Output(component_id='table3-container', component_property='data'),
    [Input(component_id='table3_dropdown', component_property='value')])
def display_table(mth):
    pivot = supp_pivot1[supp_pivot1.Month==mth]
    pivot = pivot.sort_values('Qty', ascending=False)
    return pivot.to_dict('records')

# Add the server clause:
if __name__ == '__main__':
    app.run_server()
