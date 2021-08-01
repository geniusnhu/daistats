import pandas as pd
import numpy as np
import argparse
#from tqdm import tqdm

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly import tools
import plotly.offline as py
import plotly.express as px

import os#, time
from utils import *

# Define arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--fig_save", default=False,
                help="Whether to save figure or not")
ap.add_argument("-s", "--streamlit", default=True,
                help="Whether to deplot on streamlit or not")
args = vars(ap.parse_args())
parent_dir = os.getcwd()
path = os.path.dirname(parent_dir) # Go up one level to the common parent directory
#sys.path.append(path)

#result_path = path+'/daistats_images/'
result_path = path+'/daistats_images/'

if args['streamlit']:
    st.set_page_config(
        page_title="DAISTATS status",
        page_icon="🚀", layout="wide",initial_sidebar_state='auto'
    )
    st.title("**✮** DaiStats Report **✮**")
    st.subheader("Status of [MAKER](https://oasis.app/) Vaults")
    st.markdown("Data is obtained from [DaiStats](https://daistats.com)")
else:
    pass

data = pd.read_csv('daistats_data.csv')

# ================== 1. Ratio by vault ==================
total_loan = data['current_loan'].sum()
portion = data.groupby('vault_name').agg({'current_loan': 'sum'}) / total_loan
portion = portion.reset_index()

fig1 = px.pie(
    portion,
    values=portion.current_loan,
    names=portion.vault_name,
    color=portion.vault_name,
)
fig1.update_traces(
    textposition='inside', textinfo='percent+label',
    hovertemplate=None
)
fig1.update_layout(title="<b>Ratio by vault</b>", hovermode="x unified")
#fig1.write_html(result_path + "vault_ratio.html")
if args['streamlit']:
    st.markdown('## **OVERVIEW**')
    st.plotly_chart(fig1)

st.markdown("--")

#===============================================================#
# SELECT VAULT AND IN-DEPT MOVEMENT
#===============================================================#
# Create drop down bar -----------------------------------------
sorted_vaults = data.groupby('vault_name')['current_loan'].sum()\
    .sort_values(ascending=False).index

st.markdown("# **IN-DEPT MOVEMENT**")
st.markdown("### Choose one or several vaults below and explore In-dept movement")
st.markdown("### **Select Vault:**")

sorted_vault = st.multiselect(
    'Choose one or several vaults in-dept performance', sorted_vaults, default=['ETH-A'],
    #help = 'Test help'
)

# Filter df based on selection---------------------------------
vault_df = data[data['vault_name'].isin(sorted_vault)]
vault_df['timestamp_date'] = vault_df['timestamp'].map(lambda x: str(x).split(' ')[0])

if len(sorted_vault) == 1:
    st.markdown(f"### Current vault fee: " +\
                f"{vault_df.loc[vault_df['timestamp_date']==np.max(vault_df['timestamp_date']),'fee'].values[0]}")
else:
    vault_df = vault_df.groupby(['vault_name','timestamp_date']).mean().reset_index(drop=False)
    vault_df = vault_df.groupby('timestamp_date').sum().reset_index(drop=False)

# Plot figures ------------------------------------------------
col1, col2 = st.beta_columns(2)

fig1 = movement_chart(
    data=vault_df, fig_name=result_path + "USDC_loan.html", chart_title = '',
    file_save=args['fig_save']
)
if args['streamlit']:
    with col1:
        col1.header('Vault loan amount')
        st.plotly_chart(fig1, use_container_width=True)
else:
    pass

# Daily changes in coin locked vs the previous day
fig2 = coin_diff(
    vault_df, chart_title = '',
    fig_name=result_path + "ETHA_daily_diff.html",
    file_save=args['fig_save']
)

if len(sorted_vault) == 1:
    coin = sorted_vault[0].split('-')[0]
else:
    coin = ', '.join(list(set([i.split('-')[0] for i in sorted_vault])))
if args['streamlit']:
    with col2:
        col2.header(f'Changes in {coin} locked')
        col2.subheader('')
        st.plotly_chart(fig2, use_container_width=True)
        with st.beta_expander("See explanation"):
            st.write("""
                Net Change in amount of coin(s) locked vs previous day. The illustrated number is the total number of coins regardless its difference in nature.

                *Note that data of different vaults might not be updated with the same timestamp*
                """)

#===============================================================#
# SELECT VAULT AND SETUP DATA
#===============================================================#

st.markdown("# 🐳 **RICH WALLET MOVEMENT** 🐳")
st.markdown("### Movement of the third richest Bitcoin wallet. Source data on [bitinfocharts](https://bitinfocharts.com/bitcoin/address/1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ)")
st.write('')

# Load data
data = pd.read_csv('rich_wallet.csv')
data['timestamp_date'] = data['timestamp'].map(lambda x: str(x).split(' ')[0])

# DCA price
DCA_price = data['Amount'] * data['Realized price']
DCA_price = round(DCA_price.sum()/data.loc[0,'Balance'], 2)
st.markdown(f"### DCA price: ${DCA_price:,}")

# Plot figures ------------------------------------------------

data = data.groupby('timestamp_date').agg({'Amount': 'sum', 'Realized price': 'mean'}).reset_index(drop=False)
data['Balance'] = data['Amount'].cumsum()
data['Balance USD'] = data['Balance'] * data['Realized price']
data = data.dropna()

fig3 = wallet_movement_chart(
    data=data, chart_title = '', fig_name=result_path + "rich_wallet_balance.html",
    file_save=args['fig_save']
)
if args['streamlit']:
    st.markdown("## Wallet balance")
    st.plotly_chart(fig3, use_container_width=True)
    # with col3:
    #     col3.header('Wallet balance')
    #     st.plotly_chart(fig3, use_container_width=True)
else:
    pass

# Drop date that has movement < 0.1 BTC
data_diff = data[(data['Amount']>=0.1) | (data['Amount']<=-0.1)]
fig4 = balance_diff(
    data_diff, chart_title = '',
    fig_name=result_path + "wallet_diff.html",
    file_save=args['fig_save']
)

if args['streamlit']:
    st.markdown("## Changes in balance")
    st.plotly_chart(fig4, use_container_width=True)
    # with col4:
    #     col4.header('Changes in balance')
    #     col4.subheader('')
    #     st.plotly_chart(fig4, use_container_width=True)
