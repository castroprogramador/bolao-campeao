import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Bolão Campeão 🇧🇷", page_icon="⚽", layout="centered")

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

# --- ÁREA DE APOSTAS (Agora sem o st.form para ser dinâmico) ---
st.subheader("⚽ Faça sua Aposta")

nome = st.text_input("Seu Nome")

# Placar no tempo normal
col_br, col_op = st.columns(2)
placar_br = col_br.number_input("Gols do Brasil 🇧🇷", min_value=0, step=1)
placar_op = col_op.number_input("Gols da Noruega 🇳🇴", min_value=0, step=1)

st.markdown("---")

# Sistema de Pênaltis dinâmico
tem_penaltis = st.checkbox("O jogo vai para os pênaltis? 🥅")

pen_br = 0
pen_op = 0

if tem_penaltis:
    col_pen_br, col_pen_op = st.columns(2)
    pen_br = col_pen_br.number_input("Pênaltis - Brasil 🇧🇷", min_value=0, step=1)
    pen_op = col_pen_op.number_input("Pênaltis - Noruega 🇳🇴", min_value=0, step=1)

st.markdown("---")

valor = st.number_input("Valor da Aposta (R$)", min_value=5.0, step=5.0)

# Botão de registro isolado
if st.button("Registrar Aposta"):
    if nome == "":
        st.warning("Por favor, preencha seu nome!")
    elif tem_penaltis and placar_br != placar_op:
        st.warning("Atenção: O jogo só vai para os pênaltis se o placar normal terminar empatado! Arrume o placar normal antes de apostar.")
    else:
        # Verifica se a pessoa já apostou 2 vezes
        if 'Nome' in df_apostas.columns and not df_apostas.empty:
            apostas_feitas = len(df_apostas[df_apostas['Nome'].astype(str).str.lower() == nome.lower()])
        else:
            apostas_feitas = 0
        
        if apostas_feitas >= 2:
            st.error(f"Atenção {nome}: Você já atingiu o limite de 2 apostas por pessoa!")
        else:
            # Salva tudo de uma vez só na ordem certa
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
            
            st.success(f"Aposta de {nome} registrada com sucesso! Veja as instruções de pagamento abaixo.")

st.divider()

# --- PAGAMENTO VIA PIX ---
st.subheader("💸 Pagamento via PIX")
st.info("Para validar sua aposta, realize o PIX do valor escolhido e envie o comprovante no WhatsApp.")
st.code("Chave PIX (Celular): 47989037463", language="text")

st.divider()

# --- TABELA DE APOSTAS ---
st.subheader("📊 Apostas Registradas")
if df_apostas.empty:
    st.write("Nenhuma aposta feita ainda. Seja o primeiro!")
else:
    st.dataframe(df_apostas, hide_index=True, use_container_width=True)

st.divider()

# --- RODAPÉ COM REGRAS E CONTATO (Letras Pequenas) ---
st.caption("📌 **REGRAS DO BOLÃO:** Cada pessoa pode fazer até **duas apostas**. Caso mais de uma pessoa acerte o placar exato, o prêmio acumulado será dividido em partes iguais. Caso ninguém acerte, 40% do valor fica para a casa e os 60% restantes acumularão para o próximo jogo.")

st.caption("📞 **CONTATO:** Criador: Davi Castro | WhatsApp: (47) 98903-7463")