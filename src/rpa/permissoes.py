import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config.settings import URLS_YEASTAR
from src.utils.navegador import iniciar_driver, login_yeastar, clicar_seguro, digitar_seguro

def configurar_permissoes(nuvem_yeastar, cliente):
    if str(nuvem_yeastar) not in URLS_YEASTAR:
        raise ValueError("ID de Nuvem Yeastar inválido.")

    driver, wait = iniciar_driver(timeout=20)
    
    try:
        login_yeastar(driver, wait, URLS_YEASTAR[str(nuvem_yeastar)])
        
        clicar_seguro(driver, wait, By.ID, "m_extension_trunk")
        clicar_seguro(driver, wait, By.ID, "m_client_permission")
        clicar_seguro(driver, wait, By.ID, "permissionInternalTitle")
        
        clicar_seguro(driver, wait, By.CLASS_NAME, "permissionAdd")
        
        def confirmar_modal():
            btn_confirmar = wait.until(lambda d: d.find_element(By.XPATH, "//button[.//span[contains(.,'Confirmar')]]"))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_confirmar)
            driver.execute_script("arguments[0].click();", btn_confirmar)

        # Configurar ENTRADA
        clicar_seguro(driver, wait, By.CLASS_NAME, "permissionMemberInput")
        digitar_seguro(wait, By.XPATH, "//input[@autocomplete='off' and @placeholder='Procurar']", cliente)
        time.sleep(1.5) 
        clicar_seguro(driver, wait, By.CLASS_NAME, "permissionSelectMembersItemCheck")
        confirmar_modal()
        
        # Configurar VISUALIZAÇÃO
        select_vis = wait.until(lambda d: d.find_element(By.XPATH, "//div[contains(@class,'ant-select-selection-selected-value')]"))
        driver.execute_script("arguments[0].click();", select_vis)
        
        campo_vis = wait.until(lambda d: d.find_element(By.XPATH, "//input[contains(@class,'ant-select-search__field')]"))
        campo_vis.send_keys("Permitir a Visualização")
        campo_vis.send_keys(Keys.ENTER)
        
        # Configurar SAÍDA
        clicar_seguro(driver, wait, By.XPATH, "(//i[contains(@class,'input-edit-icon')])[2]")
        digitar_seguro(wait, By.XPATH, "//input[@autocomplete='off' and @placeholder='Procurar']", cliente)
        time.sleep(1.5)
        clicar_seguro(driver, wait, By.CLASS_NAME, "permissionSelectMembersItemCheck")
        confirmar_modal()
        
        # Salvar Regra
        clicar_seguro(driver, wait, By.XPATH, "//a[contains(@class,'common-opt-primary') and normalize-space()='Salvar']")
        time.sleep(3)
        
    finally:
        driver.quit()