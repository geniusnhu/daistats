import pandas as pd
import numpy as np

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import tools
import plotly.offline as py
import plotly.express as px
from plotly.graph_objs import *


def summary_vault(data):
    #MAKE SUBPLOTS
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[1, 1],
        specs=[[{"secondary_y": True}, {"secondary_y": False}]],
        #subplot_titles=('Loan amount in USD', 'Changes in coin locked amount'),
        vertical_spacing=0.1, horizontal_spacing= 0.09)

    # SCATTER
    fig.add_trace(
        go.Scatter(
            x=data['timestamp_date'], y=data['current_loan'], name = 'Total loan (USD)',
            fill='tozeroy', hovertemplate = 'Loan amount: %{y}<extra></extra>', #y:.2f
            marker_color = '#F63366',
        ), secondary_y=False,  # fill down to xaxis
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=data['timestamp_date'], y=data['amount_coin_locked'], name = 'Total coin locked',
            fill='tozeroy', hovertemplate = 'Coin locked amount: %{y}<extra></extra>', #y:.2f
            marker_color = '#2BB1BB',
        ), secondary_y=True,  # fill down to xaxis
        row=1, col=1,
    )
    fig.update_xaxes(title_text="", row = 1, col = 1)
    fig.update_yaxes(title_text="Vault loan (USD)", secondary_y=False, row = 1, col = 1)
    fig.update_yaxes(title_text="Vault coin locked amount", secondary_y=True, row = 1, col = 1)

    # BAR
    data['amount_coin_diff'] = data['amount_coin_locked'].diff()
    data['diff_neg_pos'] = data['amount_coin_diff'].map(lambda x: 'neg' if x<0 else 'pos')
    color_dict = {'neg': '#F63366', 'pos': '#2BB1BB'}

    for t in data['diff_neg_pos'].unique():
        dfp = data[data['diff_neg_pos']==t]
        fig.add_trace(go.Bar(
            x=data['timestamp_date'], y = data['amount_coin_diff'],
            hovertemplate='Difference: %{y}<extra></extra>',
            marker_color = color_dict[t],
            showlegend=False
        ), row = 1, col = 2)
    # fig = px.bar(
    #     data, x='timestamp_date', y='amount_coin_diff', color="diff_neg_pos",
    #     color_discrete_map = {'neg': '#F63366', 'pos': '#2BB1BB'}
    # )

    fig.update_traces(
        showlegend=False,
        hovertemplate = 'Difference: %{y}<extra></extra>', #y:.2f
        row = 1, col = 2
    )

    fig.update_xaxes(title_text="", row = 1, col = 2)
    fig.update_yaxes(title_text="Amount of coin locked difference", row = 1, col = 2)
    fig.update_layout(plot_bgcolor='rgb(255, 255, 255)',hovermode="x", width=1500, height=500,)

    return fig



def movement_chart(data, chart_title = '', fig_name='chart.html', file_save=False):
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
    #fig.update_traces(hovertemplate = 'Difference: %{y}<extra></extra>', #y:.2f)
    fig.update_layout(
        title="<b>"+chart_title+"<b>", #plot_bgcolor='rgb(255, 255, 255)',
        hovermode="x", template = "simple_white",
    )
    fig.update_xaxes(title_text="") #, type='date')
    fig.update_yaxes(title_text="Vault loan (USD)", secondary_y=False)
    fig.update_yaxes(title_text="Vault coin locked amount", secondary_y=True)
    #if file_save:
    #    fig.write_html(fig_name)
    return fig

def coin_diff(data, chart_title = '', fig_name='chart.html', file_save=False):
    data['amount_coin_diff'] = data['amount_coin_locked'].diff()
    data['diff_neg_pos'] = data['amount_coin_diff'].map(lambda x: 'neg' if x<0 else 'pos')
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
    fig.update_xaxes(title_text="") #, type='date')
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

def balance_diff(data, chart_title = '', fig_name='chart.html', file_save=False):
    data['diff_neg_pos'] = data['Amount'].map(lambda x: 'neg' if x<0 else 'pos')
    fig = px.bar(
        data, x='timestamp_date', y='Amount', color="diff_neg_pos",
        color_discrete_map = {'neg': '#F63366', 'pos': '#2BB1BB'},
        height=600
    )

    fig.update_traces(
        showlegend=False,
        hovertemplate = 'Change: %{y} BTC<extra></extra>', #y:.2f
    )
    fig.update_layout(
        title="<b>"+chart_title+"<b>", #plot_bgcolor='rgb(255, 255, 255)',
        hovermode="x", template = "none",
    )
    fig.update_xaxes(title_text="", rangeslider_visible=True) #, type='date')
    fig.update_yaxes(title_text="BTC")
    #if file_save:
    #    fig.write_html(fig_name)

    return fig
