![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=selenium&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-1E88E5)
![Status](https://img.shields.io/badge/Status-Complete-success)

# Imigra — Automated 3CX → Yeastar PBX migration

[🇧🇷 Versão em Português](README.pt-BR.md)

Desktop automation tool (RPA) in Python that migrates cloud PBX clients from **3CX** to **Yeastar** end to end: it extracts the settings from the old panel, converts the data and registers everything in the new panel, with no manual re-entry.

## 📋 About

Done by hand, this migration meant re-entering dozens of settings (extensions, trunks, queues, permissions and routes) one by one in the new panel. Imigra extracts these settings from 3CX, converts them to the format Yeastar expects and registers them in the new system automatically.

## ✨ Features

- **Custom GUI** (CustomTkinter) with a dark theme; each step runs in its own thread, so the window never freezes during automation.
- **Extensions:** export from 3CX and automated import into Yeastar.
- **Trunks:** migration with standardized naming.
- **Extension groups.**
- **Queues** and **inbound routes:** present in the interface, still in development in this version.
- **Client permissions** in Yeastar.
- **Outbound route rules.**
- **ETL pipeline (pandas):** converts the CSVs exported from 3CX into Yeastar's import layout, with column mapping and encoding handling.
- **Robust navigation (Selenium):** automated login to both panels, with retries for clicks and typing on elements that load slowly.

## 🔄 How it works

1. In the interface, the user enters the source 3CX cloud, the target Yeastar cloud and the client name.
2. The robot logs into 3CX and exports the client's settings.
3. The ETL converts the data to Yeastar's import model.
4. The robot logs into Yeastar and imports or registers each item.
5. Steps can run one at a time or all in sequence.

## 📁 Structure

```
imigra/
├── main.py                    # GUI and step orchestration
├── config/
│   └── settings.py            # Folders, cloud URLs and .env loading
├── src/
│   ├── rpa/
│   │   ├── extensoes.py       # Extensions
│   │   ├── troncos.py         # Trunks
│   │   ├── filas.py           # Queues
│   │   ├── grupos_extensao.py # Extension groups
│   │   ├── permissoes.py      # Permissions
│   │   └── regras_saida.py    # Outbound routes
│   ├── etl/
│   │   └── processador.py     # 3CX → Yeastar conversion
│   └── utils/
│       └── navegador.py       # Driver, login and safe actions (Selenium)
└── data/                      # Created at runtime: input, output, processed and templates
```

## ⚙️ Getting started

**Requirements:** Python 3.12 and Google Chrome.

```bash
git clone https://github.com/AndrewMBarros/imigra.git
cd imigra
pip install -r requirements.txt
```

1. Copy `.env.example` to `.env` and fill in:

   ```
   YEASTAR_USUARIO=
   YEASTAR_SENHA=
   TRESCX_USUARIO=
   TRESCX_SENHA=
   ORGANIZACAO=      # organization prefix used in the Yeastar import
   ```

2. In `config/settings.py`, replace the sample addresses in `URLS_3CX` and `URLS_YEASTAR` with your own clouds.
3. Put the Yeastar import templates (`MODELO YEASTAR.csv` and `TRONCO YEASTAR.csv`) in `data/modelos/`. They are exported from the Yeastar panel itself.
4. Run:

   ```bash
   python main.py
   ```

> Credentials, server addresses and client data are **not** part of the repository. The `.env` file and the data folders are in `.gitignore`.

## 🛠 Tech stack

Python · Selenium · pandas · CustomTkinter · python-dotenv

## 👤 Author

**Andrew Matheus** — [LinkedIn](https://www.linkedin.com/in/andrewmbs/) · [GitHub](https://github.com/AndrewMBarros)

Portfolio project, published for technical demonstration.
