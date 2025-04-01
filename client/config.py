# Arquivo de configurações do Sistema de Avaliação Fisioterapêutica

# URL do servidor (para sistemas integrados)
SERVER_URL = "http://localhost:5000"

# Cores do sistema (paleta harmonizada com #00ab7d como cor principal)
CORES = {
    "fundo": "#f5f8f7",           # Fundo principal (verde muito claro)
    "secao_bg": "#ffffff",        # Fundo das seções (branco)
    "titulo_bg": "#00805e",       # Verde escuro para títulos (75% da cor principal)
    "texto_destaque": "#000000",  # Texto sobre fundos coloridos (branco)
    "texto": "#1a2a25",           # Texto principal escuro - melhor contraste com verde
    "texto_rotulo": "#00805e",    # Verde escuro para rótulos - mesma cor dos títulos
    "campo_bg": "#f7fcfa",        # Fundo dos campos (verde muito suave)
    "primaria": "#00ab7d",        # Cor primária (verde esmeralda - cor principal)
    "secundaria": "#009688",      # Cor secundária (verde azulado complementar)
    "sucesso": "#00c853",         # Verde vivo
    "erro": "#e53935",            # Vermelho escuro
    "aviso": "#ff9800",           # Laranja (cor complementar ao verde)
    "notebook_bg": "#e8f5f0",     # Fundo do notebook (verde muito claro)
    "tab_bg": "#80d5bb",          # Fundo das abas (verde médio claro)
    "button_bg": "#00805e",       # Botões (verde escuro)
    "separador": "#cce6df"        # Cor dos separadores (verde claro)
}

# Tipografia com fontes mais consistentes
FONTES = {
    "titulo": ("Segoe UI", 16, "bold"),
    "secao": ("Segoe UI", 14, "bold"),
    "subtitulo_secao": ("Segoe UI", 13, "bold"),
    "texto_secao": ("Segoe UI", 12, "bold"),
    "cabecalho_card": ("Segoe UI", 12, "bold"),
    "subsecao": ("Segoe UI", 11, "bold"),
    "campo": ("Segoe UI", 11),
    "campo_destaque": ("Segoe UI", 11, "bold"),
    "campo_pequeno": ("Segoe UI", 10),
    "subcampo": ("Segoe UI", 10, "italic"),
    "botao": ("Segoe UI", 11, "bold"),
    "checkbox_texto": ("Segoe UI", 10)
}

# Tamanhos padrão
TAMANHOS = {
    "padding_padrao": 12,
    "largura_janela": 1200,
    "altura_janela": 800,
    "largura_coluna": 150,
    "altura_inicial_campo": 3,     # Aumentado de 2 para 3
    "altura_maxima_campo": 20      # Aumentado de 8 para 20
}

# Estilos para componentes
ESTILOS = {
    "arredondamento_botao": 5,
    "borda_campo": 1,
    "sombreamento": "2px 2px 5px rgba(0, 171, 125, 0.2)"  # Sombra verde suave
}

# Configurações específicas do formulário
CONFIG_FORMULARIO = {
    "num_colunas": 12,  # Para layout responsivo
    "altura_maxima_texto": 25,     # Aumentado de 10 para 25
    "largura_padrao_campo": 60     # Aumentado de 40 para 60
}

# Opções para campos de seleção
OPCOES = {
    "sesiones_semana": ["1", "2", "3", "4", "5", "7"],
    "duracion_sesion": ["30 minutos", "45 minutos", "60 minutos", "90 minutos"]
}

# Escalas (para EVA e outras medições)
ESCALAS = {
    "eva": {"min": 0, "max": 10, "step": 1},
    "forca_muscular": {"min": 0, "max": 5, "step": 1}
}

# Cores para campos de placeholder
PLACEHOLDER_COLOR = "#9cbdb2"  # Tom médio de verde acinzentado