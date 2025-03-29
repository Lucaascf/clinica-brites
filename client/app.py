import tkinter as tk
from tkinter import messagebox, font
from tkcalendar import DateEntry
import datetime
import json
import os
from PIL import Image, ImageTk  # Para ícones e imagens
from tkinter import ttk  

# Importar as configurações
from config import SERVER_URL, CORES, FONTES, TAMANHOS, ESTILOS, CONFIG_FORMULARIO, OPCOES, ESCALAS, PLACEHOLDER_COLOR

class CampoTextoAutoExpansivel(tk.Frame):
    """
    Widget personalizado que cria um campo de texto que expande automaticamente
    conforme o conteúdo é adicionado, mantendo todo o texto visível.
    """
    def __init__(self, master=None, **kwargs):
        """Inicializa o widget com um campo de texto que auto-expande"""
        super().__init__(master)
        
        # Extrair e remover argumentos específicos deste widget
        self.largura = kwargs.pop("width", 40)
        self.altura_inicial = kwargs.pop("height", TAMANHOS["altura_inicial_campo"])
        self.altura_maxima = kwargs.pop("max_height", TAMANHOS["altura_maxima_campo"])
        self.cor_fundo = kwargs.pop("bg", CORES["campo_bg"])
        self.cor_placeholder = kwargs.pop("placeholder_color", PLACEHOLDER_COLOR)
        self.texto_placeholder = kwargs.pop("placeholder", "")
        self.font = kwargs.pop("font", FONTES["campo"])  # Usar fonte do config.py com padrão
        
        # Configurar o estilo do frame com bordas arredondadas
        self.configure(
            highlightthickness=1, 
            highlightbackground="#cccccc", 
            highlightcolor=CORES["secundaria"],
            bg=self.cor_fundo,
            bd=0,
            padx=2,
            pady=2
        )
        
        # Configurar padrões para o Text widget
        kwargs.setdefault("wrap", "word")
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("padx", 8)
        kwargs.setdefault("pady", 8)
        kwargs.setdefault("bg", self.cor_fundo)
        kwargs.setdefault("font", self.font)  # Usar a fonte definida acima
        
        # Criar e configurar o campo de texto
        self.texto = tk.Text(
            self, 
            width=self.largura, 
            height=self.altura_inicial,
            highlightthickness=0,
            **kwargs
        )
        self.texto.pack(fill=tk.BOTH, expand=True)
        
        # Inserir placeholder se definido
        if self.texto_placeholder:
            self.texto.insert("1.0", self.texto_placeholder)
            self.texto.config(fg=self.cor_placeholder)
            self.has_placeholder = True
        else:
            self.has_placeholder = False
        
        # Vincular eventos para ajuste automático de tamanho
        self.texto.bind("<KeyRelease>", self._ajustar_altura)
        self.texto.bind("<FocusIn>", self._ao_receber_foco)
        self.texto.bind("<FocusOut>", self._ao_perder_foco)
    
    def _ajustar_altura(self, evento=None):
        """Ajusta a altura do widget com base no conteúdo"""
        # Obter número de linhas pelo índice da última linha
        num_linhas = int(self.texto.index('end-1c').split('.')[0])
        
        # Garantir pelo menos a altura inicial
        num_linhas = max(self.altura_inicial, min(num_linhas, self.altura_maxima))
        
        # Configurar nova altura
        self.texto.configure(height=num_linhas)
        
        # Atualizar visualização
        self.update_idletasks()
    
    def _ao_receber_foco(self, evento=None):
        """Altera a aparência quando o campo recebe foco"""
        self.configure(highlightbackground="#3498db", highlightthickness=2)
        
        # Limpar placeholder se necessário
        if self.has_placeholder and self.texto.get("1.0", "end-1c") == self.texto_placeholder:
            self.texto.delete("1.0", "end")
            self.texto.config(fg="black")
            self.has_placeholder = False
    
    def _ao_perder_foco(self, evento=None):
        """Altera a aparência quando o campo perde foco e ajusta a altura"""
        self.configure(highlightbackground="#cccccc", highlightthickness=1)
        
        # Restaurar placeholder se o campo estiver vazio
        if not self.texto.get("1.0", "end-1c") and self.texto_placeholder:
            self.texto.insert("1.0", self.texto_placeholder)
            self.texto.config(fg=self.cor_placeholder)
            self.has_placeholder = True
            
        self._ajustar_altura()
    
    def obter(self):
        """Retorna o texto atual (excluindo placeholder)"""
        if self.has_placeholder:
            return ""
        return self.texto.get("1.0", "end-1c")
    
    def definir(self, texto):
        """Define o texto e ajusta a altura"""
        self.texto.delete("1.0", "end")
        if texto:
            self.texto.insert("1.0", texto)
            self.texto.config(fg="black")
            self.has_placeholder = False
        elif self.texto_placeholder:
            self.texto.insert("1.0", self.texto_placeholder)
            self.texto.config(fg=self.cor_placeholder)
            self.has_placeholder = True
        self._ajustar_altura()
    
    def limpar(self):
        """Limpa o campo de texto"""
        self.texto.delete("1.0", "end")
        if self.texto_placeholder:
            self.texto.insert("1.0", self.texto_placeholder)
            self.texto.config(fg=self.cor_placeholder)
            self.has_placeholder = True
        self._ajustar_altura()


class FormularioFisioterapia:
    """
    Formulário profissional de avaliação fisioterapêutica com layout moderno,
    responsivo e recursos avançados de usabilidade.
    """
    def __init__(self, parent):
        """Inicializa o formulário"""
        # Criar frame principal
        self.frame = tk.Frame(parent, bg=CORES["fundo"])
        parent.add(self.frame, text="Evaluación")
        
        # Obter cores do arquivo de configurações
        self.cores = CORES
        
        # Número de colunas para layout responsivo
        self.num_colunas = CONFIG_FORMULARIO["num_colunas"]
        
        # Criar sistema de rolagem
        self.criar_sistema_rolagem()
        
        # Armazenar campos de formulário
        self.campos = {}
        self.checkbuttons = []
        self.radio_buttons = {}
        
        # Rastrear alterações para perguntar antes de sair
        self.modificado = False
        
        # Configurar o formulário
        self.configurar_formulario()
    
    def criar_sistema_rolagem(self):
        """Cria o sistema de rolagem para o formulário"""
        # Frame principal com rolagem
        self.frame_principal = tk.Frame(self.frame, bg=self.cores["fundo"])
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Criar canvas e scrollbar
        self.canvas = tk.Canvas(self.frame_principal, bg=self.cores["fundo"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.frame_principal, orient="vertical", command=self.canvas.yview)
        
        # Configurar canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout dos componentes
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para conteúdo
        self.frame_conteudo = tk.Frame(self.canvas, bg=self.cores["secao_bg"], padx=TAMANHOS["padding_padrao"], pady=TAMANHOS["padding_padrao"])
        self.frame_conteudo.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Criar janela para conteúdo
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.frame_conteudo, 
            anchor="nw",
            width=self.canvas.winfo_width()
        )
        
        # Ajustar largura do conteúdo quando o canvas for redimensionado
        self.canvas.bind('<Configure>', self._ao_configurar_canvas)
        
        # Configurar eventos de scroll
        self.configurar_eventos_scroll()
    
    def _ao_configurar_canvas(self, evento):
        """Ajusta o tamanho da janela do conteúdo quando o canvas é redimensionado"""
        # Definir a largura do frame de conteúdo para a largura atual do canvas
        self.canvas.itemconfig(self.canvas_window, width=evento.width)
    
    def configurar_eventos_scroll(self):
        """Configura os eventos de rolagem do mouse"""
        # Windows/MacOS
        self.canvas.bind_all("<MouseWheel>", self._ao_rolar_mouse_windows)
        # Linux
        self.canvas.bind_all("<Button-4>", self._ao_rolar_mouse_linux_cima)
        self.canvas.bind_all("<Button-5>", self._ao_rolar_mouse_linux_baixo)
    
    def _ao_rolar_mouse_windows(self, evento):
        """Trata evento de rolagem no Windows/MacOS"""
        self.canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")
    
    def _ao_rolar_mouse_linux_cima(self, evento):
        """Trata evento de rolagem para cima no Linux"""
        self.canvas.yview_scroll(-1, "units")

    def _ao_rolar_mouse_linux_baixo(self, evento):
        """Trata evento de rolagem para baixo no Linux"""
        self.canvas.yview_scroll(1, "units")
    
    def configurar_formulario(self):
        """Configura e preenche o formulário com todos os campos"""
        # Configurar as colunas para layout responsivo
        for i in range(self.num_colunas):
            self.frame_conteudo.columnconfigure(i, weight=1)
        
        # Cabeçalho do formulário
        self.criar_cabecalho()
        
        # Criar as seções do formulário utilizando frames
        linha = self.criar_secao_historial_paciente(1)
        linha = self.criar_secao_historia_clinica(linha)
        linha = self.criar_secao_evaluacion_fisica(linha)
        linha = self.criar_secao_pruebas_especificas(linha)
        linha = self.criar_secao_mediciones_escalas(linha)
        linha = self.criar_secao_diagnosticos(linha)
        linha = self.criar_secao_plan_tratamiento(linha)
        linha = self.criar_secao_seguimiento(linha)
        
        # Botões de ação
        self.criar_botoes_acao(linha)
    
    def criar_cabecalho(self):
        """Cria o cabeçalho do formulário com logotipo"""
        # Frame do cabeçalho
        frame_cabecalho = tk.Frame(self.frame_conteudo, bg=self.cores["titulo_bg"])
        frame_cabecalho.grid(row=0, column=0, columnspan=self.num_colunas, sticky="ew", padx=5, pady=5)
        
        # Título e subtítulo
        frame_textos = tk.Frame(frame_cabecalho, bg=self.cores["titulo_bg"])
        frame_textos.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=15)
        
        subtitulo = tk.Label(
            frame_textos, 
            text="Formulario profesional de evaluación", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=("Segoe UI", 19, "bold")
            #font=FONTES["secao"]
        )
        subtitulo.pack(anchor="w", pady=(5, 0))
        
        # Data e hora à direita
        data_atual = datetime.datetime.now().strftime("%d/%m/%Y")
        label_data = tk.Label(
            frame_cabecalho, 
            text=f"Fecha: {data_atual}", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 10)
        )
        label_data.pack(side=tk.RIGHT, padx=20)
    
    def criar_secao_historial_paciente(self, linha_inicio):
        """Cria a seção de Histórico do Paciente com layout ajustado"""
        linha = linha_inicio
        
        # Frame da seção (com borda e sombra)
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="HISTORIAL PACIENTE", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Conteúdo da seção - usar um layout de tabela com grid
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"], padx=15, pady=15)
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid mais preciso
        # Coluna 0: Label Nome
        # Coluna 1-6: Campo Nome (span 6)
        frame_conteudo_secao.columnconfigure(0, weight=0, minsize=120)  # Label
        frame_conteudo_secao.columnconfigure(1, weight=5)               # Campo grande
        frame_conteudo_secao.columnconfigure(2, weight=0, minsize=60)   # Label secundário
        frame_conteudo_secao.columnconfigure(3, weight=2)               # Campo pequeno
        
        # --- PRIMEIRA LINHA: NOME COMPLETO ---
        label_nome = tk.Label(
            frame_conteudo_secao, 
            text="Nombre Completo", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_nome.grid(row=0, column=0, padx=(0, 5), pady=(0, 10), sticky="w")
        
        campo_nome = CampoTextoAutoExpansivel(
            frame_conteudo_secao, 
            width=50, 
            height=1, 
            max_height=3, 
            bg=self.cores["campo_bg"],
            placeholder="Ingrese nombre completo..."
        )
        campo_nome.grid(row=0, column=1, columnspan=3, padx=0, pady=(0, 10), sticky="ew")
        campo_nome.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Nombre Completo"] = campo_nome
        
        # --- SEGUNDA LINHA: IDADE E GÊNERO ---
        # Idade
        label_idade = tk.Label(
            frame_conteudo_secao, 
            text="Edad", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_idade.grid(row=1, column=0, padx=(0, 5), pady=(0, 10), sticky="w")
        
        campo_idade = CampoTextoAutoExpansivel(
            frame_conteudo_secao, 
            width=10, 
            height=1, 
            max_height=1, 
            bg=self.cores["campo_bg"],
            placeholder="Ingrese edad..."
        )
        campo_idade.grid(row=1, column=1, padx=(0, 20), pady=(0, 10), sticky="w")
        campo_idade.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Edad"] = campo_idade
        
        # Gênero (diretamente ao lado da idade)
        label_genero = tk.Label(
            frame_conteudo_secao, 
            text="Genero", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_genero.grid(row=1, column=2, padx=(0, 5), pady=(0, 10), sticky="w")
        
        campo_genero = CampoTextoAutoExpansivel(
            frame_conteudo_secao, 
            width=20, 
            height=1, 
            max_height=1, 
            bg=self.cores["campo_bg"],
            placeholder="Ingrese genero..."
        )
        campo_genero.grid(row=1, column=3, padx=0, pady=(0, 10), sticky="ew")
        campo_genero.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Genero"] = campo_genero
        
        # --- TERCEIRA LINHA: CONTATO E DATA DE NASCIMENTO ---
        # Contato
        label_contato = tk.Label(
            frame_conteudo_secao, 
            text="Contacto", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_contato.grid(row=2, column=0, padx=(0, 5), pady=(0, 10), sticky="w")
        
        campo_contato = CampoTextoAutoExpansivel(
            frame_conteudo_secao, 
            width=30, 
            height=1, 
            max_height=1, 
            bg=self.cores["campo_bg"],
            placeholder="Ingrese contacto..."
        )
        campo_contato.grid(row=2, column=1, padx=(0, 20), pady=(0, 10), sticky="ew")
        campo_contato.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Contacto"] = campo_contato
        
        # Data de nascimento (imediatamente após o contato)
        label_data = tk.Label(
            frame_conteudo_secao, 
            text="Fecha Nasc.", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_data.grid(row=2, column=2, padx=(0, 5), pady=(0, 10), sticky="w")

        # Usar bg em vez de background para DateEntry
        data_nasc = DateEntry(
            frame_conteudo_secao, 
            width=12, 
            bg=self.cores["secundaria"],
            fg='white', 
            date_pattern='dd/mm/yyyy',
            borderwidth=0
        )
        data_nasc.grid(row=2, column=3, padx=0, pady=(0, 10), sticky="w")
        self.campos["Fecha Nasc."] = data_nasc
        
        # --- QUARTA LINHA: ÁREA DE CONSULTA ---
        label_area = tk.Label(
            frame_conteudo_secao, 
            text="Área de consulta", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_area.grid(row=3, column=0, padx=(0, 5), pady=(0, 10), sticky="w")
        
        campo_area = CampoTextoAutoExpansivel(
            frame_conteudo_secao, 
            width=50, 
            height=1, 
            max_height=2, 
            bg=self.cores["campo_bg"],
            placeholder="Ingrese área de consulta..."
        )
        campo_area.grid(row=3, column=1, columnspan=3, padx=0, pady=(0, 10), sticky="ew")
        campo_area.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Área de consulta"] = campo_area
        
        # --- QUINTA LINHA: ALERGIAS ---
        label_alergias = tk.Label(
            frame_conteudo_secao, 
            text="Alergias", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_alergias.grid(row=4, column=0, padx=(0, 5), pady=0, sticky="nw")
        
        campo_alergias = CampoTextoAutoExpansivel(
            frame_conteudo_secao, 
            width=50, 
            height=2, 
            max_height=4, 
            bg=self.cores["campo_bg"],
            placeholder="Ingrese alergias..."
        )
        campo_alergias.grid(row=4, column=1, columnspan=3, padx=0, pady=0, sticky="ew")
        campo_alergias.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Alergias"] = campo_alergias
        
        return linha
    
    def criar_secao_historia_clinica(self, linha_inicio):
        """Cria a seção de História Clínica"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="HISTORIA CLÍNICA", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Conteúdo da seção
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Campos com área de texto maior
        campos = [
            ("Motivo de consulta", 0),
            ("Antecedentes", 1),
            ("Efermedad actual", 2),
            ("Cirurgías previas", 3),
            ("Medicamentos actuales", 4)
        ]
        
        # Criar campos com mais altura
        for campo, linha_local in campos:
            label = tk.Label(
                frame_conteudo_secao, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=5, pady=8, sticky="nw")
            
            # Campo de texto expansível com placeholder
            campo_texto = CampoTextoAutoExpansivel(
                frame_conteudo_secao, 
                width=80,  # Mais largo
                height=3,  # Mais alto
                max_height=8,
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {campo.lower()}...",
                placeholder_color="#AAAAAA"
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=8, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        return linha
    
    def criar_secao_evaluacion_fisica(self, linha_inicio):
        """Cria a seção de Avaliação Física com todas as subseções e labels fora dos campos"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="EVALUACIÓN FÍSICA", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Notebook para organizar subseções em abas
        notebook_avaliacao = ttk.Notebook(frame_secao)
        notebook_avaliacao.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 0. Frame para Exáme Físico
        frame_exame = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_exame, text="EXÁME FISICO")
        
        # Configurar layout de grid para este frame
        frame_exame.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_exame.columnconfigure(1, weight=1)              # Coluna para campos
        
        # Título da subseção com linha separadora abaixo
        label_titulo_exame = tk.Label(
            frame_exame, 
            text="EXÁME FISICO", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_exame.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 5), sticky="w")
        
        # Linha separadora para o título
        separador_exame = tk.Frame(frame_exame, height=1, bg="#cccccc")
        separador_exame.grid(row=0, column=0, columnspan=2, padx=5, pady=(30, 10), sticky="ew")
        
        # Parâmetros vitais com labels fora dos campos
        parametros_vitais = [
            ("PA", 1, "mmHg"),
            ("Pulso", 2, "lpm"),
            ("Talla", 3, "cm"),
            ("Peso", 4, "kg"),
            ("T", 5, "°C"),
            ("FR", 6, "rpm"),
            ("Sat.O2", 7, "%")
        ]
        
        for parametro, linha_local, unidade in parametros_vitais:
            # Label à esquerda
            label = tk.Label(
                frame_exame, 
                text=f"{parametro}:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(5, 10), pady=5, sticky="w")
            
            # Criar um frame contenedor para o campo e a unidade
            frame_campo = tk.Frame(frame_exame, bg=self.cores["secao_bg"])
            frame_campo.grid(row=linha_local, column=1, padx=5, pady=5, sticky="w")
            
            # Campo de texto dentro do frame contenedor
            campo_texto = CampoTextoAutoExpansivel(
                frame_campo, 
                width=30, 
                height=1, 
                max_height=1, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {parametro}..."
            )
            campo_texto.pack(side=tk.LEFT, fill=tk.X)
            
            # Label da unidade à direita do campo, no mesmo frame
            label_unidade = tk.Label(
                frame_campo, 
                text=unidade, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"],
                padx=5
            )
            label_unidade.pack(side=tk.LEFT)
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[parametro] = campo_texto
        
        # Adicionar linha separadora após os parâmetros vitais
        separador_params = tk.Frame(frame_exame, height=1, bg="#cccccc")
        separador_params.grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        
        # Campos IDx e Conducta
        campos_adicionales = [
            ("IDx", 9),
            ("Conducta", 10)
        ]
        
        for campo, linha_local in campos_adicionales:
            # Label à esquerda
            label = tk.Label(
                frame_exame, 
                text=f"{campo}:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(5, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_exame, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {campo}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
            
        # RESTO DO CÓDIGO PERMANECE IGUAL
        # 1. Frame para Inspeção e Palpação
        frame_inspeccion = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_inspeccion, text="Inspección y Palpación")
        
        # Configurar layout de grid para este frame
        frame_inspeccion.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_inspeccion.columnconfigure(1, weight=1)              # Coluna para campos
        
        # 1.1 Título da Inspeção
        label_titulo_inspeccion = tk.Label(
            frame_inspeccion, 
            text="1. Inspección", 
            bg=self.cores["secao_bg"],
            fg="#ffffff", # Texto branco para contraste no fundo verde
            font=FONTES["secao"]
        )
        label_titulo_inspeccion.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 5), sticky="w")
        
        # Linha separadora
        separador_inspeccion = tk.Frame(frame_inspeccion, height=1, bg="#cccccc")
        separador_inspeccion.grid(row=0, column=0, columnspan=2, padx=5, pady=(30, 10), sticky="ew")
        
        # Campos de Inspeção com labels fora dos campos
        campos_inspecao = [
            ("Postura", 1),
            ("Simetría corporal", 2),
            ("Deformidades aparentes", 3)
        ]
        
        for campo, linha_local in campos_inspecao:
            # Label à esquerda
            label = tk.Label(
                frame_inspeccion, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(5, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_inspeccion, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        # 1.2 Título da Palpação com linha separadora
        separador_palpacion = tk.Frame(frame_inspeccion, height=1, bg="#cccccc")
        separador_palpacion.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        
        label_titulo_palpacion = tk.Label(
            frame_inspeccion, 
            text="2. Palpación", 
            bg=self.cores["secao_bg"],
            fg="#ffffff", # Texto branco para contraste
            font=FONTES["secao"]
        )
        label_titulo_palpacion.grid(row=4, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="w")
        
        # Campos de Palpação
        campos_palpacao = [
            ("Puntos dolorosos", 5),
            ("Tensión muscular", 6)
        ]
        
        for campo, linha_local in campos_palpacao:
            # Label à esquerda
            label = tk.Label(
                frame_inspeccion, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(5, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_inspeccion, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        # Continuar com as outras abas... (mantenha o código existente para as outras abas)
        # 2. Frame para Coluna Vertebral
        frame_columna = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_columna, text="Columna Vertebral")
        
        # Configurar layout de grid para este frame
        frame_columna.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_columna.columnconfigure(1, weight=1)              # Coluna para campos
        
        # Título da subseção com linha separadora
        label_titulo_columna = tk.Label(
            frame_columna, 
            text="Evaluación de la Columna Vertebral", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_columna.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 5), sticky="w")
        
        # Linha separadora
        separador_columna = tk.Frame(frame_columna, height=1, bg="#cccccc")
        separador_columna.grid(row=0, column=0, columnspan=2, padx=5, pady=(30, 10), sticky="ew")
        
        # Campos da Coluna Vertebral
        campos_coluna = [
            ("Curvas Fisiológicas", 1),
            ("Presencia de Escoliosis", 2),
            ("Cifosis o Lordosis", 3)
        ]
        
        for campo, linha_local in campos_coluna:
            # Label à esquerda
            label = tk.Label(
                frame_columna, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(5, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_columna, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        # 3. Frame para Mobilidade Articular
        frame_movilidad = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_movilidad, text="Movilidad Articular")
        
        # Configurar layout de grid para este frame
        frame_movilidad.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_movilidad.columnconfigure(1, weight=1)              # Coluna para campos
        
        # Título da subseção
        label_titulo_movilidad = tk.Label(
            frame_movilidad, 
            text="Movilidad Articular", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_movilidad.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="w")
        
        # Rango de movimento
        label_rango = tk.Label(
            frame_movilidad, 
            text="Rango de movimiento:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subsecao"]
        )
        label_rango.grid(row=1, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="w")
        
        # Campos do Rango de movimento
        campos_rango = [
            ("Activo", 2),
            ("Pasivo", 3)
        ]
        
        for campo, linha_local in campos_rango:
            # Label indentada à esquerda
            label = tk.Label(
                frame_movilidad, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(25, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_movilidad, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre movimiento {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[f"Movimiento {campo}"] = campo_texto
        
        # Avaliação das articulações
        label_articul = tk.Label(
            frame_movilidad, 
            text="Evaluación de las articulaciones afectadas:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subsecao"]
        )
        label_articul.grid(row=4, column=0, columnspan=2, padx=5, pady=(15, 10), sticky="w")
        
        campo_art = CampoTextoAutoExpansivel(
            frame_movilidad,
            width=80,
            height=4,
            max_height=8,
            bg=self.cores["campo_bg"],
            placeholder="Describa la evaluación de las articulaciones afectadas..."
        )
        campo_art.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Vincular evento de modificação
        campo_art.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["Evaluación de articulaciones"] = campo_art
        
        # 4. Frame para Força Muscular
        frame_fuerza = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_fuerza, text="Fuerza Muscular")
        
        # Configurar layout de grid para este frame
        frame_fuerza.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_fuerza.columnconfigure(1, weight=1)              # Coluna para campos
        
        # Título da subseção
        label_titulo_fuerza = tk.Label(
            frame_fuerza, 
            text="Fuerza Muscular", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_fuerza.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="w")
        
        # Campo para avaliação de grupos musculares
        label_grupos = tk.Label(
            frame_fuerza, 
            text="Evaluación de grupos musculares específicos:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        label_grupos.grid(row=1, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="w")
        
        campo_musculos = CampoTextoAutoExpansivel(
            frame_fuerza,
            width=80,
            height=4,
            max_height=8,
            bg=self.cores["campo_bg"],
            placeholder="Describa la evaluación de los grupos musculares específicos..."
        )
        campo_musculos.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Vincular evento de modificação
        campo_musculos.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["Evaluación de grupos musculares"] = campo_musculos
        
        # Níveis de força
        label_grados = tk.Label(
            frame_fuerza, 
            text="Grados de fuerza según la escala establecida:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 18, 'bold')
        )
        label_grados.grid(row=3, column=0, columnspan=2, padx=5, pady=(15, 10), sticky="w")
        
        # Opções com checkbuttons
        opcoes_forca = [
            "Grado 0: Ausencia de contracción",
            "Grado 1: Contracción detectable, pero no mueve la articulación",
            "Grado 2: Movimiento activo, pero no contra la gravedad",
            "Grado 3: Movimiento activo contra la gravedad, pero no con resistencia",
            "Grado 4: Movimiento activo contra resistencia moderada",
            "Grado 5: Movimiento activo contra resistencia completa"
        ]
        
        # Criar frame para checkbuttons com estilo
        frame_check = tk.Frame(frame_fuerza, bg=self.cores["secao_bg"], padx=5, pady=5)
        frame_check.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Criar checkbuttons em uma lista vertical
        for i, opcao in enumerate(opcoes_forca):
            var = tk.BooleanVar()
            
            check = tk.Checkbutton(
                frame_check, 
                text=opcao, 
                variable=var,
                command=self.marcar_modificado,
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                selectcolor=self.cores["secao_bg"],
                activebackground=self.cores["secao_bg"],
                activeforeground=self.cores["texto_destaque"],
                font=FONTES["checkbox_texto"]
            )
            check.grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            self.checkbuttons.append((check, var))

        # 5. Frame para Avaliação Neuromuscular
        frame_neuro = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_neuro, text="Evaluación Neuromuscular")
        
        # Configurar layout de grid para este frame
        frame_neuro.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_neuro.columnconfigure(1, weight=1)              # Coluna para campos
        
        # Título da subseção
        label_titulo_neuro = tk.Label(
            frame_neuro, 
            text="Evaluación Neuromuscular", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_neuro.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="w")
        
        # Campos da Avaliação Neuromuscular
        campos_neuro = [
            ("Reflejos", 1),
            ("Coordinación motora", 2),
            ("Equilibrio", 3)
        ]
        
        for campo, linha_local in campos_neuro:
            # Label à esquerda
            label = tk.Label(
                frame_neuro, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(5, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_neuro, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
            
        # 6. Frame para Avaliação Funcional
        frame_funcional = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_funcional, text="Evaluación Funcional")
        
        # Configurar layout de grid para este frame
        frame_funcional.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_funcional.columnconfigure(1, weight=1)              # Coluna para campos
        
        # Título da subseção
        label_titulo_funcional = tk.Label(
            frame_funcional, 
            text="Evaluación Funcional", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_funcional.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="w")
        
        # Campos da Avaliação Funcional
        campos_funcional = [
            ("Capacidad para realizar actividades diarias", 1), 
            ("Limitaciones y dificultades", 2)
        ]
        
        for campo, linha_local in campos_funcional:
            # Label à esquerda
            label = tk.Label(
                frame_funcional, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(5, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_funcional, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        # 7. Frame para Coordenação
        frame_coordinacion = tk.Frame(notebook_avaliacao, bg=self.cores["secao_bg"], padx=10, pady=10)
        notebook_avaliacao.add(frame_coordinacion, text="Coordinación")
        
        # Configurar layout de grid para este frame
        frame_coordinacion.columnconfigure(0, weight=0, minsize=120)  # Coluna para labels
        frame_coordinacion.columnconfigure(1, weight=1)              # Coluna para campos
        
        # Título da subseção
        label_titulo_coordinacion = tk.Label(
            frame_coordinacion, 
            text="Evaluación de la Coordinación", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_coordinacion.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 15), sticky="w")
        
        # Coordenação motora fina
        label_motora_fina = tk.Label(
            frame_coordinacion, 
            text="Pruebas de coordinación motora fina:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        label_motora_fina.grid(row=1, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="w")
        
        # Campos para coordenação fina
        campos_fina = [
            ("Ejercicios con dedos", 2),
            ("Precisión en movimientos", 3)
        ]
        
        for campo, linha_local in campos_fina:
            # Label à esquerda, indentada
            label = tk.Label(
                frame_coordinacion, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(25, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_coordinacion, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        # Coordenação motora grossa
        label_motora_gruesa = tk.Label(
            frame_coordinacion, 
            text="Pruebas de coordinación motora gruesa:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"] 
        )
        label_motora_gruesa.grid(row=4, column=0, columnspan=2, padx=5, pady=(15, 10), sticky="w")
        
        # Campos para coordenação grossa
        campos_gruesa = [
            ("Marcha", 5),
            ("Equilibrio Dinámico", 6)
        ]
        
        for campo, linha_local in campos_gruesa:
            # Label à esquerda, indentada
            label = tk.Label(
                frame_coordinacion, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label.grid(row=linha_local, column=0, padx=(25, 10), pady=5, sticky="w")
            
            # Campo de texto
            campo_texto = CampoTextoAutoExpansivel(
                frame_coordinacion, 
                width=60, 
                height=2, 
                max_height=5, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        return linha

    def criar_secao_pruebas_especificas(self, linha_inicio):
        """Cria a seção de Testes Específicos"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"])
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="PRUEBAS ESPECÍFICAS", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Conteúdo da seção com visual de cards
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configurar colunas para layout em grade
        for i in range(3):  # 3 colunas para os cards
            frame_conteudo_secao.columnconfigure(i, weight=1)
        
        # Criar três cards lado a lado
        campos = [
            ("Pruebas ortopédicas", 0),
            ("Pruebas neurológicas", 1),
            ("Pruebas de estabilidad", 2)
        ]
        
        for campo, col in campos:
            # Frame do card
            card = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"], padx=5, pady=5)
            card.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
            
            # Título do card como texto externo
            label = tk.Label(
            card, 
            text=campo, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["cabecalho_card"]  # Usando a nova fonte maior
            )
            label.pack(anchor="w", padx=5, pady=5)
            
            # Campo de texto com altura maior
            campo_texto = CampoTextoAutoExpansivel(
                card, 
                width=30,
                height=5,
                max_height=10,
                bg=self.cores["campo_bg"],
                placeholder=f"Detalles de {campo.lower()}..."
            )
            campo_texto.pack(fill=tk.X, expand=True, padx=5, pady=5)
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        return linha
    
    def criar_secao_mediciones_escalas(self, linha_inicio):
        """Cria a seção de Medições e Escalas"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"])
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="MEDICIONES Y ESCALAS", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Conteúdo da seção
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Frame para a escala EVA com visual moderno
        frame_eva_container = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_eva_container.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Label principal como texto externo
        label_principal = tk.Label(
            frame_eva_container, 
            text="(EVA) Escala Visual Analógica del Dolor", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 16, 'bold')  # Aumentado para 16
        )
        label_principal.pack(anchor="w", padx=5, pady=5)
        
        # Descrição da escala
        descricao = tk.Label(
            frame_eva_container,
            text="Seleccione el nivel de dolor del paciente en la escala de 0 a 10:",
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subsecao"]
        )
        descricao.pack(anchor="w", padx=5, pady=5)
        
        # Frame para a escala EVA com design melhorado
        frame_eva = tk.Frame(frame_eva_container, bg=self.cores["secao_bg"])
        frame_eva.pack(fill=tk.X, expand=True, padx=5, pady=10)
        
        # Labels para os extremos da escala
        frame_legendas = tk.Frame(frame_eva, bg=self.cores["secao_bg"])
        frame_legendas.pack(fill=tk.X, expand=True, padx=5, pady=0)
        
        label_zero = tk.Label(
            frame_legendas, 
            text="Sin dolor", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 14, 'bold')  # Aumentado para 14
        )
        label_zero.pack(side=tk.LEFT)
        
        label_diez = tk.Label(
            frame_legendas, 
            text="Dolor máximo", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 14, 'bold')  # Aumentado para 14
        )
        label_diez.pack(side=tk.RIGHT)
        
        # Frame para a escala e valor
        frame_escala_valor = tk.Frame(frame_eva, bg=self.cores["secao_bg"])
        frame_escala_valor.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Criar escala visual usando Scale widget do tk
        var_escala = tk.DoubleVar()
        escala_eva = tk.Scale(
            frame_escala_valor, 
            from_=0, 
            to=10, 
            orient=tk.HORIZONTAL,
            length=400,
            sliderlength=30,
            showvalue=0,  # Não mostrar valor na escala
            resolution=1,
            variable=var_escala,
            bg=self.cores["secao_bg"],
            highlightthickness=0,
            troughcolor="#DDDDDD",
            width=20,  # Aumentar largura do slider
            activebackground=self.cores["secundaria"]
        )
        escala_eva.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Frame para valor com estilo
        frame_valor = tk.Frame(frame_escala_valor, bg=self.cores["secao_bg"], padx=5, pady=5)
        frame_valor.pack(side=tk.LEFT)
        
        # Label para mostrar o valor
        valor_eva = tk.Label(
            frame_valor, 
            text="0", 
            width=2, 
            font=('Segoe UI', 18, 'bold'),  # Aumentado para 18
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"]
        )
        valor_eva.pack()
        
        # Função para atualizar o valor
        def atualizar_valor_eva(evento):
            valor = int(escala_eva.get())
            valor_eva.config(text=str(valor))
            self.marcar_modificado()
        
        escala_eva.bind("<Motion>", atualizar_valor_eva)
        escala_eva.bind("<ButtonRelease-1>", atualizar_valor_eva)
        
        # Armazenar referência
        self.campos["escala_eva"] = escala_eva
        
        # Área para observações adicionais
        label_observaciones = tk.Label(
            frame_eva_container, 
            text="Observaciones adicionales sobre el dolor:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 14)  # Aumentado para 14
        )
        label_observaciones.pack(anchor="w", padx=5, pady=5)
        
        # Campo de texto para observações
        observaciones = CampoTextoAutoExpansivel(
            frame_eva_container, 
            width=80,
            height=3,
            max_height=6,
            bg=self.cores["campo_bg"],
            placeholder="Describa las características del dolor (tipo, localización, factores agravantes, etc.)"
        )
        observaciones.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Vincular evento de modificação
        observaciones.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["observaciones_dolor"] = observaciones
        
        return linha
    
    def criar_secao_diagnosticos(self, linha_inicio):
        """Cria a seção de Diagnósticos Fisioterapêuticos"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="DIAGNÓSTICOS", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Conteúdo da seção
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Campos
        campos = [
            ("Resumen del problema", 0),
            ("Objetivos del tratamiento", 1)
        ]
        
        for campo, linha_local in campos:
            label = tk.Label(
                frame_conteudo_secao, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["texto_secao"]  # Usando fonte maior definida no config
            )
            label.grid(row=linha_local, column=0, padx=5, pady=8, sticky="nw")
            
            # Campo de texto expansível com placeholder
            campo_texto = CampoTextoAutoExpansivel(
                frame_conteudo_secao, 
                width=80,
                height=4,
                max_height=8,
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {campo.lower()}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=8, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto
        
        return linha
    
    def criar_secao_plan_tratamiento(self, linha_inicio):
        """Cria a seção de Plano de Tratamento"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="PLAN DE TRATAMIENTO", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Conteúdo da seção
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Sessões por semana com interface melhorada
        frame_frecuencia = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_frecuencia.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Título como texto externo
        label_frecuencia = tk.Label(
            frame_frecuencia, 
            text="Frecuencia y duración de las sesiones", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["texto_secao"]  # Usando fonte maior
        )
        label_frecuencia.pack(anchor="w", padx=5, pady=5)
        
        # Frame para selecionar frequência e duração
        frame_selecao = tk.Frame(frame_frecuencia, bg=self.cores["secao_bg"])
        frame_selecao.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Seletor de frequência (sessões por semana)
        label_sesiones = tk.Label(
            frame_selecao, 
            text="Sesiones por semana:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_sesiones.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Usar OptionMenu em vez de Combobox
        var_sesiones = tk.StringVar(value="2")
        opcoes_sesiones = OPCOES["sesiones_semana"]  # Usando do config.py
        
        cbox_sesiones = tk.OptionMenu(
            frame_selecao, 
            var_sesiones, 
            *opcoes_sesiones
        )
        cbox_sesiones.config(
            width=8, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            activebackground=self.cores["button_bg"],
            activeforeground=self.cores["texto_destaque"],
            highlightthickness=0,
            font=FONTES["campo"]  # Adicionar fonte aqui
        )
        cbox_sesiones.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Seletor de duração da sessão
        label_duracion = tk.Label(
            frame_selecao, 
            text="Duración de cada sesión:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_duracion.grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        
        # Usar OptionMenu em vez de Combobox
        var_duracion = tk.StringVar(value="60 minutos")
        opcoes_duracion = OPCOES["duracion_sesion"]  # Usando do config.py
        
        cbox_duracion = tk.OptionMenu(
            frame_selecao, 
            var_duracion, 
            *opcoes_duracion
        )
        cbox_duracion.config(
            width=10, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            activebackground=self.cores["button_bg"],
            activeforeground=self.cores["texto_destaque"],
            highlightthickness=0,
            font=FONTES["campo"]  # Adicionar fonte aqui
        )
        cbox_duracion.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Seletor de duração da sessão
        label_duracion = tk.Label(
            frame_selecao, 
            text="Duración de cada sesión:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_duracion.grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        
        # Usar OptionMenu em vez de Combobox
        var_duracion = tk.StringVar(value="60 minutos")
        opcoes_duracion = ["30 minutos", "45 minutos", "60 minutos", "90 minutos", "Otra"]
        
        cbox_duracion = tk.OptionMenu(
            frame_selecao, 
            var_duracion, 
            *opcoes_duracion
        )
        cbox_duracion.config(
            width=10, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            activebackground=self.cores["button_bg"],
            activeforeground=self.cores["texto_destaque"],
            highlightthickness=0
        )
        cbox_duracion.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Armazenar referências
        self.campos["sesiones_semana"] = var_sesiones
        self.campos["duracion_sesion"] = var_duracion
        
        # Observações sobre frequência
        label_obs_freq = tk.Label(
            frame_frecuencia, 
            text="Observaciones adicionales:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_obs_freq.pack(anchor="w", padx=5, pady=5)
        
        obs_frecuencia = CampoTextoAutoExpansivel(
            frame_frecuencia,
            width=80,
            height=2,
            max_height=4,
            bg=self.cores["campo_bg"],
            placeholder="Detalles sobre el programa de tratamiento..."
        )
        obs_frecuencia.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Vincular evento de modificação
        obs_frecuencia.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["obs_frecuencia"] = obs_frecuencia
        
        # Exercícios recomendados
        frame_ejercicios = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_ejercicios.grid(row=1, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="ew")
        
        # Título como texto externo
        label_ejercicios = tk.Label(
            frame_ejercicios, 
            text="Ejercicios recomendados para el hogar", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        label_ejercicios.pack(anchor="w", padx=5, pady=5)
        
        ejercicios = CampoTextoAutoExpansivel(
            frame_ejercicios,
            width=80,
            height=6,
            max_height=10,
            bg=self.cores["campo_bg"],
            placeholder="Describa los ejercicios que el paciente debe realizar en casa..."
        )
        ejercicios.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Vincular evento de modificação
        ejercicios.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["Ejercicios recomendados"] = ejercicios
        
        return linha
    
    def criar_secao_seguimiento(self, linha_inicio):
        """Cria a seção de Acompanhamento e Reavaliação"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"])
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="SEGUIMIENTO Y REEVALUACIÓN", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Conteúdo da seção
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configurar layout para 2 colunas
        frame_conteudo_secao.columnconfigure(0, weight=1)
        frame_conteudo_secao.columnconfigure(1, weight=1)
        
        # Programação de sessões - Card à esquerda
        frame_programacion = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_programacion.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Título como texto externo - AQUI AUMENTAMOS A FONTE
        label_programacion = tk.Label(
            frame_programacion, 
            text="Programación de sesiones de seguimientos", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 22, 'bold')
        )
        label_programacion.pack(anchor="w", padx=5, pady=5)

        # Data da próxima avaliação (adicione esta seção)
        frame_fecha = tk.Frame(frame_programacion, bg=self.cores["secao_bg"])
        frame_fecha.pack(fill=tk.X, expand=True, padx=5, pady=5)

        label_fecha = tk.Label(
            frame_fecha, 
            text="Próxima evaluación:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_fecha.pack(side=tk.LEFT, padx=5)

        # Usando 'bg' para o DateEntry
        fecha_eval = DateEntry(
            frame_fecha, 
            width=12, 
            bg=self.cores["secundaria"],
            fg='white', 
            date_pattern='dd/mm/yyyy',
            borderwidth=0
        )
        fecha_eval.pack(side=tk.LEFT, padx=5)

        # Armazenar referência
        self.campos["fecha_prox_eval"] = fecha_eval

        # Campo de texto para detalhes
        programacion = CampoTextoAutoExpansivel(
            frame_programacion,
            width=40,
            height=5,
            max_height=8,
            bg=self.cores["campo_bg"],
            placeholder="Detalles sobre la programación de las sesiones de seguimiento..."
        )
        programacion.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        
        # Critérios para revisão - Card à direita
        frame_criterios = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_criterios.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Título como texto externo - AQUI AUMENTAMOS A FONTE
        label_criterios = tk.Label(
            frame_criterios, 
            text="Criterios para revisión", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["cabecalho_card"]  # Usando a nova fonte maior
        )
        label_criterios.pack(anchor="w", padx=5, pady=5)
        
        # RadioButtons para os critérios
        frame_radio = tk.Frame(frame_criterios, bg=self.cores["secao_bg"], padx=5, pady=5)
        frame_radio.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Variável para armazenar a seleção
        var_criterio = tk.StringVar(value="mejora")
        self.radio_buttons["criterio_revision"] = var_criterio
        
        criterios = [
            ("Mejora del dolor o movilidad", "mejora"),
            ("Objetivos funcionales alcanzados", "objetivos"),
            ("Tiempo específico transcurrido", "tiempo"),
            ("Otro criterio", "otro")
        ]
        
        # Criar os radio buttons
        for i, (texto, valor) in enumerate(criterios):
            radio = tk.Radiobutton(
                frame_radio,
                text=texto,
                variable=var_criterio,
                value=valor,
                command=self.marcar_modificado,
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                selectcolor=self.cores["secao_bg"],
                activebackground=self.cores["secao_bg"],
                activeforeground=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            radio.pack(anchor="w", padx=5, pady=2)
        
        return linha
    
    def criar_botoes_acao(self, linha_inicio):
        """Cria os botões de ação do formulário"""
        linha = linha_inicio
        
        # Frame para os botões com estilo
        frame_botoes = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_botoes.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=15
        )
        
        # Frame interno para centralizar os botões
        frame_interno = tk.Frame(frame_botoes, bg=self.cores["secao_bg"])
        frame_interno.pack(pady=10)
        
        # Botões com estilo moderno
        
        # Botão de salvar
        btn_salvar = tk.Button(
            frame_interno, 
            text="   Guardar Evaluación   ", 
            command=self.salvar_formulario,
            bg=self.cores["sucesso"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            relief=tk.RAISED,
            padx=10,
            pady=5,
            activebackground="#27ae60",
            activeforeground=self.cores["texto_destaque"]
        )
        btn_salvar.pack(side=tk.LEFT, padx=15)
        
        # Botão de imprimir
        btn_imprimir = tk.Button(
            frame_interno, 
            text="   Imprimir   ", 
            command=self.imprimir_formulario,
            bg=self.cores["secundaria"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            relief=tk.RAISED,
            padx=10,
            pady=5,
            activebackground="#2980b9",
            activeforeground=self.cores["texto_destaque"]
        )
        btn_imprimir.pack(side=tk.LEFT, padx=15)
        
        # Botão de limpar
        btn_limpar = tk.Button(
            frame_interno, 
            text="   Limpiar   ", 
            command=self.confirmar_limpar_formulario,
            bg=self.cores["aviso"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            relief=tk.RAISED,
            padx=10,
            pady=5,
            activebackground="#d35400",
            activeforeground=self.cores["texto_destaque"]
        )
        btn_limpar.pack(side=tk.LEFT, padx=15)

    def criar_titulo(self, texto, linha, col, colspan):
        """Cria um título no formulário"""
        # Frame para criar fundo estilizado com borda arredondada
        frame = tk.Frame(self.frame_conteudo, bg=self.cores["titulo_bg"])
        frame.grid(
            row=linha, 
            column=col, 
            columnspan=colspan, 
            sticky="ew", 
            padx=5, 
            pady=8
        )
        
        # Label do título centralizado
        label = tk.Label(
            frame, 
            text=texto, 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        label.pack(pady=10)
    
    def criar_campo_em_grid(self, parent, texto_label, linha, col, colspan):
        """Cria um campo de texto com etiqueta no grid"""
        # Label à esquerda
        label = tk.Label(
            parent, 
            text=texto_label, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label.grid(row=linha, column=col, padx=10, pady=5, sticky="w")
        
        # Campo de texto expansível
        campo = CampoTextoAutoExpansivel(
            parent, 
            width=40, 
            height=2, 
            max_height=6, 
            bg=self.cores["campo_bg"],
            placeholder=f"Ingrese {texto_label.replace('.', '').replace('*', '').lower()}..."
        )
        
        # Se o colspan for maior que 1, o campo ocupa múltiplas colunas
        if colspan > 1:
            campo.grid(
                row=linha, 
                column=col, 
                columnspan=colspan, 
                padx=10, 
                pady=5, 
                sticky="ew"
            )
        else:
            # Senão, o campo fica na coluna seguinte
            campo.grid(
                row=linha, 
                column=col+1, 
                padx=10, 
                pady=5, 
                sticky="ew"
            )
        
        # Vincular evento de modificação
        campo.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos[texto_label] = campo
        
        return campo
    
    def criar_campo_indentado(self, parent, texto_label, linha, col):
        """Cria um campo indentado para subelementos"""
        # Label indentada à esquerda
        label = tk.Label(
            parent, 
            text=texto_label, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subcampo"]
        )
        label.grid(row=linha, column=col, padx=30, pady=5, sticky="w")
        
        # Campo de texto expansível à direita
        campo = CampoTextoAutoExpansivel(
            parent, 
            width=40, 
            height=2, 
            max_height=6, 
            bg=self.cores["campo_bg"],
            placeholder=f"Ingrese información sobre {texto_label.replace('.', '').replace('*', '').lower()}..."
        )
        campo.grid(row=linha, column=col+1, padx=10, pady=5, sticky="ew")
        
        # Vincular evento de modificação
        campo.texto.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos[texto_label] = campo
        
        return campo
    
    def marcar_modificado(self, evento=None):
        """Marca o formulário como modificado"""
        self.modificado = True
    
    def confirmar_limpar_formulario(self):
        """Confirma antes de limpar o formulário"""
        if self.modificado:
            resposta = messagebox.askyesno(
                "Confirmar", 
                "¿Está seguro que desea limpiar todos los campos? Se perderán los datos no guardados.",
                icon='warning'
            )
            if resposta:
                self.limpar_formulario()
        else:
            self.limpar_formulario()
    
    def limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        # Limpar todos os campos de texto
        for campo in self.campos.values():
            if hasattr(campo, 'limpar'):
                campo.limpar()
            elif isinstance(campo, DateEntry):
                campo.set_date(datetime.datetime.now())
            elif isinstance(campo, tk.Scale):
                campo.set(0)
            elif isinstance(campo, tk.StringVar):
                # Para OptionMenu
                if campo is self.campos.get("sesiones_semana"):
                    campo.set("2")
                elif campo is self.campos.get("duracion_sesion"):
                    campo.set("60 minutos")
                else:
                    campo.set("")
        
        # Desmarcar todos os checkbuttons
        for _, var in self.checkbuttons:
            var.set(False)
        
        # Resetar radio buttons para o valor padrão
        for var_name, var in self.radio_buttons.items():
            if var_name == "criterio_revision":
                var.set("mejora")
            else:
                var.set("")
        
        # Resetar flag de modificação
        self.modificado = False
        
        # Feedback visual com estilo melhorado
        messagebox.showinfo(
            "Limpiar", 
            "Formulario limpiado correctamente.",
            icon='info'
        )
    
    def salvar_formulario(self):
        """Salva os dados do formulário"""
        try:
            # Coletar todos os dados
            dados = {}
            
            # Processar os campos de texto
            for etiqueta, campo in self.campos.items():
                if hasattr(campo, 'obter'):
                    dados[etiqueta] = campo.obter()
                elif isinstance(campo, DateEntry):
                    dados[etiqueta] = campo.get_date().strftime('%d/%m/%Y')
                elif isinstance(campo, tk.Scale):
                    dados[etiqueta] = int(campo.get())
                elif isinstance(campo, tk.StringVar):
                    dados[etiqueta] = campo.get()
            
            # Processar os checkbuttons
            forca_muscular = []
            for (check, var) in self.checkbuttons:
                if var.get():
                    forca_muscular.append(check.cget('text'))
            
            dados['Fuerza Muscular'] = forca_muscular
            
            # Processar radio buttons
            for var_name, var in self.radio_buttons.items():
                dados[var_name] = var.get()
            
            # Criar pasta de dados se não existir
            diretorio_dados = CONFIG_FORMULARIO["dir_dados"]
            if not os.path.exists(diretorio_dados):
                os.makedirs(diretorio_dados)
            
            # Gerar nome de arquivo baseado no nome do paciente e data
            nome_paciente = dados.get('Nombre Completo', '').strip()
            if not nome_paciente:
                nome_paciente = 'paciente_sem_nome'
            nome_paciente = nome_paciente.replace(' ', '_').lower()
            
            data_atual = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_paciente}_{data_atual}.json"
            
            # Caminho completo do arquivo
            caminho_arquivo = os.path.join(diretorio_dados, nome_arquivo)
            
            # Salvar como JSON
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
            
            # Resetar flag de modificação
            self.modificado = False
            
            # Mostrar mensagem de sucesso com mais detalhes
            messagebox.showinfo(
                "Guardar", 
                f"Evaluación guardada correctamente.\n\nArchivo: {nome_arquivo}\nDirectorio: {diretorio_dados}",
                icon='info'
            )
            
            return dados
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Error al guardar el formulario: {str(e)}",
                icon='error'
            )
    
    def imprimir_formulario(self):
        """Prepara o formulário para impressão"""
        try:
            # Tentar salvar primeiro
            dados = self.salvar_formulario()
            
            if dados:
                # Aqui você poderia implementar código para gerar um PDF
                # Usando alguma biblioteca como ReportLab, por exemplo
                
                messagebox.showinfo(
                    "Imprimir", 
                    "Preparando el documento para impresión...\n\nEl archivo será generado en breve.",
                    icon='info'
                )
            
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"Error al preparar la impresión: {str(e)}",
                icon='error'
            )


# Função para adicionar o formulário a qualquer notebook
def adicionar_formulario_fisioterapia(notebook):
    """
    Adiciona o formulário de fisioterapia a qualquer notebook
    
    Args:
        notebook: Notebook (ttk.Notebook) onde o formulário será adicionado
        
    Returns:
        FormularioFisioterapia: Instância do formulário criado
    """
    return FormularioFisioterapia(notebook)


# Parte principal do código
if __name__ == "__main__":
    try:
        # Configurar janela principal
        root = tk.Tk()
        root.title("Sistema de Evaluación")
        root.geometry("1100x750")
        
        # Configurar as cores da interface
        root.config(bg=CORES["fundo"])
        
        # Frame principal com margem
        frame_principal = tk.Frame(root, bg=CORES["fundo"], padx=10, pady=10)
        frame_principal.pack(expand=True, fill="both")
        
        # Notebook principal - usando ttk.Notebook em vez de tk.Notebook
        notebook = ttk.Notebook(frame_principal)
        notebook.pack(expand=True, fill="both")
        
        # Configurar estilo do notebook
        style = ttk.Style()
        style.configure('TNotebook', background=CORES["notebook_bg"])
        style.configure('TNotebook.Tab', 
                       background=CORES["tab_bg"],
                       foreground=CORES["texto_destaque"],
                       padding=[12, 6])
        style.map('TNotebook.Tab',
                 background=[('selected', CORES["notebook_bg"])],
                 foreground=[('selected', CORES["texto_destaque"])])
        
        # Adicionar formulário
        formulario = FormularioFisioterapia(notebook)
        
        # Configurar evento de fechamento da janela
        def ao_fechar():
            """Confirma antes de fechar se houver modificações não salvas"""
            if formulario.modificado:
                resposta = messagebox.askyesno(
                    "Salir", 
                    "¿Está seguro que desea salir?",
                    icon='warning'
                )
                if resposta:
                    root.destroy()
            else:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", ao_fechar)
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror(
            "Error", 
            f"Error al iniciar la aplicación: {str(e)}",
            icon='error'
        )