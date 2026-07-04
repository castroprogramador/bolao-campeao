import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Bolão do Brasil 🇧🇷", page_icon="⚽", layout="centered")

st.title("🏆 Bolão Campeão - Brasil!")
st.write("Faça sua aposta, realize o PIX e concorra ao prêmio acumulado!")

# Inicializando um "banco de dados" temporário na sessão
if 'apostas' not in st.session_state:
    st.session_state.apostas = pd.DataFrame(columns=['Nome', 'Brasil', 'Oponente', 'Valor (R$)'])

# --- MÉTRICAS DO PRÊMIO ---
# Calcula o total arrecadado com base nas apostas feitas
total_arrecadado = st.session_state.apostas['Valor (R$)'].sum()

col1, col2 = st.columns(2)
col1.metric("Prêmio Acumulado", f"R$ {total_arrecadado:.2f}")
col2.metric("Total de Apostas", len(st.session_state.apostas))

st.divider()

# --- FORMULÁRIO DE APOSTAS ---
st.subheader("⚽ Faça sua Aposta")
with st.form("nova_aposta"):
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
            # Adiciona a nova aposta ao nosso DataFrame
            nova_aposta = pd.DataFrame([{
                'Nome': nome, 
                'Brasil': placar_br, 
                'Oponente': placar_op, 
                'Valor (R$)': valor
            }])
            st.session_state.apostas = pd.concat([st.session_state.apostas, nova_aposta], ignore_index=True)
            st.success("Aposta registrada com sucesso! Veja as instruções de pagamento abaixo.")

st.divider()

# --- PAGAMENTO VIA PIX ---
# Para simplificar entre amigos, usamos uma chave estática.
st.subheader("💸 Pagamento via PIX")
st.info("Para validar sua aposta, realize o PIX do valor escolhido e envie o comprovante no WhatsApp do administrador.")
st.code("Sua Chave PIX Aqui (Ex: 47999999999)", language="text")

st.divider()

# --- TABELA DE APOSTAS ---
st.subheader("📊 Apostas Registradas")
if st.session_state.apostas.empty:
    st.write("Nenhuma aposta feita ainda. Seja o primeiro!")
else:
    # Exibe a tabela sem o índice numérico
    st.dataframe(st.session_state.apostas, hide_index=True, use_container_width=True)