import pandas as pd
import shutil
import logging
import sys
import json
from pathlib import Path

# Consome as configurações centrais
from config.settings import (
    ENTRADA_DIR,
    SAIDA_DIR,
    PROCESSADOS_DIR,
    MODELOS_DIR,
    TRIGGER_FILE
)

logger = logging.getLogger(__name__)

MODELO_YEASTAR_FILE = MODELOS_DIR / "MODELO YEASTAR.csv"

# =========================================================
# UTILIDADES
# =========================================================

def criar_pastas_necessarias():
    for pasta in [ENTRADA_DIR, SAIDA_DIR, PROCESSADOS_DIR, MODELOS_DIR, TRIGGER_FILE.parent]:
        pasta.mkdir(parents=True, exist_ok=True)

def carregar_csv(caminho):
    return pd.read_csv(caminho, sep=None, engine="python", encoding="latin1", dtype=str)

def criar_modelo(df_modelo, qtd):
    return pd.DataFrame(index=range(qtd), columns=df_modelo.columns)

# =========================================================
# PROCESSAMENTO INDIVIDUAL
# =========================================================

def processar_arquivo(arquivo, df_modelo_base, cliente_nome):
    # Usa EXCLUSIVAMENTE o nome que veio da interface (Ex: Modulo Capital)
    cliente_arquivo = cliente_nome.replace(" ", "_")

    logger.info(f"Processando ETL para: {cliente_nome}")
    caminho_origem = ENTRADA_DIR / arquivo.name
    df_origem = carregar_csv(caminho_origem)

    df_modelo = criar_modelo(df_modelo_base, len(df_origem))
    df_modelo.columns = df_modelo_base.columns

    # Mapeamento do 3CX para o Yeastar
    mapeamento = {0: 1, 1: 2, 2: 3, 3: 4, 8: 0}
    for dest, src in mapeamento.items():
        if src < len(df_origem.columns) and dest < len(df_modelo.columns):
            df_modelo.iloc[:, dest] = df_origem.iloc[:, src]

    colunas = list(df_modelo.columns)
    colunas[8] = "Extension Number"
    df_modelo.columns = colunas

    df_modelo.iloc[:, 35] = "1"
    
    # Preenche a Coluna 79 forçando o nome da UI
    df_modelo.iloc[:, 79] = f"Inovacomm/{cliente_nome}"

    nome_saida = f"ATUALIZADO - MODELO YEASTAR_{cliente_arquivo}.csv"
    caminho_saida = SAIDA_DIR / nome_saida

    df_modelo.to_csv(caminho_saida, index=False, encoding="latin1")
    shutil.move(str(caminho_origem), PROCESSADOS_DIR / arquivo.name)

    return {"nome": cliente_nome, "arquivo": nome_saida}

# =========================================================
# FUNÇÃO PRINCIPAL (Para rodar pelo Botão ETL avulso)
# =========================================================

def executar_etl(cliente_nome):
    logger.info(f"Iniciando rotina de ETL avulsa para: {cliente_nome}")
    criar_pastas_necessarias()

    if not MODELO_YEASTAR_FILE.exists():
        logger.error(f"Modelo não encontrado em: {MODELO_YEASTAR_FILE}")
        return

    arquivos = sorted(ENTRADA_DIR.glob("extensions*.csv"))
    if not arquivos:
        logger.warning(f"Nenhum arquivo extensions.csv encontrado em: {ENTRADA_DIR}")
        raise FileNotFoundError("Coloque o CSV exportado pelo 3CX na pasta 'entrada' antes de rodar.")

    df_modelo_base = carregar_csv(MODELO_YEASTAR_FILE)
    execucao = []
    erros = []

    for arquivo in arquivos:
        try:
            resultado = processar_arquivo(arquivo, df_modelo_base, cliente_nome)
            execucao.append(resultado)
        except Exception as e:
            logger.error(f"Erro ao processar {arquivo.name}: {e}")
            erros.append(arquivo.name)

    # Atualiza Trigger JSON
    trigger = {
        "status": "pronto",
        "clientes_processados": len(execucao),
        "erros": erros,
        "clientes": execucao
    }

    with open(TRIGGER_FILE, "w", encoding="utf-8") as f:
        json.dump(trigger, f, indent=4, ensure_ascii=False)