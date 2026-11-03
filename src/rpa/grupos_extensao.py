import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config.settings import URLS_YEASTAR
from src.utils.navegador import iniciar_driver, login_yeastar, clicar_seguro, digitar_seguro

def migrar_grupos_extensao(nuvem_yeastar, cliente):
    if str(nuvem_yeastar) not in URLS_YEASTAR:
        raise ValueError("ID de Nuvem Yeastar inválido.")

    driver, wait = iniciar_driver(timeout=20)
    
    try:
        login_yeastar(driver, wait, URLS_YEASTAR[str(nuvem_yeastar)])
        
        print(f"\n[Yeastar] Criando Grupo de Extensões para: {cliente}")
        clicar_seguro(driver, wait, By.ID, "m_extension_trunk")
        clicar_seguro(driver, wait, By.ID, "m_extension_groups")
        
        clicar_seguro(driver, wait, By.XPATH, "//button[contains(@class,'btn-tools') and .//span[text()='Adicionar']]")
        
        digitar_seguro(wait, By.ID, "extension_group_basic_name", cliente)
        
        # Pesquisa na caixa de transferência (Membros)
        print(" -> Vinculando ramais ao grupo...")
        digitar_seguro(wait, By.XPATH, "//input[@placeholder='Procurar']", cliente)
        time.sleep(2) 
        
        linha_cliente = wait.until(EC.presence_of_element_located((By.XPATH, f"//tr[.//td[contains(., '{cliente}')]]")))
        checkbox = linha_cliente.find_element(By.XPATH, ".//span[contains(@class,'ant-checkbox')]")
        driver.execute_script("arguments[0].click();", checkbox)
        
        btn_direita = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'ant-btn-icon-only')]//i[contains(@class,'anticon-right')]/ancestor::button")))
        driver.execute_script("arguments[0].click();", btn_direita)
        
        print(" -> Configurando Permissões de Grupo...")
        clicar_seguro(driver, wait, By.XPATH, "//div[@role='tab' and contains(., 'Permissões de Grupo')]")
        time.sleep(1)
        
        # Desmarca o checkbox raiz do painel de operações
        inner = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(@class,'ant-tree-checkbox-inner')]")))
        driver.execute_script("arguments[0].click();", inner)
        
        # =========================================================
        # (Seus TODOs futuros de Regras Gerenciais ficam aqui)
        # BLOCO 1 - GERENTE OPÇÃO 2
        # BLOCO 1 - GERENTE OPÇÃO 3
        # BLOCO 2 - GERENTE OPÇÃO 1
        # =========================================================
        
        clicar_seguro(driver, wait, By.XPATH, '//*[contains(@id, "footer-btn-save")]')
        time.sleep(3)
        print("\n GRUPO DE EXTENSÕES CRIADO COM SUCESSO!")

    finally:
        driver.quit()