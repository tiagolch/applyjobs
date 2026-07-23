# 💼 CareerSync AI (ApplyJob)

> **Gestão Inteligente e Acompanhamento de Candidaturas a Empregos**

O **CareerSync AI** é uma aplicação web desenvolvida em Python e Streamlit projetada para ajudar profissionais a gerenciar e otimizar todo o seu processo de busca de emprego. O sistema conta com arquitetura multi-usuário (multi-tenant), visualização de vagas em pipeline Kanban, dashboard executivo e persistência segura em banco de dados PostgreSQL (Supabase).

---

## 🚀 Funcionalidades Principais

* **🔒 Autenticação & Multi-Tenant:** Sistema de login e cadastro com armazenamento seguro de senhas criptografadas via `bcrypt`. Isolamento completo de dados por usuário.
* **📋 Quadro Kanban Interativo:** Acompanhamento visual de vagas divididas por fases (*Aplicado*, *Triagem*, *Entrevista*, *Proposta*, *Rejeitado*) com movimentação rápida de status em 1 clique.
* **🔍 Busca Rápida:** Filtro instantâneo por cargo ou empresa na barra lateral.
* **✏️ Edição e Detalhamento:** Modal de edição avançada (`@st.dialog`) para ajustar links das vagas, anotações e faixas salariais.
* **📊 Dashboard Executivo:** Gráficos interativos (Plotly) com métricas do funil de contratação e taxa de conversão entre etapas.
* **⚡ Otimização de Conexão:** Gerenciamento eficiente de conexões com PostgreSQL para evitar timeouts.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Interface Web:** [Streamlit](https://streamlit.io/)
* **Banco de Dados:** [PostgreSQL](https://www.postgresql.org/) / [Supabase](https://supabase.com/)
* **Driver de Banco:** `psycopg2`
* **Visualização de Dados:** `pandas`, `plotly`
* **Segurança e Criptografia:** `bcrypt`, `streamlit-authenticator`

---

## 📁 Estrutura do Projeto

```text
ApplyJob/
├── .streamlit/
│   └── secrets.toml          # Credenciais de acesso ao banco (Não comitar!)
├── database.py               # Módulo de conexão e queries PostgreSQL
├── main.py                   # Interface e regras de negócio do Streamlit
├── requirements.txt          # Dependências do projeto
├── .gitignore                # Arquivos ignorados pelo Git
└── README.md                 # Documentação do projeto