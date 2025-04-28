
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --------------- PREPARAÇÃO DOS DADOS ---------------

df = pd.read_excel("Dados.xlsx")

df = df.rename(columns=lambda x: x.strip())  # Corrige espaços nos nomes de colunas

df['Margem rentabilidade'] = df['Margem rentabilidade']*100
df['Tempo de Contrato'] = round((df['Data de Vencimento'] - df['Data de Assinatura']).dt.days / 365.25)
df['Previsão de Rentabilidade'] = df['Margem rentabilidade'].apply(lambda x: 'Positiva' if x >= 0 else 'Negativa')

# --------------- STREAMLIT APP ---------------

st.set_page_config(page_title="Dashboard Escolas", layout="wide")

# CSS personalizado
st.markdown("""
    <style>
    .stMultiSelect > div > div > div > div {
        color: #270ffc !important;
        border-radius: 8px !important;
    }
    button[kind="primary"] {
        background-color: #270ffc !important;
        color: white !important;
    }
    button[kind="primary"]:hover {
        background-color: #270ffc !important;
        color: white !important;
    }
    .stDownloadButton > button {
        background-color: #270ffc !important;
        color: white !important;
    }
    .stDownloadButton > button:hover {
        background-color: #270ffc !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Dashboard Estratégico")

# --- SIDEBAR FILTROS ---
with st.sidebar:
    st.header("Filtros 🔍")

    with st.expander("📊 Filtros Principais"):
        lideres_disponiveis = sorted(df['Líder'].unique())
        lideres_selecionados = st.multiselect('Líderes:', lideres_disponiveis, default=lideres_disponiveis)

        status_selecionados = st.multiselect('Status da Parceria:', ['Ativa', 'Encerrada'], default=['Ativa', 'Encerrada'])

        tempo_disponivel = sorted(df['Tempo de Contrato'].dropna().unique())
        tempo_selecionado = st.multiselect('Tempo de Contrato (anos):', tempo_disponivel, default=tempo_disponivel)

        rentabilidade_selecionada = st.multiselect('Previsão de Rentabilidade:', ['Positiva', 'Negativa'], default=['Positiva', 'Negativa'])

    if st.button('🔄 Resetar Filtros'):
        lideres_selecionados = lideres_disponiveis
        status_selecionados = ['Ativa', 'Encerrada']
        tempo_selecionado = tempo_disponivel
        rentabilidade_selecionada = ['Positiva', 'Negativa']

# --- FILTRAGEM DOS DADOS ---
df_filtrado = df[
    (df['Líder'].isin(lideres_selecionados)) &
    (df['Status da Parceria'].isin(status_selecionados)) &
    (df['Tempo de Contrato'].isin(tempo_selecionado)) &
    (df['Previsão de Rentabilidade'].isin(rentabilidade_selecionada))
]

# --- PRIMEIRA LINHA DE GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    # --- Gráfico 1: Escolas por Líder (Ativa/Encerrada) ---
    df_lideres = df_filtrado.groupby(['Líder', 'Status da Parceria']).size().unstack(fill_value=0)
    df_lideres['Total'] = df_lideres.sum(axis=1)
    df_lideres = df_lideres.sort_values(by='Total', ascending=False)

    fig1 = go.Figure()

    # Adicionar Encerrada primeiro (vermelho)
    if 'Encerrada' in df_lideres.columns:
        fig1.add_trace(go.Bar(
            x=df_lideres.index,
            y=df_lideres['Encerrada'],
            name='Encerrada',
            marker_color='#fa3e3e',
            text=[f"{(v/t)*100:.0f}%" if t > 0 else "" for v, t in zip(df_lideres['Encerrada'], df_lideres['Total'])],
            textposition='inside',
            textfont_size=16
        ))

    # Depois Ativa (verde)
    if 'Ativa' in df_lideres.columns:
        fig1.add_trace(go.Bar(
            x=df_lideres.index,
            y=df_lideres['Ativa'],
            name='Ativa',
            marker_color='#10c759',
            text=[f"{(v/t)*100:.0f}%" if t > 0 else "" for v, t in zip(df_lideres['Ativa'], df_lideres['Total'])],
            textposition='inside',
            textfont_size=16
        ))

    fig1.update_layout(
        barmode='stack',
        title='📊 Escolas por Líder (Status)',
        xaxis_title='Líder',
        yaxis_title='Número de Escolas',
        height=500
    )

    st.plotly_chart(fig1, use_container_width=True)

with col2:
    # --- Gráfico 2: Escolas por Tempo de Contrato e Rentabilidade ---
    df_rentabilidade = df_filtrado.groupby(['Tempo de Contrato', 'Previsão de Rentabilidade']).size().unstack(fill_value=0)
    df_rentabilidade['Total'] = df_rentabilidade.sum(axis=1)

    fig2 = go.Figure()

    # Adicionar Negativa primeiro (vermelho)
    if 'Negativa' in df_rentabilidade.columns:
        fig2.add_trace(go.Bar(
            x=df_rentabilidade.index,
            y=df_rentabilidade['Negativa'],
            name='Rentabilidade Negativa',
            marker_color='#fa3e3e',
            text=[f"{(v/t)*100:.0f}%" if t > 0 else "" for v, t in zip(df_rentabilidade['Negativa'], df_rentabilidade['Total'])],
            textposition='inside',
            textfont_size=16
        ))

    # Depois Positiva (verde)
    if 'Positiva' in df_rentabilidade.columns:
        fig2.add_trace(go.Bar(
            x=df_rentabilidade.index,
            y=df_rentabilidade['Positiva'],
            name='Rentabilidade Positiva',
            marker_color='#10c759',
            text=[f"{(v/t)*100:.0f}%" if t > 0 else "" for v, t in zip(df_rentabilidade['Positiva'], df_rentabilidade['Total'])],
            textposition='inside',
            textfont_size=16
        ))

    fig2.update_layout(
        barmode='stack',
        title='📈 Escolas por Tempo de Contrato e Rentabilidade',
        xaxis_title='Tempo de Contrato (anos)',
        yaxis_title='Número de Escolas',
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)

# --- SEGUNDA LINHA DE GRÁFICOS ---
col3, col4 = st.columns(2)

with col3:
    # --- Gráfico 3: Rentabilidade Média por Líder ---
    df_lideres_rentabilidade_media = df_filtrado.groupby('Líder')['Margem rentabilidade'].mean().reset_index()
    df_lideres_rentabilidade_media = df_lideres_rentabilidade_media.sort_values(by='Margem rentabilidade', ascending=False)

    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        x=df_lideres_rentabilidade_media['Líder'],
        y=df_lideres_rentabilidade_media['Margem rentabilidade'],
        marker_color=['#10c759' if x >= 0 else '#fa3e3e' for x in df_lideres_rentabilidade_media['Margem rentabilidade']],
        text=[f"{x:.2f}%" for x in df_lideres_rentabilidade_media['Margem rentabilidade']],
        textposition='inside',
        textfont_size=16
    ))

    fig3.update_layout(
        title='📉 Rentabilidade Média por Líder',
        xaxis_title='Líder',
        yaxis_title='Rentabilidade Média (%)',
        height=500
    )

    st.plotly_chart(fig3, use_container_width=True)

with col4:
    # --- Gráfico 4: Distribuição da Margem de Rentabilidade ---
    fig4 = px.histogram(
        df_filtrado,
        x='Margem rentabilidade',
        nbins=20,
        title='📈 Distribuição da Margem de Rentabilidade',
        color_discrete_sequence=['#270ffc']
    )

    fig4.update_layout(
        xaxis_title='Margem de Rentabilidade (%)',
        yaxis_title='Número de Escolas',
        height=500
    )

    st.plotly_chart(fig4, use_container_width=True)

# --- TERCEIRA LINHA DE GRÁFICOS ---
col5 = st.columns(1)[0]

with col5:
    # --- Gráfico 5: Top Escolas por Rentabilidade ---
    top_escolas = df_filtrado[['Nome da Escola', 'Margem rentabilidade']].sort_values(by='Margem rentabilidade', ascending=True)

    fig5 = go.Figure()

    fig5.add_trace(go.Bar(
        x=top_escolas['Margem rentabilidade'],
        y=top_escolas['Nome da Escola'],
        orientation='h',
        marker_color=['#fa3e3e' if x < 0 else '#10c759' for x in top_escolas['Margem rentabilidade']],
    ))

    fig5.update_layout(
        title='🏆 Escolas com Maior/Menor Rentabilidade',
        xaxis_title='Margem de Rentabilidade (%)',
        yaxis_title='Nome da Escola',
        height=500,
        yaxis={'categoryorder':'total ascending'}
    )

    st.plotly_chart(fig5, use_container_width=True)

# --------------- DOWNLOAD DOS DADOS FILTRADOS ---------------
# with st.expander("📥 Baixar Dados Filtrados"):
#     csv = df_filtrado.to_csv(index=False).encode('utf-8')
#     st.download_button(
#         label="Baixar CSV Filtrado",
#         data=csv,
#         file_name='dados_filtrados.csv',
#         mime='text/csv',
#     )
