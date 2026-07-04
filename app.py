import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Bolão Campeão 🇧🇷", page_icon="⚽", layout="centered")

# --- BARRA LATERAL (CONTATO E REGRAS) ---
with st.sidebar:
    st.header("📌 Avisos e Regras")
    st.markdown("""
    * **Limite:** Cada pessoa pode fazer até **duas apostas**.
    * **Empate:** Caso mais de uma pessoa acerte, o prêmio acumulado será dividido em partes iguais.
    * **Sem ganhadores:** Caso ninguém acerte o placar, 40% do valor fica para a casa e os 60% restantes acumularão para o próximo jogo!
    """)
    
    st.divider()
    
    st.header("📞 Contato")
    st.markdown("**Criador:** Davi Castro")
    st.markdown("**WhatsApp:** (47) 98903-7463")

# --- CABEÇALHO PRINCIPAL ---
st.title("🏆 Bolão Campeão - Brasil!")
st.write("Faça sua aposta, realize o PIX e concorra ao prêmio acumulado!")

# 1. Cria a conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Lê os dados da planilha
try:
    df_apostas = conn.read(worksheet="Página1", ttl=0)
    df_apostas = df_apostas.dropna(how="all")
except Exception as e:
    st.error("Erro ao conectar com a planilha. Verifique os Secrets no Streamlit.")
    st.stop()

# Garante que a coluna de valor é um número para somar
df_apostas['Valor (R$)'] = pd.to_numeric(df_apostas['Valor (R$)'], errors='coerce').fillna(0)
total_arrecadado = df_apostas['Valor (R$)'].sum()

# --- MÉTRICAS DO PRÊMIO ---
col1, col2 = st.columns(2)
col1.metric("Prêmio Acumulado", f"R$ {total_arrecadado:.2f}")
col2.metric("Total de Apostas", len(df_apostas))

st.divider()

# --- FORMULÁRIO DE APOSTAS ---
st.subheader("⚽ Faça sua Aposta")
with st.form("nova_aposta", clear_on_submit=True):
    nome = st.text_input("Seu Nome")
    
    col_br, col_op = st.columns(2)
    placar_br = col_br.number_input("Gols do Brasil 🇧🇷", min_value=0, step=1)
    placar_op = col_op.number_input("Gols do Oponente 🏳️", min_value=0, step=1)
    
    valor = st.number_input("Valor da Aposta (R$)", min_value=5.0, step=5.0)
    
    submitted = st.form_submit_button("Registrar Aposta")
    
    if submitted:
        if nome == "":
            st.warning("Por favor, preencha seu nome!")
        else:
            # Conta quantas apostas essa pessoa já fez para aplicar a regra das 2 apostas
            apostas_feitas = len(df_apostas[df_apostas['Nome'].str.lower() == nome.lower()])
            
            if apostas_feitas >= 2:
                st.error(f"Atenção {nome}: Você já atingiu o limite de 2 apostas por pessoa!")
            else:
                nova_linha = pd.DataFrame([{
                    'Nome': nome, 
                    'Brasil': placar_br, 
                    'Oponente': placar_op, 
                    'Valor (R$)': valor
                }])
                
                df_atualizado = pd.concat([df_apostas, nova_linha], ignore_index=True)
                conn.update(worksheet="Página1", data=df_atualizado)
                
                st.success("Aposta registrada com sucesso na planilha!")
                st.rerun()

st.divider()

# --- PAGAMENTO VIA PIX ---
st.subheader("💸 Pagamento via PIX")
st.info("Para validar sua aposta, realize o PIX do valor escolhido e envie o comprovante no WhatsApp do criador (Davi).")
st.code("Chave PIX (Celular): 47989037463", language="text")

st.divider()

# --- TABELA DE APOSTAS ---
st.subheader("📊 Apostas Registradas")
if df_apostas.empty:
    st.write("Nenhuma aposta feita ainda. Seja o primeiro!")
else:
    st.dataframe(df_apostas, hide_index=True, use_container_width=True)