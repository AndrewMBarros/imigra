import time
import shutil
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

from config.settings import URLS_3CX, URLS_YEASTAR, SAIDA_DIR, ENTRADA_DIR, MODELOS_DIR
from src.utils.navegador import iniciar_driver, login_3cx, login_yeastar, clicar_seguro

# =========================================================
# FUNÇÃO DE DOWNLOAD
# =========================================================
def ultimo_download():
    DOWNLOADS = Path.home() / "Downloads"
    arquivos = list(DOWNLOADS.glob("extensions*.csv"))

    if not arquivos:
        raise Exception("Nenhum arquivo extensions*.csv encontrado na pasta Downloads.")

    def arquivo_estavel(file_path, espera=2):
        tamanho1 = file_path.stat().st_size
        time.sleep(espera)
        tamanho2 = file_path.stat().st_size
        return tamanho1 == tamanho2

    arquivos.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    for arquivo in arquivos:
        try:
            if arquivo_estavel(arquivo):
                return arquivo
        except:
            continue
    return arquivos[0]

# =========================================================
# EXPORTAÇÃO DO 3CX
# =========================================================
def exportar_3cx(driver, wait, cliente):
    print(f"\n[3CX] Acessando painel e pesquisando cliente: {cliente}")
    
    clicar_seguro(driver, wait, By.ID, "menuAdmin")
    clicar_seguro(driver, wait, By.CSS_SELECTOR, "a[data-qa='numbers-and-messaging-link']")
    time.sleep(2)
    
    clicar_seguro(driver, wait, By.XPATH, "//a[contains(.,'Users') or contains(.,'Usuários')]")
    time.sleep(3)

    search = wait.until(EC.element_to_be_clickable((By.ID, "inputSearch")))
    search.click()
    search.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
    search.send_keys(cliente)
    time.sleep(2)

    linhas = driver.find_elements(By.XPATH, "//tr")
    if len(linhas) <= 1:
        raise Exception("Cliente não encontrado nesta nuvem 3CX.")

    print(" -> Selecionando todos os ramais...")
    try:
        driver.find_element(By.XPATH, "//thead//input[@type='checkbox']").click()
    except:
        pass

    print(" -> Desmarcando ramais de Suporte...")
    try:
        suportes = driver.find_elements(By.XPATH, "//tr[contains(.,'Suporte')]//input[@type='checkbox']")
        for s in suportes:
            if s.is_selected():
                s.click()
    except:
        pass

    clicar_seguro(driver, wait, By.XPATH, "//button[contains(.,'Export')]")
    print("Aguardando download da nuvem (6s)...")
    time.sleep(6)
    
    arquivo_baixado = ultimo_download()
    
    caminho_entrada = ENTRADA_DIR / arquivo_baixado.name
    shutil.move(str(arquivo_baixado), caminho_entrada)
    print(f" Arquivo CSV recebido com sucesso: {caminho_entrada.name}")
    return caminho_entrada

# =========================================================
# CRIAÇÃO DA ORG E IMPORTAÇÃO NO YEASTAR
# =========================================================
def importar_yeastar(driver, wait, file_csv, cliente):
    print(f"\n[Yeastar] Iniciando importação para: {cliente}")
    clicar_seguro(driver, wait, By.ID, "m_extension_trunk")
    clicar_seguro(driver, wait, By.ID, "m_extensions")
    time.sleep(2)

    print(" -> Criando Sub-organização...")
    clicar_seguro(driver, wait, By.CSS_SELECTOR, "i.anticon.ys-icon.title-icon.ant-dropdown-trigger")
    clicar_seguro(driver, wait, By.CSS_SELECTOR, "a.common-right-menu-item")

    nome_input = wait.until(EC.presence_of_element_located((By.ID, "name")))
    nome_input.click()
    nome_input.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
    nome_input.send_keys(cliente)

    btn_salvar = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'ant-modal-footer')]//button[.//span[text()='Salvar']]")))
    driver.execute_script("arguments[0].click();", btn_salvar)
    time.sleep(3)

    print(f" -> Acessando a Sub-organização {cliente}...")
    search = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Procurar']")))
    search.click()
    search.send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
    search.send_keys(cliente)
    time.sleep(2)

    cliente_span = wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(),'{cliente}')]")))
    driver.execute_script("arguments[0].click();", cliente_span)
    time.sleep(2) # Pequena pausa para garantir que os botões do cliente carreguem

    print(" -> Realizando upload do CSV de ramais...")
    
    # Busca o botão de importar. Usamos um try/except para garantir o clique
    try:
        btn_import = wait.until(EC.element_to_be_clickable((By.ID, "import")))
        driver.execute_script("arguments[0].click();", btn_import)
    except ElementClickInterceptedException:
        btn_import = wait.until(EC.presence_of_element_located((By.ID, "import")))
        driver.execute_script("arguments[0].click();", btn_import)

    # NOVIDADE: Aguarda a janela modal inteira aparecer na tela ANTES de buscar o input file
    print(" -> Aguardando janela de upload abrir...")
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ant-modal-content")))
    time.sleep(1) # Pausa para a animação do modal terminar
    
    # Agora sim, com o modal aberto e estável, pegamos o campo de arquivo
    input_file = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    input_file.send_keys(str(file_csv.resolve()))

    btn_confirmar_importacao = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//div[contains(@class,"ant-modal-footer")]//button[.//span[normalize-space()="Importar"]]')
        )
    )
    
    driver.execute_script("arguments[0].click();", btn_confirmar_importacao)
    
    print("Aguardando processamento no servidor (8s)...")
    time.sleep(8)
    
    try:
        btn_ok = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='OK']]")))
        driver.execute_script("arguments[0].click();", btn_ok)
    except TimeoutException:
        pass
        
    print("Ramais importados com sucesso para o Yeastar!")

# =========================================================
# ORQUESTRAÇÃO
# =========================================================
def migrar_extensoes(nuvem_3cx, nuvem_yeastar, cliente):
    if str(nuvem_3cx) not in URLS_3CX or str(nuvem_yeastar) not in URLS_YEASTAR:
        raise ValueError("IDs de Nuvem inválidos. Verifique os números digitados.")

    from src.etl.processador import processar_arquivo, carregar_csv
    
    driver, wait = iniciar_driver(timeout=15)
    try:
        login_3cx(driver, wait, URLS_3CX[str(nuvem_3cx)])
        csv_3cx = exportar_3cx(driver, wait, cliente)
        
        print("\n[ETL] Formatando CSV extraído com o nome correto do cliente...")
        modelo_base = carregar_csv(MODELOS_DIR / "MODELO YEASTAR.csv")
        resultado = processar_arquivo(csv_3cx, modelo_base, cliente_nome=cliente)
        csv_final = SAIDA_DIR / resultado["arquivo"]

        login_yeastar(driver, wait, URLS_YEASTAR[str(nuvem_yeastar)])
        importar_yeastar(driver, wait, csv_final, cliente)
        
    finally:
        driver.quit()