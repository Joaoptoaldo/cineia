import os
import csv
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

import streamlit as st
import google.generativeai as genai

# Configuração da página (DEVE ser o primeiro comando Streamlit)
st.set_page_config(page_title="CineIA", page_icon="🎬")

# Carregar variáveis do arquivo .env na raiz do projeto
# procura por .. / .env a partir deste arquivo (app/app.py)
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(dotenv_path=env_path)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEEDBACK_CSV = PROJECT_ROOT / "feedback.csv"

# --- CONFIGURAÇÃO DA API ---
# Se for publicar na Web é essencial proteger a CHAVE.
# Nunca publique com as Chaves Secretas diretamente no código do app.
# Uma das formas de proteger a chave é utilizar `st.secrets` no Streamlit:
# genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
CHAVE_API = os.getenv("GOOGLE_API_KEY", "SUA_CHAVE_AQUI")  # Gere no Google AI Studio
genai.configure(api_key=CHAVE_API)

# Os modelos são alterados frequentemente pelo Google, então deixamos configurável
NOME_MODELO = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
model = genai.GenerativeModel(NOME_MODELO)


def exibir_erro_api(erro: Exception) -> None:
	texto = str(erro)
	texto_lower = texto.lower()
	if "429" in texto_lower or "quota" in texto_lower or "rate limit" in texto_lower:
		st.error(
			"A chave está sendo lida, mas o projeto ficou sem cota para chamadas à API. "
			"Verifique billing/plano no Google AI Studio ou troque para um projeto com quota ativa."
		)
		
	else:
		st.error(f"Erro ao conectar com a IA: {erro}")


def eh_erro_de_quota(erro: Exception) -> bool:
	texto_lower = str(erro).lower()
	return "429" in texto_lower or "quota" in texto_lower or "rate limit" in texto_lower


def sugestoes_locais(generos: list[str], tempo_maximo: int, mood: str) -> str:
	base = [
		("Interestelar", 2014, "ficção científica emocional e visualmente forte"),
		("A Origem", 2010, "reviravoltas e tensão psicológica"),
		("Que Horas Ela Volta?", 2015, "drama humano com ótima atuação"),
		("Parasita", 2019, "mistura de suspense, crítica social e surpresa"),
		("Divertida Mente", 2015, "leve, inteligente e ótima para vários humores"),
		("O Poço", 2019, "intenso e mais sombrio"),
	]
	
	texto_generos = ", ".join(generos) if generos else "qualquer gênero"
	linhas = [
		"Sugestões locais baseadas no seu pedido:",
		f"- Gêneros: {texto_generos}",
		f"- Duração máxima: {tempo_maximo} minutos",
		f"- Clima informado: {mood}",
		"",
	]
	
	for titulo, ano, motivo in base[:3]:
		linhas.append(f"- {titulo} ({ano}) — {motivo}")
	return "\n".join(linhas)


def registrar_feedback(mood: str, generos: list[str], tempo: int, feedback: str) -> None:
	criar_cabecalho = not FEEDBACK_CSV.exists()
	with FEEDBACK_CSV.open("a", newline="", encoding="utf-8") as arquivo:
		writer = csv.writer(arquivo)
		if criar_cabecalho:
			writer.writerow(["timestamp", "mood", "genero", "tempo", "feedback"])
		writer.writerow([
			datetime.now().isoformat(timespec="seconds"),
			mood,
			" | ".join(generos) if generos else "",
			tempo,
			feedback,
		])

# --- INTERFACE ---
st.title("CineIA: Seu Próximo Filme 🎬")
st.markdown("Descubra filmes baseados no seu estado de espírito atual.")

with st.sidebar:
	st.header("Preferências")
	genero = st.multiselect(
		"Gêneros favoritos:",
		["Ação", "Drama", "Sci-Fi", "Comédia", "Terror", "Documentário"]
	)
	tempo = st.slider("Duração máxima (minutos):", 60, 240, 120)

	# Text area movido para a barra lateral para organizar melhor o layout
	mood = st.text_area(
		"Descreva como você está se sentindo ou o que busca no filme:",
		placeholder="Ex: Quero um filme de ficção científica com reviravoltas na história."
	)

	botao_recomendar = st.button("Buscar Recomendações")
	

# --- LÓGICA DE PROCESSAMENTO ---
if botao_recomendar:
	if not mood:
		st.warning("Por favor, descreva o que você deseja assistir!")
	else:
		with st.spinner("Analisando catálogo cinematográfico..."):
			# Tratamento de gêneros caso o usuário não selecione nenhum
			generos_str = ', '.join(genero) if genero else 'qualquer gênero'

			prompt = f"""Você é um especialista em cinema.
                        Recomende 3 filmes para alguém que gosta de {generos_str} e que durem até {tempo} minutos.
                        O usuário descreveu o clima do filme como: '{mood}'.
                        Para cada filme, forneça: Título, Ano e uma frase curta do porquê combina com o pedido.
                        """

			try:
				response = model.generate_content(prompt)
				st.success("Aqui estão minhas sugestões:")
				st.markdown("---")
				st.write(response.text)
				st.session_state["rlhf_context"] = {
					"mood": mood,
					"genero": genero,
					"tempo": tempo,
				}
			except Exception as e:
				if eh_erro_de_quota(e):
					st.info("A IA está indisponível agora. Vou usar sugestões locais para continuar te ajudando.")
					st.markdown(sugestoes_locais(genero, tempo, mood))
					st.session_state["rlhf_context"] = {
						"mood": mood,
						"genero": genero,
						"tempo": tempo,
					}
				else:
					exibir_erro_api(e)

if "rlhf_context" in st.session_state:
	st.markdown("---")
	st.subheader("Seu feedback ajuda a melhorar as recomendações")
	col1, col2 = st.columns(2)
	with col1:
		if st.button("Gostei", use_container_width=True):
			ctx = st.session_state["rlhf_context"]
			registrar_feedback(ctx["mood"], ctx["genero"], ctx["tempo"], "Gostei")
			st.success("Obrigado pelo seu feedback positivo!")
	with col2:
		if st.button("Não gostei", use_container_width=True):
			ctx = st.session_state["rlhf_context"]
			registrar_feedback(ctx["mood"], ctx["genero"], ctx["tempo"], "Não gostei")
			st.info("Feedback registrado. Vamos melhorar!")

st.markdown("---")
st.caption(
	"Projeto de Demonstração para Google Generative AI"
)
