# CineIA

Aplicação em Streamlit para recomendar filmes com apoio da Gemini API, com fallback local quando a API estiver sem cota e registro simples de feedback do usuário em CSV.

## Funcionalidades

- Recomenda 3 filmes com base em gênero, duração máxima e estado de espírito.
- Usa a Gemini API quando houver cota disponível.
- Exibe sugestões locais quando a API estiver indisponível.
- Registra feedback do tipo "Gostei" e "Não gostei" em `feedback.csv`.

## Requisitos

- Python 3.10+
- Uma chave válida da Gemini API
- A API `Generative Language API` habilitada no projeto do Google Cloud
- Cota ou faturamento ativo no projeto, se quiser usar a resposta da IA

## Instalação

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv venv
venv\Scripts\activate
pip install streamlit python-dotenv google-generativeai
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com:

```env
GOOGLE_API_KEY=sua_chave_da_gemini
GOOGLE_MODEL_NAME=gemini-2.5-flash
```

Se preferir, você pode copiar o exemplo:

```bash
copy .env.example .env
```

## Como executar

```bash
streamlit run app/app.py
```

## Estrutura principal

- `app/app.py`: interface principal do CineIA
- `.env`: variáveis sensíveis locais
- `feedback.csv`: histórico de feedback gerado pela aplicação
- `.gitignore`: evita versionar segredos e arquivos locais

## Sobre o feedback

Quando o usuário avalia uma recomendação com "Gostei" ou "Não gostei", o app salva o contexto da sessão em `feedback.csv`. Isso serve como base para evoluir o comportamento do sistema em uma etapa futura de RLHF.


## Licença

Projeto acadêmico/demonstrativo.