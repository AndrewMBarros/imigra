import threading
import traceback
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

# Importando as funções da nossa arquitetura
from src.etl.processador import executar_etl
from src.rpa.troncos import migrar_troncos
from src.rpa.filas import migrar_filas
from src.rpa.regras_saida import migrar_regras_saida
from src.rpa.extensoes import migrar_extensoes
from src.rpa.permissoes import configurar_permissoes
from src.rpa.grupos_extensao import migrar_grupos_extensao

# =========================================================
# CONFIGURAÇÃO INICIAL
# =========================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Migração 3CX → Yeastar")

# =========================================================
# TELA CHEIA
# =========================================================

def configurar_tela_maxima(app):
    largura = app.winfo_screenwidth()
    altura = app.winfo_screenheight()
    app.geometry(f"{largura}x{altura}+0+0")
    app.resizable(True, True)

configurar_tela_maxima(app)


BG_COLOR = "#0f172a"
CARD_COLOR = "#111827"
BTN_COLOR = "#2563eb"
BTN_HOVER = "#1d4ed8"
TEXT_COLOR = "#f8fafc"
SUBTEXT = "#94a3b8"

app.configure(fg_color=BG_COLOR)

# Variáveis globais para os inputs
entry_3cx = None
entry_yeastar = None
entry_cliente = None
status_label = None

def limpar_tela():
    for widget in app.winfo_children():
        widget.destroy()

# =========================================================
# EXECUTAR SCRIPTS (COM THREADING SEGURO)
# =========================================================
def iniciar_migracao(opcao):
    nuvem_3cx = entry_3cx.get().strip()
    nuvem_yeastar = entry_yeastar.get().strip()
    cliente = entry_cliente.get().strip()

    # Validação rápida para processos que exigem inputs
    if opcao in ["A", "C", "D", "E", "G", "TODOS"] and not (nuvem_3cx and nuvem_yeastar and cliente):
        messagebox.showwarning("Aviso", "Preencha a Nuvem 3CX, Nuvem Yeastar e o Cliente na lateral direita.")
        return

    rotinas = {
        "A": ("Migração de Ramais", lambda: migrar_extensoes(nuvem_3cx, nuvem_yeastar, cliente)),
        "B": ("Migração de Troncos", lambda: migrar_troncos(nuvem_3cx, nuvem_yeastar, cliente)),
        "C": ("Migração de Filas", lambda: migrar_filas(nuvem_3cx, nuvem_yeastar, cliente)),
        "D": ("Grupo de Extensão", lambda: migrar_grupos_extensao(nuvem_yeastar, cliente)),
        "E": ("Permissão de Cliente", lambda: configurar_permissoes(nuvem_yeastar, cliente)),
        "F": ("Rota de Entrada", lambda: print("Módulo de Rota de Entrada em breve...")),
        "G": ("Rotas de Saída", lambda: migrar_regras_saida(nuvem_3cx, nuvem_yeastar, cliente)),
        "ETL": ("Formatação ETL", lambda: executar_etl(cliente))
    }

    if opcao not in rotinas:
        messagebox.showinfo("Em desenvolvimento", "Este módulo será acoplado em breve.")
        return

    nome_processo, funcao = rotinas[opcao]
    
    status_label.configure(text=f"Executando: {nome_processo}...", text_color="#eab308")
    
    def worker():
        try:
            # Roda a automação pesada do Selenium no fundo
            funcao()
            
            # Quando dá certo, agenda a atualização na interface
            def on_success():
                status_label.configure(text=f"Concluído: {nome_processo}!", text_color="#22c55e")
                messagebox.showinfo("Sucesso", f"{nome_processo} finalizado com sucesso.")
            
            app.after(0, on_success)
            
        except Exception as e:
            # Imprime o erro exato no console caso dê problema no Selenium
            traceback.print_exc()
            
            # Congela a mensagem de erro numa variável estática
            erro_texto = str(e)
            
            # Agenda a mensagem de falha para a interface
            def on_error(err=erro_texto):
                status_label.configure(text="Erro no processo", text_color="#ef4444")
                messagebox.showerror("Erro na Execução", err)
                
            app.after(0, on_error)




    # Inicia a thread
    threading.Thread(target=worker, daemon=True).start()




# =========================================================
# TELA PRINCIPAL - 
# =========================================================
def tela_principal():
    global entry_3cx, entry_yeastar, entry_cliente, status_label
    limpar_tela()


# corrigir essa parte nao exatamente ao lado, mas com espaco

    INOVACOMM_LOGO = None

    try:
        INOVACOMM_LOGO = ctk.CTkImage(
            light_image=Image.open("data/img/inovacomm_logo.png"),
            size=(160, 55)
        )
    except Exception:
        pass


    container = ctk.CTkFrame(app, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=25, pady=10)



    menu = ctk.CTkFrame(
        container,
        fg_color=CARD_COLOR,
        corner_radius=20
    )

    menu.pack(side="left", fill="both", expand=True)


    # CAIXAS DE INFORMAÇÃO DOS BOXES  

    titulo = ctk.CTkLabel(
        menu,
        text="Migrações Disponíveis",
        font=("Arial", 24, "bold"),
        text_color=TEXT_COLOR
    )

    titulo.pack(pady=(0, 40))


    frame_botoes = ctk.CTkFrame(menu, fg_color="transparent")

    frame_botoes.pack(
        expand=True
    )

    frame_botoes.grid_columnconfigure(0, weight=1)
    frame_botoes.grid_columnconfigure(1, weight=1)

    # Frame dos botões
    frame_botoes = ctk.CTkFrame(menu, fg_color="transparent")
    frame_botoes.pack(expand=True)

    # ... criação dos botões ...

    # =====================================================
    # RODAPÉ CENTRAL
    # =====================================================

    footer = ctk.CTkFrame(menu, fg_color="transparent")
    footer.pack(pady=(30, 10))

    ctk.CTkLabel(
        footer,
        text="Versão 1.0.0",
        font=("Arial", 11),
        text_color="#64748b"
    ).pack()

    ctk.CTkLabel(
        footer,
        text="© 2026 Inovacomm Comunicações Unificadas",
        font=("Arial", 11),
        text_color="#64748b"
    ).pack()




    botoes = [
        ("A - RAMAL", "A"),
        ("B - TRONCO", "B"),
        ("C - FILA", "C"),
        ("D - GRUPO DE EXTENSÃO", "D"),
        ("E - PERMISSÃO DE CLIENTE", "E"),
        ("F - ROTA DE ENTRADA (PADRÃO DATORA)", "F"),
        ("G - ROTAS DE SAÍDA (PADRÃO DATORA)", "G"),
        ("H - MIGRAÇÃO COMPLETA", "H"),
    ]

    for i, (texto, codigo) in enumerate(botoes):

        linha = i // 2
        coluna = i % 2

        cor = BTN_COLOR
        hover = BTN_HOVER

        # H = botão verde
        if codigo == "H":
            cor = "#16a34a"
            hover = "#15803d"

        btn = ctk.CTkButton(
            frame_botoes,
            text=texto,
            height=50,
            corner_radius=12,
            fg_color=cor,
            hover_color=hover,
            font=("Arial", 14, "bold"),
            command=lambda c=codigo: iniciar_migracao(c)
        )

        btn.grid(
            row=linha,
            column=coluna,
            padx=8,
            pady=8,
            sticky="ew"
        )

    # Painel Lateral (Inputs)

    INOVACOMM_LOGO = None

    try:
        INOVACOMM_LOGO = ctk.CTkImage(
            light_image=Image.open("data/img/inovacomm_logo.png"),
            size=(160, 55)
        )
    except Exception:
        INOVACOMM_LOGO = None


    side = ctk.CTkFrame(
        container,
        width=320,
        fg_color=CARD_COLOR,
        corner_radius=20,
        border_width=1,
        border_color="#1e40af"
    )   
    
    side.pack(side="right", fill="y", padx=(20, 0))
    side.pack_propagate(False)



### gostaria de remover o logo desse canto 

    # =========================================================
    # TÍTULO DO PAINEL
    # =========================================================
    ctk.CTkLabel(
        side,
        text="CONFIGURAÇÃO",
        font=("Arial", 18, "bold"),
        text_color=TEXT_COLOR
    ).pack(pady=(25, 15))

    ctk.CTkLabel(side, text="Nuvem 3CX (Ex: 2, 3, 8):", text_color=SUBTEXT).pack(anchor="w", padx=25)
    entry_3cx = ctk.CTkEntry(side, width=270, height=40, corner_radius=10)
    entry_3cx.pack(padx=25, pady=(0, 15))

    ctk.CTkLabel(side, text="Nuvem Yeastar (Ex: 2, 5, 9):", text_color=SUBTEXT).pack(anchor="w", padx=25)
    entry_yeastar = ctk.CTkEntry(side, width=270, height=40, corner_radius=10)
    entry_yeastar.pack(padx=25, pady=(0, 15))

    ctk.CTkLabel(side, text="Nome do Cliente:", text_color=SUBTEXT).pack(anchor="w", padx=25)
    entry_cliente = ctk.CTkEntry(side, width=270, height=40, corner_radius=10)
    entry_cliente.pack(padx=25, pady=(0, 20))

    ctk.CTkFrame(
        side,
        height=1,
        fg_color="#1e40af"
    ).pack(fill="x", padx=25, pady=15)


    ctk.CTkLabel(
        side,
        text="STATUS",
        font=("Arial", 14, "bold"),
        text_color=TEXT_COLOR
    ).pack(anchor="w", padx=25)


    status_label = ctk.CTkLabel(
        side,
        text="Aguardando ação...",
        font=("Arial", 13),
        text_color=SUBTEXT
    )

    status_label.pack(
        anchor="w",
        padx=25,
        pady=(5, 20)
    )


    sair_btn = ctk.CTkButton(
        side, text="ENCERRAR", height=50, fg_color="#dc2626",
        hover_color="#b91c1c", font=("Arial", 16, "bold"), command=app.destroy
    )
    
    sair_btn.pack(
        side="bottom",
        padx=25,
        pady=(0, 80),
        fill="x"
    )


# =========================================================
# TELA BOAS VINDAS
# =========================================================

def tela_boas_vindas():
    limpar_tela()

    container = ctk.CTkFrame(
        app,
        width=700,
        height=560,
        fg_color=CARD_COLOR,
        corner_radius=25,
        border_width=1,
        border_color="#1e3a8a"
    )

    container.place(relx=0.5, rely=0.5, anchor="center")
    container.pack_propagate(False)

    # =====================================================
    # LOGO
    # =====================================================

    try:
        logo_inovacomm = ctk.CTkImage(
            light_image=Image.open("data/img/inovacomm_logo.png"),
            size=(350, 120)
        )

        ctk.CTkLabel(
            container,
            image=logo_inovacomm,
            text=""
        ).pack(pady=(35, 15))

    except Exception:
        pass

    # =====================================================
    # TITULO
    # =====================================================

    ctk.CTkLabel(
        container,
        text="3CX → Yeastar",
        font=("Arial", 34, "bold"),
        text_color=TEXT_COLOR
    ).pack()

    ctk.CTkLabel(
        container,
        text="Sistema de Migração Automatizada",
        font=("Arial", 16),
        text_color=SUBTEXT
    ).pack(pady=(6, 15))

    # =====================================================
    # SEPARADOR
    # =====================================================

    ctk.CTkFrame(
        container,
        height=1,
        fg_color="#1e40af"
    ).pack(fill="x", padx=80, pady=(0, 20))


    # =====================================================
    # BOTAO
    # =====================================================

    ctk.CTkButton(
        container,
        text="INICIAR MIGRAÇÃO",
        width=400,
        height=60,
        corner_radius=15,
        fg_color=BTN_COLOR,
        hover_color=BTN_HOVER,
        font=("Arial", 18, "bold"),
        command=tela_principal
    ).pack()

    # =====================================================
    # RODAPE
    # =====================================================

    ctk.CTkLabel(
        container,
        text="Versão 1.0.0",
        font=("Arial", 11),
        text_color="#64748b"
    ).pack(pady=(35, 5))

    ctk.CTkLabel(
        container,
        text="© 2026 Inovacomm Comunicações Unificadas",
        font=("Arial", 11),
        text_color="#64748b"

    ).pack()


tela_boas_vindas()
app.mainloop()
