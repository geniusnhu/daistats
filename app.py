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

data = pd.read_csv(path+'/daistats_data.csv')

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
fig1.write_html(result_path + "vault_ratio.html")
if args['streamlit']:
    st.markdown('## **OVERVIEW**')
    st.plotly_chart(fig1)

st.markdown("--")
#---------------------------------------------------------------#
# SELECT VAULT AND SETUP DATA
#---------------------------------------------------------------#
# Create drop down bar -----------------------------------------
sorted_vaults = data.groupby('vault_name')['current_loan'].sum()\
    .sort_values(ascending=False).index

st.markdown("## **Select Vault:**")
sorted_vault = st.multiselect('', sorted_vaults, default=['ETH-A'])
#sorted_vault = []
#sorted_vault.append(st.selectbox('', sorted_vaults))

# Filter df based on selection---------------------------------
vault_df = data[data['vault_name'].isin(sorted_vault)]
vault_df['timestamp_date'] = vault_df['timestamp'].map(lambda x: str(x).split(' ')[0])

if len(sorted_vault) == 1:
    st.markdown(f"### Current fee: " +\
                f"{vault_df.loc[vault_df['timestamp_date']==np.max(vault_df['timestamp_date']),'fee'].values[0]}")
else:
    vault_df = data[data['vault_name'].isin(sorted_vault)].groupby('timestamp').sum().reset_index(drop=False)
    vault_df['timestamp_date'] = vault_df['timestamp'].map(lambda x: str(x).split(' ')[0])

st.markdown(f"### Selected vault(s): {', '.join([i for i in sorted_vault])}")

# Plot figures ------------------------------------------------
col1, col2 = st.beta_columns(2)

fig2 = movement_chart(
    data=vault_df, chart_title = 'Loan amount in USD', fig_name=result_path + "USDC_loan.html",
    file_save=args['fig_save']
)
if args['streamlit']:
    with col1:
        st.plotly_chart(fig2, use_container_width=True)
else:
    pass

# Daily changes in coin locked vs the previous day
fig4 = coin_diff(
    vault_df, chart_title = 'Changes in coin locked amount',
    fig_name=result_path + "ETHA_daily_diff.html",
    file_save=args['fig_save']
)
if args['streamlit']:
    with col2:
        st.plotly_chart(fig4, use_container_width=True)
        with st.beta_expander("See explanation"):
            st.write("""
                Net Change in amount of coin locked.

                *Note that data of different vaults might not be updated with the same timestamp*
                """)
