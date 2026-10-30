<div align="center">

# 🌍 API IBGE · Países

**Consulta e exibição de dados de países a partir da API pública do IBGE**

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)
![API](https://img.shields.io/badge/API-IBGE-009c3b?style=for-the-badge)
![Licença](https://img.shields.io/badge/licença-MIT-blue?style=for-the-badge)
<!-- ⚠️ Troque/adicione badges conforme as tecnologias usadas, ex.: -->
<!-- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) -->
<!-- ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) -->

[Sobre](#-sobre) • [Funcionalidades](#-funcionalidades) • [Tecnologias](#-tecnologias) • [Como executar](#-como-executar) • [API](#-api-utilizada) • [Estrutura](#-estrutura-do-projeto) • [Autora](#-autora)

</div>

---

## 📖 Sobre

Este projeto consome a **API de Países do IBGE** para obter e apresentar informações sobre diferentes países, como identificação, localização, área, idiomas e outros indicadores disponibilizados pelo serviço.

> ⚠️ Descreva aqui, em 2 ou 3 linhas, o objetivo do projeto (acadêmico, estudo de consumo de API, dashboard etc.).

## ✨ Funcionalidades

- 🔎 Consulta de dados de países pela API do IBGE
- 📊 Exibição organizada das informações retornadas
- 🌐 Dados oficiais e atualizados, sem necessidade de chave de acesso
- ⚠️ *(adicione: busca por país, filtros, gráficos, tabela, comparação etc.)*

## 🛠️ Tecnologias

| Tecnologia | Uso |
|-----------|-----|
| ⚠️ Linguagem | Lógica e consumo da API |
| ⚠️ Biblioteca de requisições | Ex.: `requests`, `fetch`, `axios` |
| ⚠️ Interface | Ex.: Streamlit, HTML/CSS, Bootstrap |
| API REST do IBGE | Fonte dos dados |

## 🚀 Como executar

### Pré-requisitos

- ⚠️ Ex.: Python 3.10+ ou Node.js 18+
- Conexão com a internet

### Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/luizasilva08/api-IBGE-paises.git

# 2. Acessar a pasta
cd api-IBGE-paises

# 3. Instalar as dependências  ⚠️ ajuste conforme o projeto
pip install -r requirements.txt
```

### Execução

```bash
# ⚠️ Ajuste o comando conforme o projeto
python app.py
# ou
streamlit run front-end.py
```

## 🔌 API utilizada

Endpoint base da **API de Países do IBGE**:

```
https://servicodados.ibge.gov.br/api/v1/paises/{código}
```

**Exemplo de requisição:**

```bash
curl https://servicodados.ibge.gov.br/api/v1/paises/BR
```

**Principais informações retornadas:**

| Campo | Descrição |
|-------|-----------|
| `id` | Códigos de identificação (M49, ISO alpha-2 e alpha-3) |
| `nome` | Nome do país em diferentes idiomas |
| `area` | Área territorial |
| `localizacao` | Região e sub-região |
| `linguas` | Idiomas oficiais |

📚 Documentação oficial: [servicodados.ibge.gov.br/api/docs](https://servicodados.ibge.gov.br/api/docs)

## 📂 Estrutura do projeto

```
api-IBGE-paises/
├── ⚠️ arquivo_principal   # Ponto de entrada
├── ⚠️ requirements.txt    # Dependências
└── README.md              # Documentação
```

## 👩‍💻 Autora

<div align="center">

**Luíza da Silva**

[![GitHub](https://img.shields.io/badge/GitHub-luizasilva08-181717?style=for-the-badge&logo=github)](https://github.com/luizasilva08)

</div>

---

<div align="center">

Dados fornecidos pelo [IBGE](https://www.ibge.gov.br/) 🇧🇷

</div>
