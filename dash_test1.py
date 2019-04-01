import seaborn as sns
from sklearn import datasets
import sklearn
import statsmodels.api as sm

import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import datetime, re
import plotly.graph_objs as go
import flask

class checklist_div:
    def __init__(self, id='', name = '', label_list='', value_list=''):
        self.id = id
        self.name = name
        self.dropdown_id = '_'.join([id,'dropdown'])
        self.checklist_id = '_'.join([id,'checklist'])
        self.checklist_and_dropdown_div_id = '_'.join([id,'checklist_and_dropdown'])
        self.radioitems_id = '_'.join([id,'radioitem'])
        self.label_list = label_list
        self.value_list = value_list

    def get_html_div(self, default_dropdown_value='All'):
        option1 = [{'label': x, 'value': y} for (x, y) in list(zip(self.label_list, self.value_list))]
        if default_dropdown_value =='':
            default_dropdown_value = 'All'

        checklist_div = html.Div(id=self.checklist_and_dropdown_div_id, children=
        [
            dcc.Dropdown(id=self.dropdown_id,
                         options=[
                             {'label': 'Select All', 'value': 'All'},
                             {'label': 'Select None', 'value': 'None'},
                             {'label': 'Select Latest', 'value': 'Latest'}
                         ],
                         placeholder="Select All or None",
                         value=default_dropdown_value,
                         multi=False),
            dcc.Checklist(id=self.checklist_id, options=option1, values= [x['value'] for x in option1],
                          style={'overflow-y': 'scroll',
                  'overflow-x': 'hidden'})
        ], style={'background': 'white', 'overflow-y': 'scroll', 'z-index':2,
                  'overflow-x': 'hidden'}
        )

        toggled_checklist_div = html.Div(children=[
                                        html.Div([
                                                    dcc.RadioItems(id=self.radioitems_id, options=[{'label': i, 'value': i} for i in ['Show', 'Hide']],
                                                    value='Hide', labelStyle={'display': 'inline-block'}, style={'background': 'white', 'z-index':1})
                                                ]),
                                        checklist_div
                                        ])

        return toggled_checklist_div

class dropdown_div:
    def __init__(self, id='', name='', label_list='', value_list=''):
        self.id = id
        self.name = name
        self.label_list = label_list
        self.value_list = value_list
        self.dropdown_id = self.id + '_dropdown'

    def get_html_div(self):
        option1 = [{'label': x, 'value': y} for (x, y) in list(zip(self.label_list, self.value_list))]

        dropdown_div = html.Div(id=self.id, children=
        [
            dcc.Dropdown(id=self.dropdown_id,
                         options=option1,
                         placeholder="Select value",
                         multi=False,
                         value=self.value_list[0])
        ], style={"position": "relative", 'background': 'white', 'overflow-y': 'scroll',
                  'overflow-x': 'hidden'}
        )
        return dropdown_div


def create_app(name):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    tip = sns.load_dataset('tips')
    tip2 = tip.copy()
    tip2['customer_id'] = tip2.index
    df1 = pd.melt(tip2, id_vars=['customer_id', 'sex', 'smoker', 'day', 'time', 'size'],
                  value_vars=['total_bill', 'tip'], value_name='payment', var_name='tip_type')

    feature_names = ['sex', 'smoker', 'day', 'time', 'size', 'tip_type']

    grouping_factor_dropdown_div = dropdown_div(id='grouping_factor', name='Grouping', label_list= feature_names, value_list= feature_names)

    spliter_dropdown_div = dropdown_div(id='spliter_factor', name='spliter', label_list=feature_names, value_list= feature_names)

    level_checklist_div = checklist_div(id= 'level', name= 'level', label_list=df1['sex'], value_list= df1['sex'])

    app = dash.Dash(name=name, external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        html.H3(children='Grouping View',id='header1'),
        html.Div([  html.Div([html.B('Select a grouping variable:', style={'background':'lightgrey'}),
                              grouping_factor_dropdown_div.get_html_div()],
                              style={"border": "1px solid #C8D4E3", "borderColor": "rgba(68,149,209,.9)"}),
                    html.Div([html.B('Select a splitting variable:' ,style={'background':'lightgrey'}),
                                spliter_dropdown_div.get_html_div()],
                              style={"border": "1px solid #C8D4E3", "borderColor": "rgba(68,149,209,.9)"}),
                    html.Div([html.B('Select Levels:' ,style={'background':'lightgrey'}),
                                level_checklist_div.get_html_div()],
                             style={"border": "1px solid #C8D4E3", "borderColor": "rgba(68,149,209,.9)"})],
                 style={"border": "3px solid #C8D4E3", "borderColor": "rgba(68,149,209,.9)", 'margin-left': '5px', 'margin-righ':'5px'}
                 ),
        html.Div(children= [dcc.Graph(id='figure')], style={'position': 'relative'})
        ])

    # Grouping Factor selector
    @app.callback(dash.dependencies.Output(spliter_dropdown_div.dropdown_id, 'options'),
                  [dash.dependencies.Input(grouping_factor_dropdown_div.dropdown_id, 'value')])
    def select_grouping_factor(grouping_factor):
        spliter_factors = []
        spliter_factors = feature_names
        option1 = [{'label': x, 'value': y} for (x, y) in list(zip(spliter_factors, spliter_factors))]
        return option1

    # click Splitter factor selector to set level checklist
    @app.callback(dash.dependencies.Output(level_checklist_div.checklist_id, 'options'),
                      [dash.dependencies.Input(spliter_dropdown_div.dropdown_id, 'value')])
    def spliter_selector(value):
        levels = df1[value]
        option1 = [{'label': x, 'value': y} for (x, y) in list(zip(levels, levels))]
        return option1

    #Select all or none of the checklist
    @app.callback(dash.dependencies.Output(level_checklist_div.checklist_id, 'values'),
                      [dash.dependencies.Input(level_checklist_div.dropdown_id, 'value'),
                       dash.dependencies.Input(spliter_dropdown_div.dropdown_id, 'value')])
    def clear_and_select_all_level_factor_checklist(all_or_none, spliter_value):
        if all_or_none =='All':
            values = df1[spliter_value].unique().tolist()
        if all_or_none == 'None':
            values = []
        if all_or_none == 'Latest':
            values = [df1[spliter_value].unique().tolist()[0]]
        return values

    #hide or show the level list
    @app.callback(dash.dependencies.Output(level_checklist_div.checklist_and_dropdown_div_id, 'style'),
                  [dash.dependencies.Input(level_checklist_div.radioitems_id, 'value')])
    def toggle_level_checklist(toggle_value):
        if toggle_value == 'Show':
            return {'display': 'block'}
        else:
            return {'display': 'none'}


    @app.callback(
        dash.dependencies.Output('figure', 'figure'),
        [dash.dependencies.Input(grouping_factor_dropdown_div.dropdown_id, 'value'),
         dash.dependencies.Input(spliter_dropdown_div.dropdown_id, 'value'),
         dash.dependencies.Input(level_checklist_div.checklist_id, 'values')
         ])
    def update_figure(grouping_factor, split_factor, selected_level_factors):

        selected_boolen_index_by_levels = df1[split_factor].apply(
            lambda x: True if x in selected_level_factors else False)

        selected_df = df1[selected_boolen_index_by_levels]

        traces = []

        for each in selected_level_factors:
            selected_df_tem = selected_df[selected_df[split_factor]==each]

            traces.append(go.Box(
                x=selected_df_tem[grouping_factor],
                y=selected_df_tem['payment'],
                text=selected_df_tem[split_factor],
                opacity=0.7,
                boxpoints='all',
                pointpos=0,
                marker={
                    'size': 10,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name = each
            ))

        return {
            'data': traces,
            'layout': go.Layout(
                yaxis={'title': 'Payment',
                       'type': 'linear',
                       'automargin': True,
                       },
                xaxis={'showticklabels':True, 'automargin': True, 'tickangle':45},
                margin={'l': 100, 'b': 150, 't': 10, 'r': 100},
                showlegend=True,
                hovermode='closest',
                boxmode='group'
            )
        }
    return app

if __name__ =='__main__':
     dash_app = create_app(name=__name__)
     dash_app.run_server(debug=True)
