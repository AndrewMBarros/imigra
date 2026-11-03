import time
import shutil
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException

# Importa nossas configurações e ferramentas criadas
from config.settings import (
    ENTRADA_DIR,
    SAIDA_DIR,
    PROCESSADOS_DIR,
    MODELOS_DIR,
    URLS_3CX,
    URLS_YEASTAR
)
from src.utils.navegador import (
    iniciar_driver,
    clicar_seguro,
    login_3cx,
    login_yeastar
)

MODELO_TRONCO_FILE = MODELOS_DIR / "TRONCO YEASTAR.csv"

def gerar_coluna_a(texto):
    """Regra de negócio para gerar o Name da Datora."""
    try:
        texto = str(texto).replace("Datora -", "").strip()
        partes = texto.rsplit(" ", 1)
        if len(partes) < 2: return ""
        
        cliente_nome = partes[0].strip().upper().replace(" ", "_")
        numero = partes[1].strip()
        
        if len(numero) == 14:
            return f"{cliente_nome}_DATORA_SAIDA_{numero}"
        return f"{cliente_nome}_DATORA_{numero}"
    except:
        return ""

# AGORA A FUNÇÃO RECEBE AS VARIÁVEIS DA INTERFACE
def migrar_troncos(nuvem_3cx, nuvem_yeastar, nome_cliente):
    if str(nuvem_3cx) not in URLS_3CX or str(nuvem_yeastar) not in URLS_YEASTAR:
        raise ValueError("IDs de Nuvem inválidos. Verifique os números digitados.")

    print(f"\n--- INICIANDO MIGRAÇÃO DE TRONCOS PARA: {nome_cliente} ---")
    
    # =========================================================
    # 1. LOGIN NO 3CX E EXTRAÇÃO
    # =========================================================
    driver, wait = iniciar_driver(timeout=25)
    
    try:
        login_3cx(driver, wait, URLS_3CX[str(nuvem_3cx)])

        clicar_seguro(driver, wait, By.ID, "menuAdmin")
        clicar_seguro(driver, wait, By.CSS_SELECTOR, 'a[routerlink="/office/voice-and-chat"]')

        # Pesquisa o cliente
        print(" -> Pesquisando troncos no 3CX...")
        campo_busca = wait.until(EC.element_to_be_clickable((By.ID, "inputSearch")))
        campo_busca.click()
        campo_busca.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
        campo_busca.send_keys(nome_cliente)

        # Aguarda tabela atualizar
        time.sleep(3) 

        linhas = driver.find_elements(By.CSS_SELECTOR, 'tr[data-qa="trunk"]')
        if not linhas:
            raise Exception(f"Nenhum tronco encontrado para o cliente {nome_cliente} no 3CX.")

        dados = []
        for linha in linhas:
            try:
                dados.append({
                    "Nome": linha.find_element(By.CSS_SELECTOR, 'span[data-qa="name"]').text.strip(),
                    "Informacao": linha.find_element(By.CSS_SELECTOR, 'td[data-qa="text"] .line-clamp-1').text.strip(),
                    "Departamento": linha.find_element(By.CSS_SELECTOR, 'td[data-qa="groups"] .line-clamp-1').text.strip(),
                    "Encaminhar_Para": linha.find_element(By.CSS_SELECTOR, 'div[data-qa="route-destination"]').text.replace("\n", " ").strip()
                })
            except Exception as e:
                print(f"Erro ao ler linha de tronco: {e}")

        # Salva o CSV bruto
        df_tronco = pd.DataFrame(dados)
        nome_csv = f"TRONCO_{nome_cliente}.csv"
        csv_tronco = ENTRADA_DIR / nome_csv
        df_tronco.to_csv(csv_tronco, index=False, sep=",", encoding="utf-8-sig")

    finally:
        driver.quit()

    # =========================================================
    # 2. TRATAMENTO DE DADOS (PANDAS)
    # =========================================================
    print("\n[ETL] Tratando dados dos troncos...")
    df_tronco = pd.read_csv(csv_tronco, sep=None, engine="python", encoding="utf-8-sig").reset_index(drop=True)
    df_modelo = pd.read_csv(MODELO_TRONCO_FILE, sep=None, engine="python", encoding="utf-8-sig").reset_index(drop=True)

    df_modelo = df_modelo.iloc[:len(df_tronco)].copy()
    df_modelo["Name"] = df_tronco.iloc[:, 0].apply(gerar_coluna_a).reset_index(drop=True)
    df_modelo["Username"] = df_tronco.iloc[:, 1].fillna("").astype(str).reset_index(drop=True)

    saida_csv = SAIDA_DIR / f"ATUALIZADA_{nome_csv}"
    df_modelo.to_csv(saida_csv, index=False, sep=",", encoding="utf-8-sig")
    shutil.move(str(csv_tronco), PROCESSADOS_DIR / nome_csv)

    # =========================================================
    # 3. LOGIN E UPLOAD NO YEASTAR
    # =========================================================
    print(f"\n[Yeastar] Iniciando importação do tronco...")
    driver, wait = iniciar_driver(timeout=20)
    
    try:
        login_yeastar(driver, wait, URLS_YEASTAR[str(nuvem_yeastar)])

        clicar_seguro(driver, wait, By.ID, "m_extension_trunk")
        clicar_seguro(driver, wait, By.ID, "m_trunks")
        time.sleep(2)

        print(f" -> Realizando upload de: {saida_csv.name}")
        
        try:
            btn_import = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[normalize-space()='Importar']]")))
            driver.execute_script("arguments[0].click();", btn_import)
        except:
            btn_import = wait.until(EC.presence_of_element_located((By.XPATH, "//button[.//span[normalize-space()='Importar']]")))
            driver.execute_script("arguments[0].click();", btn_import)

        # Usamos a mesma trava de segurança que usamos em Ramais para evitar o "NoSuchElementException"
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ant-modal-content")))
        time.sleep(1)

        input_file = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        input_file.send_keys(str(saida_csv.resolve()))

        btn_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"ant-modal-footer")]//button[.//span[normalize-space()="Importar"]]')))
        driver.execute_script("arguments[0].click();", btn_confirmar)
        
        time.sleep(5)
        
        try:
            btn_ok = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='OK']]")))
            driver.execute_script("arguments[0].click();", btn_ok)
        except:
            pass

        print(" Troncos importados com sucesso para o Yeastar!")
            
    finally:
        driver.quit()
        print("--- MIGRAÇÃO DE TRONCOS FINALIZADA ---")