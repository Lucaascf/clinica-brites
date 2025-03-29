"""
Arquivo de configurações para o sistema de avaliação fisioterapêutica.
Contém as definições de cores, fontes, outros elementos visuais e configurações da aplicação.
"""

# URL do servidor
SERVER_URL = "http://localhost:5000"

# Configurações de cores principais
CORES = {
    "primaria": "#00ab7d",       # Verde turquesa (cor principal de fundo)
    "secundaria": "#3498db",     # Azul claro (para destaques e botões)
    "destaque": "#e74c3c",       # Vermelho (para alertas e elementos importantes)
    "fundo": "#00ab7d",          # Verde turquesa para o fundo geral
    "titulo_bg": "#00ab7d",      # Verde turquesa para o fundo dos títulos
    "texto": "#000000",          # Texto preto
    "texto_destaque": "#ffffff", # Texto branco para destaques
    "sucesso": "#2ecc71",        # Verde (para mensagens de sucesso e botões positivos)
    "aviso": "#f39c12",          # Laranja (para avisos)
    "campo_bg": "#ffffff",       # Branco para campos de entrada
    "secao_bg": "#00ab7d",       # Verde turquesa para seções
    "info": "#3498db",           # Azul informativo
    "borda": "#008c66",          # Verde mais escuro para bordas (variação do primário)
    "frame_bg": "#00ab7d",       # Verde turquesa para frames
    "notebook_bg": "#00ab7d",    # Verde turquesa para notebooks
    "tab_bg": "#008c66",         # Verde mais escuro para abas
    "button_bg": "#008c66"       # Verde mais escuro para botões
}

# Configurações de fonte
FONTES = {
    "titulo": ("Segoe UI", 22, "bold"),        # Já aumentado
    "secao": ("Segoe UI", 18, "bold"),         # Já aumentado
    "subsecao": ("Segoe UI", 16, "bold"),      # Já criado
    "campo": ("Segoe UI", 14),                 # Já aumentado
    "subcampo": ("Segoe UI", 14),              # Já aumentado
    "botao": ("Segoe UI", 14, "bold"),         # Já aumentado
    "texto_secao": ("Segoe UI", 16, "bold"),   # Já criado
    "cabecalho_card": ("Segoe UI", 18, "bold"), # Nova fonte para cabeçalhos de cards

    # Novas definições
    "cabecalho_card": ("Segoe UI", 20, "bold"),   # Para cabeçalhos de cards
    "subtitulo_secao": ("Segoe UI", 18, "bold"),  # Para subtítulos de seções
    "checkbox_texto": ("Segoe UI", 14)            # Para texto de checkboxes
}

# Configurações de tamanho
TAMANHOS = {
    "padding_padrao": 14,
    "margem_secao": 15,
    "altura_inicial_campo": 2,
    "altura_maxima_campo": 6
}

# Configurações de estilo para widgets
ESTILOS = {
    # Labels
    "titulo_label": {
        "font": FONTES["titulo"],
        "background": CORES["titulo_bg"],
        "foreground": CORES["texto_destaque"]
    },
    "secao_label": {
        "font": FONTES["secao"],
        "background": CORES["secao_bg"],
        "foreground": CORES["texto_destaque"]
    },
    "campo_label": {
        "font": FONTES["campo"],
        "background": CORES["secao_bg"],
        "foreground": CORES["texto_destaque"]
    },
    
    # Frames
    "titulo_frame": {
        "background": CORES["titulo_bg"]
    },
    "secao_frame": {
        "background": CORES["secao_bg"]
    },
    
    # Botões
    "botao_primario": {
        "background": CORES["button_bg"],
        "foreground": CORES["texto_destaque"]
    },
    "botao_sucesso": {
        "background": CORES["sucesso"],
        "foreground": CORES["texto_destaque"]
    },
    "botao_aviso": {
        "background": CORES["aviso"],
        "foreground": CORES["texto_destaque"]
    },
    
    # Campos de texto
    "campo_texto": {
        "background": CORES["campo_bg"],
        "foreground": CORES["texto"],
        "relief": "flat",
        "highlightthickness": 1,
        "highlightbackground": CORES["borda"],
        "highlightcolor": CORES["secundaria"]
    }
}

# Configurações do formulário
CONFIG_FORMULARIO = {
    "num_colunas": 2,  # Número de colunas para layout responsivo
    "dir_dados": "dados_pacientes"  # Diretório para salvar os dados
}

# Opções pré-definidas para comboboxes
OPCOES = {
    "sesiones_semana": ["1", "2", "3", "4", "5", "Otra"],
    "duracion_sesion": ["30 minutos", "45 minutos", "60 minutos", "90 minutos", "Otra"]
}

# Escalas
ESCALAS = {
    "eva": {
        "min": 0,
        "max": 10,
        "default": 0
    }
}

# Outras configurações
PLACEHOLDER_COLOR = "#666666" 