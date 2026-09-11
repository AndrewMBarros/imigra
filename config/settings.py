import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de segurança do arquivo .env
load_dotenv()

# ==========================================
# MAPEAMENTO DE DIRETÓRIOS
# ==========================================
# Sobe duas pastas a partir de config/settings.py para chegar na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

ENTRADA_DIR = DATA_DIR / "entrada"
SAIDA_DIR = DATA_DIR / "saida"
PROCESSADOS_DIR = DATA_DIR / "processados"
MODELOS_DIR = DATA_DIR / "modelos"
TRIGGER_DIR = DATA_DIR / "trigger"

TRIGGER_FILE = TRIGGER_DIR / "trigger.json"
CONTROLE_FILE = DATA_DIR / "processados_upload.json"

# ==========================================
# CREDENCIAIS
# ==========================================
YEASTAR_USUARIO = os.getenv("YEASTAR_USUARIO")
YEASTAR_SENHA = os.getenv("YEASTAR_SENHA")

TRESCX_USUARIO = os.getenv("TRESCX_USUARIO")
TRESCX_SENHA = os.getenv("TRESCX_SENHA")

# ==========================================
# URLS DE NUVEM
# ==========================================
URLS_3CX = {
    "2": "https://URLS_3CX2.com.br/login",
    "3": "https://URLS_3CX3.com.br/login",
    "4": "https://URLS_3CX4.com.br/login",
    "5": "https://URLS_3CX5.com.br/login",
    "6": "https://URLS_3CX6.com.br/login",
    "8": "https://URLS_3CX8.com.br/login"
}

URLS_YEASTAR = {
    "2": "https://URLS_YEASTAR2/login",
    "5": "https://URLS_YEASTAR5/login",
    "7": "https://URLS_YEASTAR7/login",
    "9": "https://URLS_YEASTAR9/login"
}