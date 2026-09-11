import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException
)

# Importamos as configurações centralizadas
from config.settings import (
    YEASTAR_USUARIO,
    YEASTAR_SENHA,
    TRESCX_USUARIO,
    TRESCX_SENHA
)

logger = logging.getLogger(__name__)

# =========================================================
# INICIALIZAÇÃO
# =========================================================

def iniciar_driver(timeout=20):
    """Instancia o WebDriver com opções otimizadas."""
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, timeout)
    logger.info("Driver iniciado com sucesso.")
    
    return driver, wait

# =========================================================
# AÇÕES SEGURAS (CANIVETE SUÍÇO)
# =========================================================

def clicar_seguro(driver, wait, by, valor, tentativas=3):
    """
    Tenta clicar em um elemento. Se o clique for interceptado,
    força o clique via JavaScript.
    """
    for i in range(tentativas):
        try:
            elemento = wait.until(EC.element_to_be_clickable((by, valor)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elemento)
            time.sleep(0.3) 
            elemento.click()
            return elemento
            
        except ElementClickInterceptedException:
            logger.warning(f"Clique interceptado. Forçando JS no elemento: {valor}")
            driver.execute_script("arguments[0].click();", elemento)
            return elemento
            
        except Exception as e:
            if i == tentativas - 1:
                logger.error(f"Falha ao clicar em {valor} após {tentativas} tentativas: {e}")
                raise e
            time.sleep(1)

def digitar_seguro(wait, by, valor, texto):
    """Garante que o campo está limpo antes de digitar."""
    if texto is None:
        return
        
    campo = wait.until(EC.visibility_of_element_located((by, valor)))
    campo.click()
    campo.send_keys(Keys.CONTROL + "a")
    campo.send_keys(Keys.DELETE)
    campo.send_keys(str(texto))
    return campo

# =========================================================
# FLUXOS DE LOGIN
# =========================================================

def login_3cx(driver, wait, url):
    """Realiza o fluxo completo de login no 3CX."""
    logger.info(f"Acessando 3CX em: {url}")
    driver.get(url)
    
    digitar_seguro(wait, By.ID, "loginInput", TRESCX_USUARIO)
    digitar_seguro(wait, By.ID, "passwordInput", TRESCX_SENHA)
    
    clicar_seguro(driver, wait, By.ID, "submitBtn")
    
    # Aguarda o dashboard carregar para confirmar o login
    wait.until(EC.presence_of_element_located((By.ID, "menuAdmin")))
    
    # ==============================================================
    # CORREÇÃO: Aguarda o splash-screen do 3CX desaparecer da tela
    # ==============================================================
    try:
        wait.until(EC.invisibility_of_element_located((By.ID, "splash-screen")))
    except:
        pass
    
    time.sleep(1.5) # Pausa extra para a animação do menu estabilizar
    logger.info("Login no 3CX realizado com sucesso.")

def login_yeastar(driver, wait, url):
    """Realiza o fluxo completo de login no Yeastar."""
    logger.info(f"Acessando Yeastar em: {url}")
    driver.get(url)
    
    # Tenta aceitar certificado inseguro (ignora se não aparecer)
    try:
        wait_curto = WebDriverWait(driver, 3)
        btn_avancado = wait_curto.until(EC.element_to_be_clickable((By.ID, "details-button")))
        btn_avancado.click()
        wait_curto.until(EC.element_to_be_clickable((By.ID, "proceed-link"))).click()
    except TimeoutException:
        pass 
        
    digitar_seguro(wait, By.ID, "login_username", YEASTAR_USUARIO)
    digitar_seguro(wait, By.ID, "login_password", YEASTAR_SENHA)
    
    clicar_seguro(driver, wait, By.ID, "login-btn")
    logger.info("Login no Yeastar realizado com sucesso.")