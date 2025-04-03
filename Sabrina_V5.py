import streamlit as st
import pandasai as pai
import pandas as pd
import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

# Definindo o modelo
model = "ollama/llama3.1"

# Definindo a chave da API do Pandas AI
pai.api_key.set(PAI_API_KEY)

st.set_page_config(
    page_title="Sabrina",
    page_icon=":sparkles:",
    layout="centered"
)

st.title("Solvis - Innovative CX Solutions")

uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=";")
        df.columns = df.columns.str.replace(' ', '_')
        df['Horário'] = df['Horário'].map(lambda x: str(x).replace(" às ", "|"))
        df[['Data', 'Hora']] = df['Horário'].str.split('|', expand=True)
        df.drop('Horário', axis=1, inplace=True)
        df = df.map(lambda x: str(x).replace(" estrelas", ""))
        df = df.map(lambda x: str(x).replace(" estrela", ""))
        df = df.map(lambda x: str(x).replace("Não avaliar", ""))
        df = df.map(lambda x: str(x).replace("Não aceito", "0"))
        df = df.map(lambda x: str(x).replace("Aceito", "1"))
        df = df.map(lambda x: str(x).replace("Sim", "1"))
        df = df.map(lambda x: str(x).replace("Não", "0"))
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                pass  # Coluna contém dados não numéricos
        for col in df.columns:
            if "coment" in col.lower():
                comentarios = df[col].tolist()
        df = pai.DataFrame(df)
        st.write("Dados carregados com sucesso!")
        st.dataframe(df)

        user_question = st.text_input("Faça sua pergunta sobre os dados:")

        if user_question:
            # Palavras-chave para resumo e cálculo
            # É uma abordagem que funciona, mas seria interessante treinar um modelo de classificação
            # para interpretar a intenção do usuário. 
            resumo_keywords = ["resumo", "resuma", "sumarize", "principais pontos", "sentimentos", "opinião", "feedback"]
            calculo_keywords = ["média", "soma", "máximo", "mínimo", "desvio padrão", "calcular", "calcule", "total", "contar"]

            if any(keyword in user_question.lower() for keyword in resumo_keywords):
                descricao = "Seu nome é Sabrina e você é especialista em resumir comentários de clientes, elencando os principais aspectos positivos e negativos informados pelos clientes."
                contexto = f"{descricao} {comentarios}"
                response = completion(
                    model=model,
                    messages=[
                        {"role": "user", "content": user_question},
                        {"role": "system", "content": contexto},
                    ],
                    api_base="http://localhost:11434",
                )
                st.write(str(response.choices[0]['message']['content']))
            elif any(keyword in user_question.lower() for keyword in calculo_keywords):
                try:
                    resp = df.chat(user_question)
                    st.write("Resposta:")
                    st.write(resp)
                except Exception as e:
                    st.write(f"Ocorreu um erro: {e}")
            else:
                # Caso não se encaixe em nenhum, tenta com PandasAI
                try:
                    resp = df.chat(user_question)
                    st.write("Resposta:")
                    st.write(resp)
                except Exception as e:
                    st.write(f"Ocorreu um erro: {e}")

    except Exception as e:
        st.write(f"Erro ao processar o arquivo: {e}")

if st.button("Limpar Chat"):
    st.session_state.chat_history = []
