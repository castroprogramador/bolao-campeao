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
    st.error(f"Erro ao conectar com a planilha: {e}")
    st.stop()

# Garante que a coluna de valor é um número para somar
if 'Valor (R$)' in df_apostas.columns:
    df_apostas['Valor (R$)'] = pd.to_numeric(df_apostas['Valor (R$)'], errors='coerce').fillna(0)
    total_arrecadado = df_apostas['Valor (R$)'].sum()
else:
    total_arrecadado = 0.0

# --- MÉTRICAS DO PRÊMIO ---
col1, col2 = st.columns(2)
col1.metric("Prêmio Acumulado", f"R$ {total_arrecadado:.2f}")
col2.metric("Total de Apostas", len(df_apostas))

st.divider()

# --- FORMULÁRIO DE APOSTAS ---
st.subheader("⚽ Faça sua Aposta")
with st.form("nova_aposta", clear_on_submit=True):
    nome = st.text_input("Seu Nome")
    
    # Placar no tempo normal
    col_br, col_op = st.columns(2)
    placar_br = col_br.number_input("Gols do Brasil 🇧🇷", min_value=0, step=1)
    placar_op = col_op.number_input("Gols da Noruega 🇳🇴", min_value=0, step=1)
    
    st.markdown("---")
    
    # Sistema de Pênaltis
    tem_penaltis = st.checkbox("O jogo vai para os pênaltis? 🥅")
    
    if tem_penaltis:
        col_pen_br, col_pen_op = st.columns(2)
        pen_br = col_pen_br.number_input("Pênaltis - Brasil 🇧🇷", min_value=0, step=1)
        pen_op = col_pen_op.number_input("Pênaltis - Noruega 🇳🇴", min_value=0, step=1)
    
    st.markdown("---")
    
    valor = st.number_input("Valor da Aposta (R$)", min_value=5.0, step=5.0)
    
    submitted = st.form_submit_button("Registrar Aposta")
    
    if submitted:
        if nome == "":
            st.warning("Por favor, preencha seu nome!")
        elif tem_penaltis and placar_br != placar_op:
            # Um pequeno aviso de lógica, mas não impede a aposta
            st.warning("Atenção: O jogo só vai para os pênaltis se o placar normal terminar empatado!")
        else:
            # CORREÇÃO DO ERRO: Usando .astype(str) para garantir que seja lido como texto
            if 'Nome' in df_apostas.columns and not df_apostas.empty:
                apostas_feitas = len(df_apostas[df_apostas['Nome'].astype(str).str.lower() == nome.lower()])
            else:
                apostas_feitas = 0
            
            if apostas_feitas >= 2:
                st.error(f"Atenção {nome}: Você já atingiu o limite de 2 apostas por pessoa!")
            else:
                # Prepara os dados da nova aposta
                nova_linha = pd.DataFrame([{
                    'Nome': nome, 
                    'Brasil': placar_br, 
                    'Noruega': placar_op, 
                    'Pênaltis?': 'Sim' if tem_penaltis else 'Não',
                    'Pên. Brasil': pen_br if tem_penaltis else '-',
                    'Pên. Noruega': pen_op if tem_penaltis else '-',
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