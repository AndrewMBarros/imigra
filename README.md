![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-1E88E5)
![Status](https://img.shields.io/badge/Status-Active-success)


# Imigra — Automação de Migração 3CX → Yeastar

Ferramenta desktop de automação (RPA) desenvolvida em Python para migrar clientes de PABX em nuvem do **3CX** para o **Yeastar**, de ponta a ponta — sem necessidade de recadastro manual em cada painel.

## 📋 Sobre o projeto

O "Imigra" nasceu da necessidade de automatizar um processo que, feito manualmente, exigia recadastrar dezenas de configurações (ramais, troncos, filas, permissões, rotas) uma a uma no novo painel. A ferramenta automatiza a extração dessas configurações do 3CX, converte os dados para o formato exigido pelo Yeastar e realiza o cadastro automatizado no novo sistema.

## ✨ Funcionalidades

- **Interface gráfica própria** (CustomTkinter), com tema escuro e execução das etapas em threads separadas, sem travar a UI durante a automação.
- **Migração de Ramais** — exportação do 3CX e cadastro automatizado no Yeastar.
- **Migração de Troncos** — incluindo geração automática de nomenclatura padronizada.
- **Migração de Filas de Atendimento**.
- **Migração de Grupos de Extensão**.
- **Configuração de Permissões de Cliente** no Yeastar.
- **Migração de Regras de Rota de Saída**.
- **Pipeline de ETL** (pandas) para conversão dos CSVs exportados do 3CX ao layout de importação do Yeastar, com mapeamento de colunas e tratamento de encoding.
- Login e navegação automatizados nos dois painéis via Selenium, com lógica de retry para elementos que demoram a carregar.

## 🛠 Tecnologias

- Python
- Selenium
- Pandas
- CustomTkinter
- Pillow
- python-dotenv

## 📁 Estrutura do projeto

```
imigra/
├── main.py                    # Interface gráfica e orquestração das etapas
├── config/
│   └── settings.py            # Configurações e carregamento de credenciais (.env)
├── src/
│   ├── rpa/
│   │   ├── extensoes.py       # Migração de ramais
│   │   ├── troncos.py         # Migração de troncos
│   │   ├── filas.py           # Migração de filas
│   │   ├── grupos_extensao.py # Migração de grupos de extensão
│   │   ├── permissoes.py      # Configuração de permissões
│   │   └── regras_saida.py    # Migração de regras de rota de saída
│   ├── etl/
│   │   └── processador.py     # Conversão dos dados 3CX → Yeastar
│   └── utils/
│       └── navegador.py       # Login e navegação automatizados (Selenium)
└── data/                      # Pastas de entrada, saída e processados
```

## ⚙️ Configuração

As credenciais e URLs dos painéis são carregadas de um arquivo `.env` (não incluído no repositório) com as variáveis:

```
YEASTAR_USUARIO=
YEASTAR_SENHA=
TRESCX_USUARIO=
TRESCX_SENHA=
```

## 🚧 Status

Em desenvolvimento — migração de Grupos de Extensão e Rotas de Saída/Entrada em ajuste.

## 👤 Autor

Desenvolvido individualmente por **Andrew Matheus** enquanto Desenvolvedor Backend.

## 📄 Uso

Projeto de portfólio pessoal, publicado para fins de demonstração técnica. Uso comercial não autorizado sem permissão do autor.
