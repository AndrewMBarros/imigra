import time
import pandas as pd

from selenium.webdriver.common.by import By

from config.settings import SAIDA_DIR, URLS_3CX, URLS_YEASTAR
from src.utils.navegador import (
    iniciar_driver,
    login_3cx,
    login_yeastar,
    clicar_seguro
)


def safe_get(driver, xpath, attr="value"):
    try:
        elemento = driver.find_element(By.XPATH, xpath)

        if attr is None:
            return elemento.text.strip()

        valor = elemento.get_attribute(attr)

        return valor.strip() if valor else ""

    except Exception:
        return ""


def migrar_regras_saida(nuvem_3cx, nuvem_yeastar, nome_empresa):

    if nuvem_3cx not in URLS_3CX:
        raise ValueError("Nuvem 3CX inválida.")

    if nuvem_yeastar not in URLS_YEASTAR:
        raise ValueError("Nuvem Yeastar inválida.")

    dados_regras = []

    driver = None
    wait = None

    try:

        print("Iniciando navegador...")
        driver, wait = iniciar_driver(timeout=30)

        print("Login 3CX...")
        login_3cx(
            driver,
            wait,
            URLS_3CX[nuvem_3cx]
        )

        try:
            clicar_seguro(
                driver,
                wait,
                By.XPATH,
                '//a[contains(@href,"outbound-rules")]'
            )
        except Exception:
            clicar_seguro(
                driver,
                wait,
                By.XPATH,
                '//span[contains(text(),"Regras de Saída")]'
            )

        campo_busca = wait.until(
            lambda d: d.find_element(
                By.ID,
                "inputSearch"
            )
        )

        campo_busca.clear()
        campo_busca.send_keys(nome_empresa)

        time.sleep(3)

        linhas = wait.until(
            lambda d: d.find_elements(
                By.CSS_SELECTOR,
                "tbody tr"
            )
        )

        total_linhas = len(linhas)

        print(f"Encontradas {total_linhas} regras.")

        for indice in range(total_linhas):

            try:

                linhas = wait.until(
                    lambda d: d.find_elements(
                        By.CSS_SELECTOR,
                        "tbody tr"
                    )
                )

                if indice >= len(linhas):
                    continue

                linhas[indice].click()

                time.sleep(1)

                botoes_editar = driver.find_elements(
                    By.XPATH,
                    '//button[contains(.,"Editar")]'
                )

                if not botoes_editar:
                    print(
                        f"Regra {indice + 1}: botão editar não encontrado."
                    )
                    continue

                botoes_editar[0].click()

                wait.until(
                    lambda d: d.find_element(
                        By.XPATH,
                        '//input[contains(@ng-model,"rule.Name")]'
                    )
                )

                nome_regra = safe_get(
                    driver,
                    '//input[contains(@ng-model,"rule.Name")]'
                )

                anexar = safe_get(
                    driver,
                    '(//input[contains(@ng-model,"route.Prepend")])[1]'
                )

                callerid = safe_get(
                    driver,
                    '(//input[contains(@ng-model,"route.CallerID")])[1]'
                )

                tronco = safe_get(
                    driver,
                    '(//select[contains(@ng-model,"route.Gateway")])[1]',
                    None
                )

                grupo = safe_get(
                    driver,
                    '//button[contains(@class,"department")]',
                    None
                )

                callerid_yeastar = f"{anexar}{callerid}"

                dados_regras.append({
                    "Nome": nome_regra,
                    "Anexar": anexar,
                    "CallerID": callerid,
                    "CallerID_Yeastar": callerid_yeastar,
                    "Tronco": tronco,
                    "Grupo": grupo,
                    "Formato_1": "[1-9]X.",
                    "Retira_1": "",
                    "Prefixo_1": anexar,
                    "Formato_2": "0X.",
                    "Retira_2": "1",
                    "Prefixo_2": "55"
                })

                print(
                    f"Capturado: {nome_regra}"
                )

                try:
                    clicar_seguro(
                        driver,
                        wait,
                        By.XPATH,
                        '//button[contains(@class,"back")]'
                    )
                except Exception:
                    driver.back()

                time.sleep(2)

            except Exception as erro:

                print(
                    f"Erro na regra {indice + 1}: "
                    f"{type(erro).__name__} - {erro}"
                )

                try:
                    driver.back()
                except Exception:
                    pass

        arquivo_csv = (
            SAIDA_DIR /
            f"REGRAS_{nome_empresa}.csv"
        )

        pd.DataFrame(
            dados_regras
        ).to_csv(
            arquivo_csv,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )

        print(f"CSV salvo: {arquivo_csv}")

        print("Login Yeastar...")

        login_yeastar(
            driver,
            wait,
            URLS_YEASTAR[nuvem_yeastar]
        )

        wait.until(
            lambda d: d.find_element(
                By.ID,
                "m_call_control"
            )
        ).click()

        time.sleep(1)

        wait.until(
            lambda d: d.find_element(
                By.ID,
                "m_outbound_routes"
            )
        ).click()

        time.sleep(2)

        for regra in dados_regras:

            try:

                clicar_seguro(
                    driver,
                    wait,
                    By.XPATH,
                    '//button[contains(.,"Adicionar")]'
                )

                time.sleep(2)

                wait.until(
                    lambda d: d.find_element(
                        By.ID,
                        "name"
                    )
                ).send_keys(regra["Nome"])

                wait.until(
                    lambda d: d.find_element(
                        By.ID,
                        "outbound_caller_id"
                    )
                ).send_keys(
                    regra["CallerID_Yeastar"]
                )

                patterns = driver.find_elements(
                    By.XPATH,
                    '//input[contains(@name,"pattern")]'
                )

                prepends = driver.find_elements(
                    By.XPATH,
                    '//input[contains(@name,"prepend")]'
                )

                if len(patterns) > 0:
                    patterns[0].send_keys(
                        regra["Formato_1"]
                    )

                if len(prepends) > 0:
                    prepends[0].send_keys(
                        regra["Prefixo_1"]
                    )

                clicar_seguro(
                    driver,
                    wait,
                    By.XPATH,
                    '//button[contains(.,"Adicionar")]'
                )

                time.sleep(1)

                patterns = driver.find_elements(
                    By.XPATH,
                    '//input[contains(@name,"pattern")]'
                )

                strips = driver.find_elements(
                    By.XPATH,
                    '//input[contains(@name,"strip")]'
                )

                prepends = driver.find_elements(
                    By.XPATH,
                    '//input[contains(@name,"prepend")]'
                )

                if len(patterns) > 1:
                    patterns[1].send_keys(
                        regra["Formato_2"]
                    )

                if len(strips) > 1:
                    strips[1].send_keys(
                        regra["Retira_2"]
                    )

                if len(prepends) > 1:
                    prepends[1].send_keys(
                        regra["Prefixo_2"]
                    )

                # AJUSTAR COM O HTML REAL
                # preencher tronco
                # preencher grupo

                print(
                    f"Tronco: {regra['Tronco']}"
                )

                print(
                    f"Grupo: {regra['Grupo']}"
                )

                clicar_seguro(
                    driver,
                    wait,
                    By.XPATH,
                    '//*[contains(@id,"footer-btn-save")]'
                )

                time.sleep(3)

                print(
                    f"Criada: {regra['Nome']}"
                )

            except Exception as erro:

                print(
                    f"Erro ao criar "
                    f"{regra['Nome']}: "
                    f"{erro}"
                )

                try:
                    driver.refresh()
                except Exception:
                    pass

                time.sleep(2)

    finally:

        if driver:
            try:
                driver.quit()
            except Exception:
                pass



'''Posso corrigir a estrutura do código, mas não consigo corrigir 100% os seletores 

do Yeastar e do 3CX sem ver o HTML das telas.
Os campos de Tronco e Grupo, por exemplo, dependem dos IDs/XPaths reais.
Mesmo assim, segue uma versão organizada e corrigida dos principais problemas:

Inicialização segura do driver.
Busca limpando o campo.
Uso correto do índice da linha.
safe_get fora do loop.
Logs de erro.
Proteção contra listas vazias.
CSV completo.
Uso do Tronco e Grupo preparado para preenchimento.'''




'''
Preciso do HTML apenas dos elementos que o script precisa preencher ou ler. Não preciso da página inteira.

Para o 3CX

Se já está capturando corretamente:

Nome da Regra
Anexar
Caller ID
Tronco
Grupo

então provavelmente não preciso de nada do 3CX.

Só preciso se algum desses campos estiver vindo vazio.

Para o Yeastar

Preciso do HTML dos campos:

1. Tronco

<div id="m_extension_trunk" class="menu-item"><i class="anticon ys-icon left-icon"><svg width="1em" height="1em" fill="currentColor" aria-hidden="true" focusable="false" class=""><use xlink:href="#icon-extension-trunk"></use></svg></i><span>Extensão e Tronco</span></div>
<a class="menu-item" id="m_trunks" href="/extension_trunk/trunks"><span>Tronco</span></a>

Na tela "Adicionar Rota de Saída":

Clique com botão direito no campo Tronco.
Inspecionar.
Copie o elemento completo.

Algo parecido com:

<select id="trunk_id">
    ...
</select>

ou

<input name="trunk">

ou

<div class="select2-container">
2. Extensão / Grupo de Extensões

Copie o HTML do campo onde você seleciona:

Extensão / Grupo de Extensões
3. Botão Salvar

Para confirmar se o XPath está correto:

'''