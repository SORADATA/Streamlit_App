import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf

st.title('S&P 500 App')

st.markdown("""
This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn
* **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# ✅ Mise à jour : Remplacement de @st.cache par @st.cache_data
@st.cache_data
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header=0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = df[df['GICS Sector'].isin(selected_sector)]

st.header('Display Companies in Selected Sector')
st.write(f'Data Dimension: {df_selected_sector.shape[0]} rows and {df_selected_sector.shape[1]} columns.')
st.dataframe(df_selected_sector)

# ✅ Amélioration : Encodage CSV robuste
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

# ✅ Vérifier si la DataFrame n'est pas vide avant d'utiliser yfinance
if not df_selected_sector.empty:
    data = yf.download(
        tickers=list(df_selected_sector[:10].Symbol),
        period="ytd",
        interval="1d",
        group_by='ticker',
        auto_adjust=True,
        prepost=True,
        threads=True,
        proxy=None
    )

    # ✅ Correction : Ajout de plt.gcf() pour bien afficher les graphiques
    def price_plot(symbol):
        df_plot = pd.DataFrame(data[symbol].Close)
        df_plot['Date'] = df_plot.index
        plt.fill_between(df_plot.Date, df_plot.Close, color='skyblue', alpha=0.3)
        plt.plot(df_plot.Date, df_plot.Close, color='skyblue', alpha=0.8)
        plt.xticks(rotation=90)
        plt.title(symbol, fontweight='bold')
        plt.xlabel('Date', fontweight='bold')
        plt.ylabel('Closing Price', fontweight='bold')
        st.pyplot(plt.gcf())

    num_company = st.sidebar.slider('Number of Companies', 1, 5)

    if st.button('Show Plots'):
        st.header('Stock Closing Price')
        for i in list(df_selected_sector.Symbol)[:num_company]:
            price_plot(i)
