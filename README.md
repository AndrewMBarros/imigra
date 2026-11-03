![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-1E88E5)
![Status](https://img.shields.io/badge/Status-Concluído-success)

# Imigra — Migração automatizada de PABX 3CX → Yeastar

Ferramenta desktop de automação (RPA) em Python que migra clientes de PABX em nuvem do **3CX** para o **Yeastar** de ponta a ponta: extrai as configurações do painel antigo, converte os dados e cadastra tudo no painel novo, sem recadastro manual.

## 📋 Sobre o projeto

O Imigra nasceu da necessidade de automatizar um processo que, feito manualmente, exigia recadastrar dezenas de configurações (ramais, troncos, filas, permissões e rotas) uma a uma no novo painel. A ferramenta extrai essas configurações do 3CX, converte os dados para o formato exigido pelo Yeastar e faz o cadastro automatizado no novo sistema.

## ✨ Funcionalidades

- **Interface gráfica própria** (CustomTkinter), com tema escuro e cada etapa rodando em thread separada, sem travar a tela durante a automação.
- **Ramais:** exportação do 3CX e importação automatizada no Yeastar.
- **Troncos:** migração com geração de nomenclatura padronizada.
- **Grupos de extensão.**
- **Filas de atendimento** e **rotas de entrada**: previstas na interface, em desenvolvimento nesta versão.
- **Permissões de cliente** no Yeastar.
- **Regras de rota de saída.**
- **Pipeline ETL (pandas):** converte os CSVs exportados do 3CX para o layout de importação do Yeastar, com mapeamento de colunas e tratamento de encoding.
- **Navegação robusta (Selenium):** login automatizado nos dois painéis, cliques e digitação com novas tentativas para elementos que demoram a carregar.

## 🔄 Como funciona

1. O usuário informa, na interface, a nuvem 3CX de origem, a nuvem Yeastar de destino e o nome do cliente.
2. O robô faz login no 3CX e exporta as configurações do cliente.
3. O ETL converte os dados para o modelo de importação do Yeastar.
4. O robô faz login no Yeastar e importa ou cadastra cada item.
5. As etapas podem ser executadas separadamente ou todas em sequência.

## 📁 Estrutura

```
imigra/
├── main.py                    # Interface gráfica e orquestração das etapas
├── config/
│   └── settings.py            # Pastas, URLs das nuvens e leitura do .env
├── src/
│   ├── rpa/
│   │   ├── extensoes.py       # Ramais
│   │   ├── troncos.py         # Troncos
│   │   ├── filas.py           # Filas
│   │   ├── grupos_extensao.py # Grupos de extensão
│   │   ├── permissoes.py      # Permissões
│   │   └── regras_saida.py    # Rotas de saída
│   ├── etl/
│   │   └── processador.py     # Conversão 3CX → Yeastar
│   └── utils/
│       └── navegador.py       # Driver, login e ações seguras (Selenium)
└── data/                      # Criada na execução: entrada, saída, processados e modelos
```

## ⚙️ Como executar

**Requisitos:** Python 3.12 e Google Chrome.

```bash
git clone https://github.com/AndrewMBarros/imigra.git
cd imigra
pip install -r requirements.txt
```

1. Copie `.env.example` para `.env` e preencha:

   ```
   YEASTAR_USUARIO=
   YEASTAR_SENHA=
   TRESCX_USUARIO=
   TRESCX_SENHA=
   ORGANIZACAO=      # prefixo da organização usado na importação do Yeastar
   ```

2. Em `config/settings.py`, troque os endereços de exemplo em `URLS_3CX` e `URLS_YEASTAR` pelos das suas nuvens.
3. Coloque os modelos de importação do Yeastar (`MODELO YEASTAR.csv` e `TRONCO YEASTAR.csv`) em `data/modelos/`. Eles são exportados do próprio painel Yeastar.
4. Execute:

   ```bash
   python main.py
   ```

> Credenciais, endereços de servidores e dados de clientes **não** fazem parte do repositório. O `.env` e as pastas de dados estão no `.gitignore`.

## 🛠 Tecnologias

Python · Selenium · pandas · CustomTkinter · python-dotenv

## 👤 Autor

**Andrew Matheus** — [LinkedIn](https://www.linkedin.com/in/andrewmbs/) · [GitHub](https://github.com/AndrewMBarros)

Projeto de portfólio, publicado para demonstração técnica.
