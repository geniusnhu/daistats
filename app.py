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
import PIL.Image
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

result_path = path+'/daistats_images/'

if args['streamlit']:
    st.set_page_config(
        page_title="DAISTATS status",
        page_icon="🚀", layout="wide",initial_sidebar_state='auto'
    )
    hide_streamlit_style = """
            <style>
            footer {
	        visibility: hidden;
	            }
            footer:after {
	            content:'© 2021 Nhu Hoang. Powered by Streamlit';
	            visibility: visible;
	            display: block;
	            position: relative;
	            #background-color: red;
	            padding: 5px;
	            top: 2px;
                    }
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.image(PIL.Image.open("title_img.png"), use_column_width=False)
    st.subheader("""
        Tracking the movement of &nbsp[![MAKER](https://img.shields.io/static/v1?label=Oasis&message=MakerDao&color=fda300&logo=MakerBot&style=for-the-badge)](https://oasis.app/) vaults.
        With data obtained from [DaiStats](https://daistats.com)
    """)
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

st.markdown("---")

#===============================================================#
# SELECT VAULT AND IN-DEPT MOVEMENT
#===============================================================#
# Create drop down bar -----------------------------------------
sorted_vaults = data.groupby('vault_name')['current_loan'].sum()\
    .sort_values(ascending=False).index

st.markdown("# **IN-DEPT MOVEMENT**")
st.markdown("### Choose one or several vaults below and explore In-dept movement")
st.markdown("### **Select Vault**")

sorted_vault = st.multiselect(
    'Choose one or several vaults for in-dept performance', sorted_vaults, default=['ETH-A'],
)

# Filter df based on selection---------------------------------
vault_df = data[data['vault_name'].isin(sorted_vault)]
vault_df['timestamp_date'] = vault_df['timestamp'].map(lambda x: str(x).split(' ')[0])
# Get the last data of the date
vault_df= vault_df.sort_values(by = 'timestamp').groupby('timestamp_date').first().reset_index()

if len(sorted_vault) == 0:
    st.success("No vault chosen. Please choose a vault name above !")
else:
    if len(sorted_vault) == 1:
        st.markdown(f"### Current vault fee: " +\
                    f"{vault_df.loc[vault_df['timestamp_date']==np.max(vault_df['timestamp_date']),'fee'].values[0]}")

    else:
        #vault_df = vault_df.groupby(['vault_name','timestamp_date']).mean().reset_index(drop=False)
        vault_df = vault_df.groupby('timestamp_date').sum().reset_index(drop=False)

    # Plot figures ------------------------------------------------
    col1, col2 = st.columns(2)

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
            with st.expander("See explanation"):
                st.markdown("""
                    Net Change in amount of coin(s) locked vs previous period.

                    When choosing several vaults at the same time,
                    the number might observe some unusual fluctuation due to the difference in vault updated timestamp.

                    It is recommended to see one vault data at a time.
                    """)

st.markdown("---")

#===============================================================#
# RICH WALLET MOVEMENT
#===============================================================#

st.markdown("# 🐳 **RICH WALLET MOVEMENT** 🐳")
#st.markdown("### Movement of the third richest Bitcoin wallet. Source data on [bitinfocharts](https://bitinfocharts.com/bitcoin/address/1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ)")
st.markdown("""
    ### Movement of the third richest Bitcoin wallet.
    Source data on &nbsp[![bitinfocharts](https://img.shields.io/static/v1?label=Bitinfocharts&message=Source&color=fda300&logo=Bitcoin&style=for-the-badge)](https://bitinfocharts.com/bitcoin/address/1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ)
""")
st.write('')

# Load data
data_wallet = pd.read_csv('rich_wallet.csv')
data_wallet['timestamp_date'] = data_wallet['timestamp'].map(lambda x: str(x).split(' ')[0])
# Load BTC price data
btc_data = pd.read_csv('BTC_price.csv')
btc_data = btc_data[btc_data['Date']>=data_wallet['timestamp_date'].min()]

# DCA price
DCA_price = data_wallet['Amount'] * data_wallet['Realized price']
DCA_price = round(DCA_price.sum()/data_wallet.loc[0,'Balance'], 2)
st.markdown(f"### DCA price: ${DCA_price:,}")

# Plot figures ------------------------------------------------
# TOTAL BALANCE------------------------------------------------
def get_final(x):
    x = x[0]
    return x

data = data_wallet.groupby('timestamp_date').agg(
    {'Amount': 'sum', 'Realized price': 'mean', 'Balance': 'first'}
).reset_index(drop=False)
data['Balance USD'] = data['Balance'] * data['Realized price']
data = data.dropna()
data['timestamp_date'] = pd.DatetimeIndex(data['timestamp_date'])

fig3 = wallet_movement_chart(
    data=data, chart_title = '', fig_name=result_path + "rich_wallet_balance.html",
    file_save=args['fig_save']
)
if args['streamlit']:
    st.markdown("## Wallet balance")
    st.plotly_chart(fig3, use_container_width=True)
else:
    pass

# CHANGE IN BALANCE---------------------------------------------
# if args['streamlit']:
#     st.markdown("## Changes in balance")
#
# col3, _ = st.columns(2)
#
# with col3:
#     DT = ('Date', "Week",'Month', 'Year')
#     DT_option = col3.selectbox(label = 'CHOOSE RESOLUTION', options = DT, index=0, help='Balance data is accumulated by selected resolution')
#
# if DT_option == 'Month':
#     data_diff = data.copy()
#     data_diff['timestamp_date'] = pd.DatetimeIndex(data_diff['timestamp_date'].dt.strftime('%m-%Y'))
#     data_diff = data_diff.groupby('timestamp_date').sum().reset_index(drop=False)
#     data_diff = data_diff[(data_diff['Amount']>=0.1) | (data_diff['Amount']<=-0.1)]
# elif DT_option == 'Year':
#     data_diff = data.copy()
#     data_diff['timestamp_date'] = pd.DatetimeIndex(data_diff['timestamp_date'].dt.strftime('%Y'))
#     data_diff = data_diff.groupby('timestamp_date').sum().reset_index(drop=False)
#     data_diff = data_diff[(data_diff['Amount']>=0.1) | (data_diff['Amount']<=-0.1)]
# elif DT_option == 'Week':
#     data_diff = data.copy()
#     data_diff['timestamp_date'] = data_diff['timestamp_date'].dt.strftime('%Y-%W').map(lambda x: process(x))
#     data_diff = data_diff.groupby('timestamp_date').sum().reset_index(drop=False)
#     data_diff = data_diff[(data_diff['Amount']>=0.1) | (data_diff['Amount']<=-0.1)]
# else:
#     data_diff = data.copy(
#     data_diff = data_diff[(data_diff['Amount']>=0.1) | (data_diff['Amount']<=-0.1)]
#
# fig4 = balance_diff(
#     data_diff, btc_data, chart_title = '',
#     fig_name=result_path + "wallet_diff.html",
#     file_save=args['fig_save']
# )
#
# if args['streamlit']:
#     st.plotly_chart(fig4, use_container_width=True)

# BTC VOLUME VS PRICE ---------------------------------------------
fig5, fig6 = bitcoin_price_volume(btc_data)

if args['streamlit']:
    st.plotly_chart(fig5, use_container_width=True)
    st.plotly_chart(fig6, use_container_width=True)

st.subheader("About this app")
st.markdown("""
Made and maintained by &nbsp[![Nhu Hoang](https://img.shields.io/static/v1?label=&message=Nhu%20Hoang&color=1f4762&logo=Netlify)](https://geniusnhu.netlify.app/)

Take a look at the &nbsp[![Source code](https://img.shields.io/static/v1?label=GitHub&message=Source%20code&color=fda300&logo=GitHub&?logoColor=1f4762)](https://github.com/geniusnhu/daistats)
""")

#https://img.shields.io/badge/-Source_code-1f4762&?style=social&logo=GitHub
