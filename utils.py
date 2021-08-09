import pandas as pd
import numpy as np

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import tools
import plotly.offline as py
import plotly.express as px
from plotly.graph_objs import *

from itertools import cycle
from datetime import datetime



def process(row):
    date = "{}-{}-1".format(row.split('-')[0], row.split('-')[1])
    dt = datetime.strptime(date, "%Y-%W-%w")
    return dt.strftime("%Y-%m-%d")

def movement_chart(data, chart_title = '', fig_name='chart.html', file_save=False):
    data['timestamp_date'] = pd.DatetimeIndex(data['timestamp_date'])
    data = data.sort_values(by = 'timestamp_date')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=data['timestamp_date'], y=data['current_loan'], name = 'Total loan (USD)',
            fill='tozeroy', hovertemplate = 'Loan amount: %{y}<extra></extra>', #y:.2f
            marker_color = '#F63366',
        ), secondary_y=False,  # fill down to xaxis
    )
    fig.add_trace(
        go.Scatter(
            x=data['timestamp_date'], y=data['amount_coin_locked'], name = 'Total coin locked',
            fill='tozeroy', hovertemplate = 'Coin locked amount: %{y}<extra></extra>', #y:.2f
            marker_color = '#2BB1BB',
        ), secondary_y=True,  # fill down to xaxis
    )
    fig.update_layout(
        title="<b>"+chart_title+"<b>", #plot_bgcolor='rgb(255, 255, 255)',
        hovermode="x", template = "simple_white",
    )
    fig.update_xaxes(title_text="") #, type='date')
    fig.update_yaxes(title_text="Vault loan (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Vault coin locked amount", secondary_y=True)
    fig.update_layout(
        legend=dict(
            yanchor="bottom",
            y=0.1,
            xanchor="left",
            x=0.01
        ),
    )
    #if file_save:
    #    fig.write_html(fig_name)
    return fig

def coin_diff(data, chart_title = '', fig_name='chart.html', file_save=False):
    data['amount_coin_diff'] = data['amount_coin_locked'].diff()
    data['diff_neg_pos'] = data['amount_coin_diff'].map(lambda x: 'neg' if x<0 else 'pos')
    data['timestamp_date'] = pd.DatetimeIndex(data['timestamp_date'])
    data = data.dropna().sort_values(by = 'timestamp_date')
    fig = px.bar(
        data, x='timestamp_date', y='amount_coin_diff', color="diff_neg_pos",
        color_discrete_map = {'neg': '#F63366', 'pos': '#2BB1BB'}
    )

    fig.update_traces(
        showlegend=False,
        hovertemplate = 'Difference: %{y}<extra></extra>', #y:.2f
    )
    fig.update_layout(
        title="<b>"+chart_title+"<b>", #plot_bgcolor='rgb(255, 255, 255)',
        hovermode="x", template = "simple_white",
    )
    fig.update_xaxes(title_text="", type='date') #, tickformat="%b\n%Y")
    fig.update_yaxes(title_text="Amount of coin locked difference")
    #if file_save:
    #    fig.write_html(fig_name)

    return fig


def wallet_movement_chart(data, chart_title = '', fig_name='chart.html', file_save=False):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=data['timestamp_date'], y=data['Balance'], name = 'in BTC',
            fill='tozeroy', hovertemplate = '%{y} BTC<extra></extra>', #y:.2f
            marker_color = '#F63366',
        ), secondary_y=False,  # fill down to xaxis
    )
    fig.add_trace(
        go.Scatter(
            x=data['timestamp_date'], y=data['Balance USD'], name = 'In USD',
            fill='tozeroy', hovertemplate = 'Balance: %{y} USD<extra></extra>', #y:.2f
            marker_color = '#2BB1BB',
        ), secondary_y=True,  # fill down to xaxis
    )
    #fig.update_traces(hovertemplate = 'Difference: %{y}<extra></extra>', #y:.2f)
    fig.update_layout(
        title="<b>"+chart_title+"<b>", #plot_bgcolor='rgb(255, 255, 255)',
        hovermode="x", template = "simple_white",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=600
    )
    fig.update_xaxes(title_text="", type='date', rangeslider_visible=True)
    fig.update_yaxes(title_text="BTC", secondary_y=False)
    fig.update_yaxes(title_text="USD", secondary_y=True)
    #if file_save:
    #    fig.write_html(fig_name)
    return fig

def balance_diff(data, btc_data, chart_title = '', fig_name='chart.html', file_save=False):
    data['diff_neg_pos'] = data['Amount'].map(lambda x: 'neg' if x<0 else 'pos')

    # Create main chart with 2 y axis
    subfig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar chart for Balance difference
    fig = px.bar(
        data, x='timestamp_date', y='Amount', color="diff_neg_pos",
        color_discrete_map = {'neg': '#F63366', 'pos': '#2BB1BB'}
    )
    names = cycle(['Positive change', 'Negative change'])
    fig.for_each_trace(lambda t:  t.update(name = next(names)))

    # Line chart for BTC price
    fig2 = px.line(btc_data, x='Date', y='Closing Price (USD)')
    fig2.update_traces(yaxis="y2", line=dict(width=2, color='#E4D00A'), name = 'Bitcoin price')

    # Update 2 charts into the main chart
    subfig.add_traces(fig.data + fig2.data)
    subfig.update_xaxes(title_text="", rangeslider_visible=True) #, type='date')
    subfig.layout.yaxis.title="Balance change (BTC)"
    subfig.layout.yaxis2.title="Bitcoin Price (USD)"
    subfig.update_traces(
        showlegend=True,
        hovertemplate = 'Change: %{y} BTC<extra></extra>', #y:.2f
    )
    subfig.update_layout(
        title="<b>"+chart_title+"<b>", #plot_bgcolor='rgb(255, 255, 255)',
        hovermode="x", template = "none",
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
    )

    #if file_save:
    #    subfig.write_html(fig_name)

    return subfig
