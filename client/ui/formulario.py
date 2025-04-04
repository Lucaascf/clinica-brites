# formulario.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from tkinter import messagebox, font
from tkcalendar import DateEntry
import datetime
import json
import traceback 
import os
from PIL import Image, ImageTk  # Para ícones e imagens
from tkinter import ttk
from client.crontrollers.integracao_aba_client import IntegradorSistema
from config import SERVER_URL, CORES, FONTES, TAMANHOS, ESTILOS, CONFIG_FORMULARIO, OPCOES, ESCALAS, PLACEHOLDER_COLOR
from server.database import BancoDadosFisioterapia
import threading




class DateEntryImproved(DateEntry):
    """
    Versão simples do DateEntry que fecha o calendário ao clicar em qualquer lugar fora
    """
    def __init__(self, master=None, auto_popup=False, **kw):
        super().__init__(master, **kw)
        self.auto_popup = auto_popup
        self._calendario_visivel = False
        
        # Substituir o binding original
        self.unbind("<Button-1>")
        self.bind("<Button-1>", self._on_click, add="+")
        
        # Binding para fechar quando clicar fora
        self.winfo_toplevel().bind("<Button-1>", self._fechar_se_clicar_fora, add="+")
    
    def _on_click(self, event):
        """Abre o calendário apenas quando clicado diretamente"""
        if not self._calendario_visivel:
            self.drop_down()
            self._calendario_visivel = True
        else:
            self._top_cal.withdraw()
            self._calendario_visivel = False
        return "break"  # Impede propagação do evento
    
    def _fechar_se_clicar_fora(self, event):
        """Fecha o calendário se clicar em qualquer lugar fora"""
        if not hasattr(self, '_top_cal') or not self._top_cal:
            return
            
        # Verificar se o clique foi fora do calendário e do campo
        widget = event.widget
        dentro = (widget == self) or (hasattr(widget, 'master') and widget.master == self._top_cal)
        
        if not dentro and self._calendario_visivel:
            self._top_cal.withdraw()
            self._calendario_visivel = False


    def _alternar_calendario(self, event=None):
        """Abre ou fecha o calendário ao clicar no campo"""
        # Impedir que o evento se propague para o bind global
        event.widget.focus_set()
        if event:
            event.widget.after(10, lambda: self._mostrar_calendario())
        return "break"  # Evita que o evento se propague
    
    def _mostrar_calendario(self):
        """Mostra o calendário"""
        try:
            # Usar o método da classe pai para mostrar o calendário
            super().drop_down()
            self._calendario_visivel = True
        except Exception as e:
            print(f"Erro ao mostrar calendário: {e}")
    
    def _verificar_clique_fora(self, event):
        """Fecha o calendário se o clique foi fora dele e do campo de entrada"""
        # Primeiro verificar se o calendário existe e está visível
        if not hasattr(self, '_top_cal') or not self._top_cal:
            return
            
        # Verificar se o calendário é visível antes de tentar fechar
        if not hasattr(self._top_cal, 'winfo_viewable') or not self._top_cal.winfo_viewable():
            return
    
            
        # Verificar se o calendário é visível antes de tentar fechar
        if not hasattr(self._top_cal, 'winfo_viewable') or not self._top_cal.winfo_viewable():
            return
            
        # Se o clique foi no próprio campo, ignore (já tratado pelo outro bind)
        if event.widget == self:
            return
            
        # Verificar se o clique foi dentro do calendário ou seus componentes
        dentro_calendario = False
        try:
            # Verificar se o widget clicado é o calendário ou um filho do calendário
            widget = event.widget
            while widget:
                if widget == self._top_cal:
                    dentro_calendario = True
                    break
                widget = widget.master
        except:
            pass
            
        # Se o clique não foi dentro do calendário, feche-o
        if not dentro_calendario:
            self._top_cal.withdraw()
            self._calendario_visivel = False



class EditableLabel(tk.Frame):
    def __init__(
        self,
        master,
        min_lines=3,
        width=None,
        max_chars=None,
        placeholder=None,
        placeholder_color=PLACEHOLDER_COLOR,
        font=("Courier New", 10),  # Fonte monoespaçada padrão
        **kwargs
    ):
        super().__init__(master)
        
        # Ajuste automático do width se max_chars existir
        if max_chars is not None and width is None:
            width = max_chars + 2  # Margem de segurança
        
        self.max_chars = max_chars
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        
        # Configurações do widget Text com a fonte
        self.text = tk.Text(
            self,
            wrap=tk.WORD,
            height=min_lines,
            width=width,
            font=font,  # Aplica a fonte aqui
            padx=5,
            pady=5,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#d3d3d3",
            highlightcolor="#4a90d9",
            **kwargs
        )
        
        # Barra de rolagem
        self.scrollbar = tk.Scrollbar(self, command=self.text.yview)
        self.text.config(yscrollcommand=self.scrollbar.set)
        
        # Layout
        self.text.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.scrollbar.grid_remove()
        
        # Configuração de grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Configuração de eventos
        self.text.bind("<FocusIn>", self._on_focus_in)
        self.text.bind("<FocusOut>", self._on_focus_out)
        self.text.bind("<Key>", lambda e: self.after(10, self._update_scrollbar))
        
        # Se max_chars não for None, adicionar validação
        if self.max_chars is not None:
            self.text.bind("<KeyPress>", self._check_limit)
            self.text.bind("<<Paste>>", self._on_paste)
        
        # Controle de foco e eventos de scroll
        self._has_focus = False
        self.text.bind("<FocusIn>", self._set_focus_true, add="+")
        self.text.bind("<FocusOut>", self._set_focus_false, add="+")
        
        # Bindings de scroll são ativados/desativados conforme o foco
        self._setup_scroll_bindings()
        
        # Identificador do binding para poder removê-lo quando necessário
        self.binding_id = None
        
        # Configurar evento quando o texto recebe foco
        self.text.bind("<FocusIn>", self._on_text_focus_in, add="+")
        
        # Configurar placeholder se fornecido
        if self.placeholder:
            self.text.insert('1.0', self.placeholder)
            self.text.config(fg=self.placeholder_color)
            
            # Bind eventos para o comportamento do placeholder
            self.text.bind('<FocusIn>', self._on_focus_in_placeholder, add="+")
            self.text.bind('<FocusOut>', self._on_focus_out_placeholder, add="+")
    
    def _on_focus_in_placeholder(self, event):
        if self.text.get('1.0', 'end-1c') == self.placeholder:
            self.text.delete('1.0', tk.END)
            self.text.config(fg='black')

    def _on_focus_out_placeholder(self, event):
        if not self.text.get('1.0', 'end-1c'):
            self.text.insert('1.0', self.placeholder)
            self.text.config(fg=self.placeholder_color)

    def _on_paste(self, event):
        """Controla a colagem para respeitar o limite de caracteres"""
        if self.max_chars is None:
            return
            
        # Interceptar o evento padrão de colagem
        self.text.tk.call('break')
        
        try:
            # Obter texto da área de transferência
            clipboard_text = self.clipboard_get()
            
            # Calcular o espaço disponível
            current_text = self.text.get('1.0', 'end-1c')
            available_chars = self.max_chars - len(current_text)
            
            # Se for placeholder, temos todo o espaço disponível
            if self.placeholder and current_text == self.placeholder:
                available_chars = self.max_chars
                self.text.delete('1.0', tk.END)
                self.text.config(fg='black')
                
            # Truncar o texto se necessário
            if len(clipboard_text) > available_chars:
                clipboard_text = clipboard_text[:available_chars]
                
            # Inserir texto truncado
            self.text.insert(tk.INSERT, clipboard_text)
            return 'break'
        except:
            return

    def _check_limit(self, event):
        """Verifica se o texto excede o limite de caracteres"""
        # Se for uma tecla especial (como setas, backspace, etc), não fazemos nada
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Tab', 'Home', 'End', 'Return'):
            return
        
        # Verificar comprimento atual
        current_text = self.text.get('1.0', 'end-1c')
        if len(current_text) >= self.max_chars:
            return "break"  # Impede a inserção de mais caracteres
    
    def _set_focus_true(self, event):
        """Marca o campo como tendo foco"""
        self._has_focus = True
        self._setup_scroll_bindings()
    
    def _set_focus_false(self, event):
        """Marca o campo como não tendo foco"""
        self._has_focus = False
        self._setup_scroll_bindings()
    
    def _setup_scroll_bindings(self):
        """Configura os bindings de scroll baseado no estado de foco"""
        # Primeiro remove qualquer binding existente
        self.text.unbind("<MouseWheel>")
        self.text.unbind("<Button-4>")
        self.text.unbind("<Button-5>")
        
        # Se o campo tem foco, adiciona os bindings para scroll
        if self._has_focus:
            self.text.bind("<MouseWheel>", self._on_mouse_scroll)
            self.text.bind("<Button-4>", self._on_scroll_up)
            self.text.bind("<Button-5>", self._on_scroll_down)
        else:
            # Quando não tem foco, bloqueia o scroll no campo e repassa para o formulário principal
            self.text.bind("<MouseWheel>", self._pass_scroll_to_parent)
            self.text.bind("<Button-4>", self._pass_scroll_up_to_parent)
            self.text.bind("<Button-5>", self._pass_scroll_down_to_parent)
    
    def _pass_scroll_to_parent(self, event):
        """Repassa o scroll para o formulário principal"""
        self.winfo_toplevel().event_generate("<MouseWheel>", 
                                           delta=event.delta,
                                           x=event.x_root, 
                                           y=event.y_root)
        return "break"  # Bloqueia o scroll no campo
    
    def _pass_scroll_up_to_parent(self, event):
        """Repassa o scroll para cima para o formulário principal (Linux)"""
        self.winfo_toplevel().event_generate("<Button-4>", 
                                           x=event.x_root, 
                                           y=event.y_root)
        return "break"  # Bloqueia o scroll no campo
    
    def _pass_scroll_down_to_parent(self, event):
        """Repassa o scroll para baixo para o formulário principal (Linux)"""
        self.winfo_toplevel().event_generate("<Button-5>", 
                                           x=event.x_root, 
                                           y=event.y_root)
        return "break"  # Bloqueia o scroll no campo
    
    def _on_text_focus_in(self, event):
        """Quando o texto recebe foco, configuramos o binding global"""
        # Remove binding anterior se existir
        if self.binding_id:
            self.winfo_toplevel().unbind("<Button-1>", self.binding_id)
        
        # Adiciona novo binding
        self.binding_id = self.winfo_toplevel().bind("<Button-1>", self._handle_global_click, add="+")
    
    def _handle_global_click(self, event):
        """Trata cliques em qualquer lugar da aplicação"""
        click_widget = event.widget
        
        # Se o clique foi em outro widget Text, não faz nada (permite que o foco mude)
        if isinstance(click_widget, tk.Text):
            return
            
        # Se o clique não foi no texto nem em seus filhos
        # E o texto está com foco, remove o foco
        if self.text.focus_displayof() and click_widget != self.text:
            # Verifica também se não é um filho do widget de texto
            parent = click_widget
            is_child = False
            
            # Verifica a hierarquia de widgets
            while parent and not is_child:
                if parent == self.text:
                    is_child = True
                    break
                try:
                    parent = parent.master
                except:
                    break
            
            # Se não for filho, remove o foco
            if not is_child:
                # Apenas remove o foco do texto
                self.master.focus_set()
    
    def _on_focus_in(self, event=None):
        """Quando o campo ganha foco"""
        self.text.config(highlightbackground="#4a90d9")
    
    def _on_focus_out(self, event=None):
        """Quando o campo perde foco"""
        self.text.config(highlightbackground="#d3d3d3")
    
    def _on_mouse_scroll(self, event):
        """Scroll do mouse (Windows/MacOS)"""
        self.text.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"  # Impede a propagação
    
    def _on_scroll_up(self, event):
        """Scroll para cima (Linux)"""
        self.text.yview_scroll(-1, "units")
        return "break"  # Impede a propagação
    
    def _on_scroll_down(self, event):
        """Scroll para baixo (Linux)"""
        self.text.yview_scroll(1, "units")
        return "break"  # Impede a propagação
    
    def _update_scrollbar(self):
        """Atualiza a visibilidade da scrollbar"""
        if self.text.yview() != (0.0, 1.0):
            self.scrollbar.grid()
        else:
            self.scrollbar.grid_remove()
    
    def get(self):
        """Retorna o texto sem a quebra de linha final"""
        return self.text.get('1.0', 'end-1c')
    
    def insert(self, index, text):
        """Insere texto no campo"""
        self.text.insert(index, text)
        self._update_scrollbar()
    
    def delete(self, start, end):
        """Remove texto do campo"""
        self.text.delete(start, end)
        self._update_scrollbar()



class CampoTextoAutoExpansivel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        # Extrai parâmetros específicos antes de passar para o Frame
        self.max_caracteres = kwargs.pop("max_caracteres", 1000000)
        self.largura = kwargs.pop("width", 40)
        self.altura_inicial = kwargs.pop("height", 1)
        self.altura_maxima = kwargs.pop("max_height", 0)
        self.cor_fundo = kwargs.pop("bg", "white")
        placeholder_text = kwargs.pop("placeholder", None)
        placeholder_color = kwargs.pop("placeholder_color", PLACEHOLDER_COLOR)

        # Inicializa o Frame pai
        super().__init__(master, bg=self.cor_fundo, **kwargs)

        # Configurações padrão para o widget Text
        text_kwargs = {
            "wrap": "word",
            "width": self.largura,
            "height": self.altura_inicial,
            "bg": self.cor_fundo,
            "highlightthickness": 0,
            "font": FONTES["campo"]
        }

        # Cria o widget Text
        self.texto = tk.Text(self, **text_kwargs)
        self.texto.pack(fill=tk.X, expand=False)

        # Configura placeholder se fornecido
        if placeholder_text:
            self.texto.insert('1.0', placeholder_text)
            self.texto.config(fg=placeholder_color)
            
            def on_focus_in(event):
                if self.texto.get('1.0', 'end-1c') == placeholder_text:
                    self.texto.delete('1.0', tk.END)
                    self.texto.config(fg='black')
            
            def on_focus_out(event):
                if not self.texto.get('1.0', 'end-1c'):
                    self.texto.insert('1.0', placeholder_text)
                    self.texto.config(fg=placeholder_color)
            
            self.texto.bind('<FocusIn>', on_focus_in)
            self.texto.bind('<FocusOut>', on_focus_out)

        # Configura eventos para auto-ajuste
        self.texto.bind('<KeyRelease>', self._ajustar_altura)
        self.texto.bind('<Configure>', self._ajustar_altura)
        
        # Ajuste inicial
        self.after(10, self._ajustar_altura)

    def _ajustar_altura(self, event=None):
        """Ajusta a altura do widget conforme o conteúdo"""
        num_linhas = self.texto.count('1.0', 'end', 'displaylines')[0]
        
        if self.altura_maxima > 0:
            num_linhas = min(num_linhas, self.altura_maxima)
        
        self.texto.config(height=num_linhas)
        self.update_idletasks()

    def obter(self):
        """Retorna o conteúdo do campo"""
        return self.texto.get('1.0', 'end-1c')

    def limpar(self):
        """Limpa o conteúdo do campo"""
        self.texto.delete('1.0', tk.END)



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

        self.aplicar_ajustes_todos_campos()

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
        
        # Criar notebook para outras seções - será carregado sob demanda
        self.notebook_avaliacao = ttk.Notebook(self.frame_conteudo)
        self.notebook_avaliacao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas, 
            sticky="ew", 
            padx=5, 
            pady=10
        )
        linha += 1
        
        # Criar apenas as abas, mas não o conteúdo ainda
        self.frames_avaliacao = {
            'evaluacion_fisica': {'frame': None, 'carregado': False, 'titulo': "EVALUACIÓN FÍSICA"},
            'pruebas_especificas': {'frame': None, 'carregado': False, 'titulo': "PRUEBAS ESPECÍFICAS"},
            'mediciones_escalas': {'frame': None, 'carregado': False, 'titulo': "MEDICIONES Y ESCALAS"},
            'diagnosticos': {'frame': None, 'carregado': False, 'titulo': "DIAGNÓSTICOS"},
            'plan_tratamiento': {'frame': None, 'carregado': False, 'titulo': "PLAN DE TRATAMIENTO"},
            'seguimiento': {'frame': None, 'carregado': False, 'titulo': "SEGUIMIENTO Y REEVALUACIÓN"}
        }
        
        # Criar os frames vazios e adicionar ao notebook
        for key, info in self.frames_avaliacao.items():
            frame = tk.Frame(self.notebook_avaliacao, bg=self.cores["secao_bg"])
            self.notebook_avaliacao.add(frame, text=info['titulo'])
            self.frames_avaliacao[key]['frame'] = frame
        
        # Vincular evento para carregar conteúdo quando a aba é selecionada
        self.notebook_avaliacao.bind("<<NotebookTabChanged>>", self._carregar_aba_sob_demanda)
        
        # Botões de ação
        self.criar_botoes_acao(linha)

    def aplicar_ajustes_todos_campos(self):
        """
        Aplica ajustes a todos os campos do formulário para garantir que funcionem
        corretamente com a expansão vertical a partir de uma linha.
        """
        for nome_campo, campo in self.campos.items():
            if hasattr(campo, 'texto'):
                # Forçar altura inicial de 1 linha
                campo.altura_inicial = 1
                
                # Garantir wrap por palavra e largura fixa
                campo.texto.config(wrap="word", width=campo.largura)
                
                # Reajustar altura com base no conteúdo atual
                campo._ajustar_altura()
        
        # Atualizar todo o formulário
        self.frame.update_idletasks()

    def ajustar_campos_vitais(self):
        """Ajusta os campos de parâmetros vitais para garantir altura correta"""
        campos_vitais = ["PA", "Pulso", "Talla", "Peso", "T", "FR", "Sat.O2"]
        for nome in campos_vitais:
            if nome in self.campos:
                campo = self.campos[nome]
                if hasattr(campo, 'texto'):
                    # Definir uma altura fixa para estes campos
                    campo.texto.configure(height=2)
                    campo.update_idletasks()

    def _carregar_aba_sob_demanda(self, evento=None):
        """Carrega o conteúdo da aba somente quando ela é selecionada, com otimização"""
        tab_id = self.notebook_avaliacao.select()
        if not tab_id:
            return
            
        tab_index = self.notebook_avaliacao.index(tab_id)
        
        # Mapear índice para chave
        keys = list(self.frames_avaliacao.keys())
        if tab_index < len(keys):
            key = keys[tab_index]
            
            # Se já carregado, não fazer nada
            if self.frames_avaliacao[key]['carregado']:
                return
            
            # Mostrar indicador de carregamento
            frame = self.frames_avaliacao[key]['frame']
            label_carregando = tk.Label(
                frame, 
                text="Carregando...", 
                bg=self.cores["secao_bg"],
                font=FONTES["titulo"]
            )
            label_carregando.pack(expand=True, fill="both", padx=20, pady=20)
            frame.update()
            
            # Carregar em uma thread separada para não travar a UI
            def thread_carregar_conteudo():
                try:
                    # Determinar qual método de criação chamar
                    if key == 'evaluacion_fisica':
                        self.criar_secao_evaluacion_fisica(frame)
                        # Agendar o ajuste dos campos vitais na thread principal
                        if frame.winfo_exists():
                            frame.after(100, self.ajustar_campos_vitais)
                    elif key == 'pruebas_especificas':
                        self.criar_secao_pruebas_especificas(frame)
                    elif key == 'mediciones_escalas':
                        self.criar_secao_mediciones_escalas(frame)
                    elif key == 'diagnosticos':
                        self.criar_secao_diagnosticos(frame)
                    elif key == 'plan_tratamiento':
                        self.criar_secao_plan_tratamiento(frame)
                    elif key == 'seguimiento':
                        self.criar_secao_seguimiento(frame)
                    
                    # Remover indicador de carregamento na thread principal
                    if frame.winfo_exists():
                        frame.after(10, lambda: label_carregando.destroy())
                        
                    # Marcar como carregado
                    self.frames_avaliacao[key]['carregado'] = True
                    self.aplicar_ajustes_todos_campos()
                except Exception as e:
                    print(f"Erro ao carregar aba {key}: {e}")
            
            # Iniciar a thread
            threading.Thread(target=thread_carregar_conteudo, daemon=True).start()
    
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
        """Versão modificada de criar_secao_historial_paciente com suporte a 1500 caracteres"""
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

        # Substituir por EditableLabel da forma mais simples
        campo_nome = EditableLabel(
            frame_conteudo_secao,
            min_lines=1,
            width=50,
            max_chars=100,
            placeholder='Ingrese Nombre Completo...',
            placeholder_color=PLACEHOLDER_COLOR,
            bg="#ffffff"
        )
        campo_nome.grid(row=0, column=1, columnspan=3, padx=0, pady=(0, 10), sticky="ew")

        # Evento de modificação
        campo_nome.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())

        # Armazenar a referência ao widget Text
        self.campos["Nombre Completo"] = campo_nome.text
        
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
        
        campo_idade = EditableLabel(
            frame_conteudo_secao,
            min_lines=1,
            width=10,  
            max_chars=3, 
            bg=self.cores["campo_bg"],
            placeholder="Edad",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_idade.grid(row=1, column=1, padx=(0, 20), pady=(0, 10), sticky="w")
        campo_idade.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Edad"] = campo_idade.text
        
        # Gênero (diretamente ao lado da idade)
        label_genero = tk.Label(
            frame_conteudo_secao, 
            text="Genero", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_genero.grid(row=1, column=2, padx=(0, 5), pady=(0, 10), sticky="w")

        # Criar uma variável para armazenar o valor selecionado
        var_genero = tk.StringVar()

        # Opções para gênero (apenas Masculino e Femenino)
        opcoes_genero = ["Masculino", "Femenino"]

        # Configuração simples para remover o azul
        style = ttk.Style()
        style.map('TCombobox', selectbackground=[('readonly', 'white')], selectforeground=[('readonly', 'black')])

        # Criar combobox
        campo_genero = ttk.Combobox(
            frame_conteudo_secao,
            textvariable=var_genero,
            values=opcoes_genero,
            width=15,
            state="readonly"  # Impede que o usuário digite, só pode selecionar
        )
        campo_genero.grid(row=1, column=3, padx=0, pady=(0, 10), sticky="w")

        # Associar evento de alteração
        campo_genero.bind("<<ComboboxSelected>>", lambda e: self.marcar_modificado())

        # Armazenar a referência no dicionário - agora é a variável, não o widget
        self.campos["Genero"] = var_genero
        
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
        
        campo_contato = EditableLabel(
            frame_conteudo_secao,
            max_chars=180,  # O width será calculado automaticamente (30 + 2)
            min_lines=1,
            bg=self.cores["campo_bg"],
            placeholder="Ingrese contacto...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_contato.grid(row=2, column=1, padx=(0, 20), pady=(0, 10), sticky="ew")
        campo_contato.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Contacto"] = campo_contato.text
        
        # Data de nascimento (imediatamente após o contato)
        label_data = tk.Label(
            frame_conteudo_secao, 
            text="Fecha Nasc.", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_data.grid(row=2, column=2, padx=(0, 5), pady=(0, 10), sticky="w")

        # Usar a classe melhorada DateEntryImproved em vez de DateEntry
        data_nasc = DateEntryImproved(
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
        
        campo_area = EditableLabel(
            frame_conteudo_secao, 
            max_chars=210, 
            min_lines=1,  
            bg=self.cores["campo_bg"],
            placeholder="Ingrese área de consulta...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_area.grid(row=3, column=1, columnspan=3, padx=0, pady=(0, 10), sticky="ew")
        campo_area.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Área de consulta"] = campo_area.text
        
        # --- QUINTA LINHA: ALERGIAS ---
        label_alergias = tk.Label(
            frame_conteudo_secao, 
            text="Alergias", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"],
            anchor="w"
        )
        label_alergias.grid(row=4, column=0, padx=(0, 5), pady=0, sticky="nw")

        # Cria o campo com 3 linhas fixas
        campo_alergias = EditableLabel(
            frame_conteudo_secao,
            min_lines=3,
            #width=90,
            bg=self.cores["campo_bg"],
            font=FONTES["campo"],
            placeholder="Ingrese alergias..."
        )

        # Posicionamento (como antes)
        campo_alergias.grid(row=4, column=1, columnspan=3, padx=0, pady=0, sticky="nsew")

        # Para vincular eventos (agora mais simples)
        campo_alergias.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())

        # Para acessar o valor
        self.campos["Alergias"] = campo_alergias.text
                
        return linha
    
    def criar_secao_historia_clinica(self, linha_inicio):
        """Versão modificada de criar_secao_historia_clinica com suporte a 1500 caracteres"""
        linha = linha_inicio
        
        # Frame da seção
        frame_secao = tk.Frame(self.frame_conteudo, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.grid(
            row=linha, 
            column=0, 
            columnspan=self.num_colunas,  # Usar todas as colunas 
            sticky="ew",  # Expandir horizontalmente 
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
        
        # Configurar colunas para layout responsivo
        frame_conteudo_secao.columnconfigure(0, weight=0)  # Coluna do label (tamanho fixo)
        frame_conteudo_secao.columnconfigure(1, weight=1)  # Coluna do campo (expansível)
        
        # Campos com área de texto maior
        campos = [
            ("Motivo de consulta", 0),
            ("Antecedentes", 1),
            ("Efermedad actual", 2),
            ("Cirurgías previas", 3),
            ("Medicamentos actuales", 4)
        ]
        
        # Criar campos com mais altura e largura para suportar até 1500 caracteres
        for campo, linha_local in campos:
            # Label com width fixo para manter alinhamento
            label = tk.Label(
                frame_conteudo_secao, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"],
                width=20,  # Largura fixa para manter alinhamento
                anchor='w'  # Alinhar texto à esquerda
            )
            label.grid(row=linha_local, column=0, padx=5, pady=8, sticky="nw")
            
            # Campo de texto expansível configurado para 1500 caracteres
            campo_texto = EditableLabel(
                frame_conteudo_secao, 
                min_lines=3,  # Largura inicial
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR,
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=8, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
        
        return linha
    
    def criar_secao_evaluacion_fisica(self, frame_pai):
        """Cria a seção de Avaliação Física com todas as subseções e labels fora dos campos"""
        # Frame da seção já é o frame_pai
        frame_secao = frame_pai
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
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
        label_titulo_exame.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")
        
        # Linha separadora para o título
        separador_exame = tk.Frame(frame_exame, height=1, bg="#cccccc")
        separador_exame.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        
        # Parâmetros vitais com labels fora dos campos - ajustado para começar na linha 2
        parametros_vitais = [
            ("PA", 2, "mmHg"),
            ("Pulso", 3, "lpm"),
            ("Talla", 4, "cm"),
            ("Peso", 5, "kg"),
            ("T", 6, "°C"),
            ("FR", 7, "rpm"),
            ("Sat.O2", 8, "%")
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
            campo_texto = EditableLabel(
                frame_campo, 
                min_lines=1, 
                max_chars=50,  
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {parametro}...",
                placeholder_color=PLACEHOLDER_COLOR
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
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[parametro] = campo_texto.text
        
        # Adicionar linha separadora após os parâmetros vitais - ajustado para linha 9
        separador_params = tk.Frame(frame_exame, height=1, bg="#cccccc")
        separador_params.grid(row=9, column=0, columnspan=2, padx=5, pady=10, sticky="ew")
        
        # Campos IDx e Conducta - ajustados para começar na linha 10
        campos_adicionales = [
            ("IDx", 10),
            ("Conducta", 11)
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
            campo_texto = EditableLabel(
                frame_exame, 
                width=53, 
                min_lines=1, 
                max_chars=50, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {campo}..."
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="w")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
            
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
            fg="#ffffff",
            font=FONTES["secao"],
            anchor="w"  # Adiciona alinhamento à esquerda
        )
        label_titulo_inspeccion.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")

        # Linha separadora - MOVIDA PARA BAIXO do título
        separador_inspeccion = tk.Frame(frame_inspeccion, height=1, bg="#cccccc")
        separador_inspeccion.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")

        # Ajustar a linha inicial dos campos para começar após o separador
        campos_inspecao = [
            ("Postura", 2),  # Alterado de 1 para 2
            ("Simetría corporal", 3),  # Alterado de 2 para 3
            ("Deformidades aparentes", 4)  # Alterado de 3 para 4
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
            campo_texto = EditableLabel(
                frame_inspeccion, 
                min_lines=4, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
        
        # 1.2 Título da Palpação com linha separadora apenas abaixo
        label_titulo_palpacion = tk.Label(
            frame_inspeccion, 
            text="2. Palpación", 
            bg=self.cores["secao_bg"],
            fg="#ffffff",
            font=FONTES["secao"]
        )
        label_titulo_palpacion.grid(row=5, column=0, columnspan=2, padx=5, pady=(20, 30), sticky="w")

        # Linha separadora apenas abaixo do título Palpación
        separador_palpacion_sub = tk.Frame(frame_inspeccion, height=1, bg="#cccccc")
        separador_palpacion_sub.grid(row=6, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")


        # Ajuste também os índices dos campos de Palpação
        # Campos de Palpação - AJUSTAR ÍNDICES para começar na linha 7
        campos_palpacao = [
            ("Puntos dolorosos", 7),  # Ajustado para linha 7
            ("Tensión muscular", 8)   # Ajustado para linha 8
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
            campo_texto = EditableLabel(
                frame_inspeccion, 
                min_lines=4,
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
        
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
        label_titulo_columna.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")
        
        # Linha separadora
        separador_columna = tk.Frame(frame_columna, height=1, bg="#cccccc")
        separador_columna.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        
        # Campos da Coluna Vertebral - ajustados para começar na linha 2
        campos_coluna = [
            ("Curvas Fisiológicas", 2),
            ("Presencia de Escoliosis", 3),
            ("Cifosis o Lordosis", 4)
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
            campo_texto = EditableLabel(
                frame_columna,  
                min_lines=4, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
        
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
        label_titulo_movilidad.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")
        
        # Linha separadora para Movilidad Articular
        separador_movilidad = tk.Frame(frame_movilidad, height=1, bg="#cccccc")
        separador_movilidad.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        
        # Rango de movimento - ajustado para começar na linha 2
        label_rango = tk.Label(
            frame_movilidad, 
            text="Rango de movimiento:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subsecao"]
        )
        label_rango.grid(row=2, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="w")
        
        # Campos do Rango de movimento - ajustados para linhas 3 e 4
        campos_rango = [
            ("Activo", 3),
            ("Pasivo", 4)
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
            campo_texto = EditableLabel(
                frame_movilidad, 
                min_lines=3,  
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre movimiento {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[f"Movimiento {campo}"] = campo_texto.text
        
        # Avaliação das articulações - ajustada para linha 5
        label_articul = tk.Label(
            frame_movilidad, 
            text="Evaluación de las articulaciones afectadas:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subsecao"]
        )
        label_articul.grid(row=5, column=0, columnspan=2, padx=5, pady=(15, 10), sticky="w")
        
        campo_art = EditableLabel(
            frame_movilidad,
            min_lines=4,
            bg=self.cores["campo_bg"],
            placeholder="Describa la evaluación de las articulaciones afectadas...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_art.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Vincular evento de modificação
        campo_art.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["Evaluación de articulaciones"] = campo_art.text
        
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
        label_titulo_fuerza.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")
        
        # Linha separadora para Fuerza Muscular
        separador_fuerza = tk.Frame(frame_fuerza, height=1, bg="#cccccc")
        separador_fuerza.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        
        # Campo para avaliação de grupos musculares - ajustado para linha 2
        label_grupos = tk.Label(
            frame_fuerza, 
            text="Evaluación de grupos musculares específicos:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        label_grupos.grid(row=2, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="w")
        
        campo_musculos = EditableLabel(
            frame_fuerza,
            min_lines=4,
            bg=self.cores["campo_bg"],
            placeholder="Describa la evaluación de los grupos musculares específicos...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_musculos.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Vincular evento de modificação
        campo_musculos.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["Evaluación de grupos musculares"] = campo_musculos.text
        
        # Níveis de força - ajustado para linha 4
        label_grados = tk.Label(
            frame_fuerza, 
            text="Grados de fuerza según la escala establecida:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 18, 'bold')
        )
        label_grados.grid(row=4, column=0, columnspan=2, padx=5, pady=(15, 10), sticky="w")
        
        # Opções com checkbuttons
        opcoes_forca = [
            "Grado 0: Ausencia de contracción",
            "Grado 1: Contracción detectable, pero no mueve la articulación",
            "Grado 2: Movimiento activo, pero no contra la gravedad",
            "Grado 3: Movimiento activo contra la gravedad, pero no con resistencia",
            "Grado 4: Movimiento activo contra resistencia moderada",
            "Grado 5: Movimiento activo contra resistencia completa"
        ]
        
        # Criar frame para radio buttons com estilo - ajustado para linha 5
        frame_check = tk.Frame(frame_fuerza, bg=self.cores["secao_bg"], padx=5, pady=5)
        frame_check.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Variável compartilhada para radio buttons (só permite uma seleção)
        var_forca = tk.StringVar(value="")
        self.radio_buttons["grado_fuerza"] = var_forca  # Guardar referência no dicionário de radio buttons

        # Criar radio buttons em uma lista vertical com tamanho aumentado
        for i, opcao in enumerate(opcoes_forca):
            style = ttk.Style()
            style.configure('Big.TRadiobutton',
                background=self.cores["secao_bg"],
                foreground=self.cores["texto_destaque"],
                font=('Segoe UI', 12),
                indicatorsize=20  # Tamanho do indicador em pixels
            )

            radio = ttk.Radiobutton(
                frame_check,
                text=opcao,
                variable=var_forca,
                value=opcao,
                command=self.marcar_modificado,
                style='Big.TRadiobutton'
            )
            radio.grid(row=i, column=0, padx=5, pady=5, sticky="w")

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
        label_titulo_neuro.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")
        
        # Linha separadora para Evaluación Neuromuscular
        separador_neuro = tk.Frame(frame_neuro, height=1, bg="#cccccc")
        separador_neuro.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        
        # Campos da Avaliação Neuromuscular - ajustados para começar na linha 2
        campos_neuro = [
            ("Reflejos", 2),
            ("Coordinación motora", 3),
            ("Equilibrio", 4)
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
            campo_texto = EditableLabel(
                frame_neuro,
                min_lines=4,  
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
            
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
        label_titulo_funcional.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")
        
        # Linha separadora para Evaluación Funcional
        separador_funcional = tk.Frame(frame_funcional, height=1, bg="#cccccc")
        separador_funcional.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        
        # Campos da Avaliação Funcional - ajustados para começar na linha 2
        campos_funcional = [
            ("Capacidad para realizar actividades diarias", 2), 
            ("Limitaciones y dificultades", 3)
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
            campo_texto = EditableLabel(
                frame_funcional, 
                min_lines=4, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
        
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
        label_titulo_coordinacion.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 30), sticky="w")
        
        # Linha separadora para Evaluación de la Coordinación
        separador_coordinacion = tk.Frame(frame_coordinacion, height=1, bg="#cccccc")
        separador_coordinacion.grid(row=1, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="ew")
        
        # Coordenação motora fina - ajustada para linha 2
        label_motora_fina = tk.Label(
            frame_coordinacion, 
            text="Pruebas de coordinación motora fina:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        label_motora_fina.grid(row=2, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="w")
        
        # Campos para coordenação fina - ajustados para linhas 3 e 4
        campos_fina = [
            ("Ejercicios con dedos", 3),
            ("Precisión en movimientos", 4)
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
            campo_texto = EditableLabel(
                frame_coordinacion, 
                min_lines=3, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
        
        # Coordenação motora grossa - ajustada para linha 5
        label_motora_gruesa = tk.Label(
            frame_coordinacion, 
            text="Pruebas de coordinación motora gruesa:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"] 
        )
        label_motora_gruesa.grid(row=5, column=0, columnspan=2, padx=5, pady=(15, 10), sticky="w")
        
        # Campos para coordenação grossa - ajustados para linhas 6 e 7
        campos_gruesa = [
            ("Marcha", 6),
            ("Equilibrio Dinámico", 7)
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
            campo_texto = EditableLabel(
                frame_coordinacion, 
                min_lines=3, 
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese información sobre {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=5, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
        
    def criar_secao_pruebas_especificas(self, frame_pai):
        """Cria a seção de Testes Específicos com cards usando EditableLabel"""
        # Frame da seção é o próprio frame_pai
        frame_secao = frame_pai
        
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
        
        # Frame container para os cards
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configurar grid
        frame_conteudo_secao.grid_rowconfigure(0, weight=1)
        for i in range(3):  # 3 colunas
            frame_conteudo_secao.columnconfigure(i, weight=1, uniform="cols")
        
        # Criar três cards lado a lado
        campos = [
            ("Pruebas ortopédicas", 0),
            ("Pruebas neurológicas", 1),
            ("Pruebas de estabilidad", 2)
        ]
        
        for campo, col in campos:
            # Frame do card
            card = tk.Frame(
                frame_conteudo_secao,
                bg=self.cores["campo_bg"],
                highlightbackground="#d3d3d3",
                highlightthickness=1,
                padx=10,
                pady=10
            )
            card.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
            
            # Título do card
            label = tk.Label(
                card, 
                text=campo, 
                bg=self.cores["campo_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["cabecalho_card"]
            )
            label.pack(anchor="w", padx=5, pady=(0, 10))
            
            # Campo de texto usando EditableLabel
            campo_texto = EditableLabel(
                card,
                min_lines=10,  # Altura mínima maior para ter mais espaço
                width=30,
                bg=self.cores["campo_bg"]
            )
            campo_texto.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Importante: o text attribute é o widget Text dentro do EditableLabel
            campo_texto.text.insert('1.0', f"")
            campo_texto.text.config(wrap=tk.WORD)  # Garantir quebra de linha por palavra
            
            # Armazenar referência ao widget Text do EditableLabel, não ao EditableLabel em si
            self.campos[campo] = campo_texto.text
            
            # Vincular evento de modificação ao widget Text
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
                
    def criar_secao_mediciones_escalas(self, frame_pai):
        """Cria a seção de Medições e Escalas com layout compactado - apenas EVA"""
        # Frame da seção é o próprio frame_pai
        frame_secao = frame_pai
        
        # Limpar qualquer conteúdo existente no frame_pai
        for widget in frame_secao.winfo_children():
            widget.destroy()
        
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
        
        # Usar um único frame para todo o conteúdo
        frame_conteudo = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo.pack(fill=tk.BOTH, expand=True, padx=15, pady=0)
        
        # Configuração de grid para melhor controle do layout
        frame_conteudo.columnconfigure(0, weight=1)
        
        # ================ ESCALA EVA ================
        # Título EVA - posicionamento imediato após o título principal
        label_eva = tk.Label(
            frame_conteudo, 
            text="(EVA) Escala Visual Analógica del Dolor", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 16, 'bold')
        )
        label_eva.grid(row=0, column=0, sticky="w", padx=5, pady=(10, 0))
        
        # Descrição
        descricao = tk.Label(
            frame_conteudo,
            text="Seleccione el nivel de dolor del paciente en la escala de 0 a 10:",
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subsecao"]
        )
        descricao.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 0))
        
        # Frame para labels de extremidades e escala (lado a lado)
        frame_escala_completa = tk.Frame(frame_conteudo, bg=self.cores["secao_bg"])
        frame_escala_completa.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 0))
        
        # Legendas e escala em um layout horizontal
        label_zero = tk.Label(
            frame_escala_completa, 
            text="Sin dolor", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 14, 'bold')
        )
        label_zero.pack(side=tk.LEFT, padx=(0, 10))
        
        # Escala em si - configurada com comprimento maior
        var_escala = tk.DoubleVar()
        escala_eva = tk.Scale(
            frame_escala_completa, 
            from_=0, 
            to=10, 
            orient=tk.HORIZONTAL,
            length=600,  # Aumentado para ocupar mais espaço
            sliderlength=30,
            showvalue=0,
            resolution=1,
            variable=var_escala,
            bg=self.cores["secao_bg"],
            highlightthickness=0,
            troughcolor="#DDDDDD",
            width=20,
            activebackground=self.cores["secundaria"]
        )
        escala_eva.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Valor numérico
        valor_eva = tk.Label(
            frame_escala_completa, 
            text="0", 
            width=2, 
            font=('Segoe UI', 18, 'bold'),
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"]
        )
        valor_eva.pack(side=tk.LEFT, padx=(10, 10))
        
        # Label máximo
        label_max = tk.Label(
            frame_escala_completa, 
            text="Dolor máximo", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 14, 'bold')
        )
        label_max.pack(side=tk.LEFT)
        
        # Função para atualizar o valor
        def atualizar_valor_eva(evento):
            valor = int(escala_eva.get())
            valor_eva.config(text=str(valor))
            self.marcar_modificado()

        escala_eva.bind("<Motion>", atualizar_valor_eva)
        escala_eva.bind("<ButtonRelease-1>", atualizar_valor_eva)
        
        # Armazenar referência
        self.campos["escala_eva"] = escala_eva
        
        # ================ OBSERVAÇÕES ================
        # Label para observações - sem espaço excessivo
        label_observaciones = tk.Label(
            frame_conteudo, 
            text="Observaciones adicionales sobre el dolor:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 14)
        )
        label_observaciones.grid(row=3, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # Campo de texto para observações
        observaciones = EditableLabel(
            frame_conteudo, 
            min_lines=5,
            bg=self.cores["campo_bg"],
            placeholder="Describa las características del dolor",
            placeholder_color=PLACEHOLDER_COLOR
        )
        observaciones.grid(row=4, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Vincular evento de modificação
        observaciones.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        
        # Armazenar referência ao campo
        self.campos["observaciones_dolor"] = observaciones.text
    
    def criar_secao_diagnosticos(self, frame_pai):
        """Cria a seção de Diagnósticos Fisioterapêuticos"""
        # Frame da seção é o próprio frame_pai
        frame_secao = frame_pai
        
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
        
        # Apenas ajuste as colunas para o grid expandir corretamente
        frame_conteudo_secao.columnconfigure(1, weight=1)
        
        # Campos
        campos = [
            ("Patológico", 0),
            ("Nutricional", 1),
            ("Inmunologico", 2)
        ]
        
        for campo, linha_local in campos:
            label = tk.Label(
                frame_conteudo_secao, 
                text=campo, 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["texto_secao"]
            )
            label.grid(row=linha_local, column=0, padx=5, pady=8, sticky="nw")
            
            # Campo de texto expansível com placeholder
            campo_texto = EditableLabel(
                frame_conteudo_secao, 
                min_lines=3,
                bg=self.cores["campo_bg"],
                placeholder=f"Ingrese {campo.lower()}...",
                placeholder_color=PLACEHOLDER_COLOR
            )
            # Apenas use sticky="ew" para o campo expandir horizontalmente
            campo_texto.grid(row=linha_local, column=1, padx=5, pady=8, sticky="ew")
            
            # Vincular evento de modificação
            campo_texto.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
            
            # Armazenar referência ao campo
            self.campos[campo] = campo_texto.text
    
    def criar_secao_plan_tratamiento(self, frame_pai):
        """Cria a seção de Plano de Tratamento com layout compactado"""
        # Frame da seção é o próprio frame_pai
        frame_secao = frame_pai
        
        # Limpar qualquer conteúdo existente no frame_pai
        for widget in frame_secao.winfo_children():
            widget.destroy()
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="PLAN DE TRATAMIENTO", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Usar um único frame para todo o conteúdo
        frame_conteudo = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo.pack(fill=tk.BOTH, expand=True, padx=15, pady=0)
        
        # Configuração de grid para melhor controle do layout
        frame_conteudo.columnconfigure(0, weight=1)
        
        # ================ FREQUÊNCIA E DURAÇÃO ================
        label_frecuencia = tk.Label(
            frame_conteudo, 
            text="Frecuencia y duración de las sesiones", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 16, 'bold')
        )
        label_frecuencia.grid(row=0, column=0, sticky="w", padx=5, pady=(10, 5))
        
        # Frame para os seletores de frequência e duração
        frame_selecao = tk.Frame(frame_conteudo, bg=self.cores["secao_bg"])
        frame_selecao.grid(row=1, column=0, sticky="w", padx=5, pady=(0, 5))
        
        # Seletor de frequência
        label_sesiones = tk.Label(
            frame_selecao, 
            text="Sesiones por semana:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_sesiones.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Definir cor mais harmônica para os botões
        cor_botao = self.cores["button_bg"]
        
        # Estilizar OptionMenu para sesiones
        var_sesiones = tk.StringVar(value="2")
        opcoes_sesiones = OPCOES["sesiones_semana"]
        
        frame_sesiones = tk.Frame(
            frame_selecao,
            bg=cor_botao,
            highlightbackground=cor_botao,
            highlightthickness=1,
            bd=0
        )
        frame_sesiones.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        cbox_sesiones = tk.OptionMenu(
            frame_sesiones, 
            var_sesiones, 
            *opcoes_sesiones
        )
        cbox_sesiones.config(
            width=5, 
            bg=cor_botao,
            fg=self.cores["texto_destaque"],
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=FONTES["campo"],
            padx=10,
            pady=5
        )
        cbox_sesiones.pack(fill=tk.BOTH, expand=True)
        
        # Seletor de duração
        label_duracion = tk.Label(
            frame_selecao, 
            text="Duración de cada sesión:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_duracion.grid(row=0, column=2, padx=(20, 5), pady=5, sticky="w")
        
        # Estilizar OptionMenu para duración
        var_duracion = tk.StringVar(value="60 minutos")
        opcoes_duracion = OPCOES["duracion_sesion"]
        
        frame_duracion = tk.Frame(
            frame_selecao,
            bg=cor_botao,
            highlightbackground=cor_botao,
            highlightthickness=1,
            bd=0
        )
        frame_duracion.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        cbox_duracion = tk.OptionMenu(
            frame_duracion, 
            var_duracion, 
            *opcoes_duracion
        )
        cbox_duracion.config(
            width=10, 
            bg=cor_botao,
            fg=self.cores["texto_destaque"],
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=FONTES["campo"],
            padx=10,
            pady=5
        )
        cbox_duracion.pack(fill=tk.BOTH, expand=True)
        
        # Armazenar referências
        self.campos["sesiones_semana"] = var_sesiones
        self.campos["duracion_sesion"] = var_duracion
        
        # Observações sobre frequência
        label_obs_freq = tk.Label(
            frame_conteudo, 
            text="Observaciones adicionales:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_obs_freq.grid(row=2, column=0, sticky="w", padx=5, pady=(5, 0))
        
        obs_frecuencia = EditableLabel(
            frame_conteudo,
            min_lines=3,
            bg=self.cores["campo_bg"],
            placeholder="Detalles sobre el programa de tratamiento...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        obs_frecuencia.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 10))
        
        obs_frecuencia.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["obs_frecuencia"] = obs_frecuencia.text
        
        # ================ EXERCÍCIOS RECOMENDADOS ================
        label_ejercicios = tk.Label(
            frame_conteudo, 
            text="Ejercicios recomendados para el hogar", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=('Segoe UI', 16, 'bold')
        )
        label_ejercicios.grid(row=4, column=0, sticky="w", padx=5, pady=(10, 5))
        
        ejercicios = EditableLabel(
            frame_conteudo,
            min_lines=3,
            bg=self.cores["campo_bg"],
            placeholder="Describa los ejercicios que el paciente debe realizar en casa..."
        )
        ejercicios.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 10))
        
        ejercicios.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["Ejercicios recomendados"] = ejercicios.text
    



















    def criar_secao_seguimiento(self, frame_pai):
        """Versão otimizada da seção de acompanhamento"""
        # Frame principal
        frame_secao = frame_pai
        
        # Label temporário de carregamento
        self.label_carregando_seguimiento = tk.Label(
            frame_secao, 
            text="Carregando...", 
            bg=self.cores["secao_bg"],
            font=FONTES["titulo"]
        )
        self.label_carregando_seguimiento.pack(expand=True, fill="both")
        
        # Agendar a criação real dos componentes após um breve delay
        frame_secao.after(100, lambda: self._criar_conteudo_seguimiento(frame_secao))

    def _criar_conteudo_seguimiento(self, frame_secao):
        """Cria o conteúdo real da seção após o delay"""
        if not hasattr(self, 'label_carregando_seguimiento') or not self.label_carregando_seguimiento.winfo_exists():
            return
            
        # Remove o label de carregamento
        self.label_carregando_seguimiento.destroy()
        
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
        
        # Conteúdo da seção - Com um frame que garante alinhamento idêntico para ambos os lados
        frame_conteudo_secao = tk.Frame(frame_secao, bg=self.cores["secao_bg"])
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configurar layout para 2 colunas com mesmas propriedades
        frame_conteudo_secao.columnconfigure(0, weight=1, uniform="col")  # Uniform garante mesma largura
        frame_conteudo_secao.columnconfigure(1, weight=1, uniform="col")
        
        # ====== LADO ESQUERDO - Com estrutura igual ao lado direito ======
        frame_programacion = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"])
        frame_programacion.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Título com mesmo padding e estilo
        label_programacion = tk.Label(
            frame_programacion, 
            text="Programación de sesiones de seguimientos", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["cabecalho_card"]
        )
        label_programacion.pack(anchor="w", padx=5, pady=5)
        
        # Frame para próxima avaliação
        frame_fecha = tk.Frame(frame_programacion, bg=self.cores["secao_bg"])
        frame_fecha.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        label_fecha = tk.Label(
            frame_fecha, 
            text="Próxima evaluación:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_fecha.pack(side=tk.LEFT, anchor="w")
        
        # Espaçador para alinhar com o lado direito
        tk.Frame(frame_programacion, height=5, bg=self.cores["secao_bg"]).pack(fill=tk.X)
        
        # Campo de texto com o placeholder correto
        programacion = EditableLabel(
            frame_programacion,
            bg=self.cores["campo_bg"],
            placeholder="Detalles sobre la programación de las sesiones de seguimiento...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        programacion.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        programacion.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["programacion_seguimiento"] = programacion.text
        
        # ====== LADO DIREITO ======
        frame_criterios = tk.Frame(frame_conteudo_secao, bg=self.cores["secao_bg"])
        frame_criterios.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        label_criterios = tk.Label(
            frame_criterios, 
            text="Criterios para la revisión del plan de tratamiento", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["cabecalho_card"]
        )
        label_criterios.pack(anchor="w", padx=5, pady=5)

        label_revisar = tk.Label(
            frame_criterios, 
            text="Revisar el plan si:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_revisar.pack(anchor="w", padx=5, pady=5)

        frame_radio = tk.Frame(frame_criterios, bg=self.cores["secao_bg"])
        frame_radio.pack(fill=tk.X, expand=True, padx=5, pady=5)

        var_criterio = tk.StringVar(value="no_mejora")
        self.radio_buttons["criterio_revision"] = var_criterio

        criterios = [
            ("No hay mejora en 3 sesiones", "no_mejora"),
            ("Hay mejora significativa", "mejora_significativa"),
            ("Hay empeoramiento", "empeoramiento"),
            ("Criterio personalizado", "personalizado")
        ]

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

        label_adicional = tk.Label(
            frame_criterios, 
            text="Criterios adicionales para la revisión del plan:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_adicional.pack(anchor="w", padx=5, pady=5)

        campo_adicional = EditableLabel(
            frame_criterios,
            bg=self.cores["campo_bg"],
            placeholder="Ingrese criterios adicionales si son necesarios...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_adicional.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        campo_adicional.text.bind("<KeyRelease>", lambda e: self.marcar_modificado())
        self.campos["criterios_adicionales"] = campo_adicional.text
        
        # Agora criamos o DateEntry depois que a interface está estável
        # Criação com atraso adicional para garantir que a aba esteja completamente carregada
        frame_secao.after(50, lambda: self._adicionar_date_entry(frame_fecha))

    def _adicionar_date_entry(self, frame_fecha):
        """Adiciona o DateEntry com segurança após a interface estar estável"""
        fecha_eval = DateEntryImproved(
            frame_fecha, 
            width=12, 
            bg=self.cores["secundaria"],
            fg='white', 
            date_pattern='dd/mm/yyyy',
            borderwidth=0,
            auto_popup=False
        )
        fecha_eval.pack(side=tk.LEFT, padx=5)
        self.campos["fecha_evaluacion"] = fecha_eval




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
        """Salva os dados do formulário e atualiza a aba de clientes"""
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
            
            # Processar radio button para força muscular
            dados['Fuerza Muscular'] = self.radio_buttons["grado_fuerza"].get()
            
            # Processar radio buttons
            for var_name, var in self.radio_buttons.items():
                dados[var_name] = var.get()
            
            # Inicializar banco de dados
            db = BancoDadosFisioterapia()
            
            # Salvar no banco de dados
            avaliacao_id = db.salvar_avaliacao(dados)
            
            # Resetar flag de modificação
            self.modificado = False
            
            # Se estivermos no contexto de uma aplicação integrada, atualizar a aba de clientes
            try:
                # Obter acesso ao notebook
                parent = self.frame.master
                
                # Procurar a aba de clientes
                for index in range(parent.index('end')):
                    tab_name = parent.tab(index, "text")
                    if tab_name == "Clientes":
                        # Encontrar a instância da AbaClientes
                        aba_clientes_frame = parent.winfo_children()[index]
                        if hasattr(aba_clientes_frame, 'winfo_children') and aba_clientes_frame.winfo_children():
                            for widget in aba_clientes_frame.winfo_children():
                                if hasattr(widget, 'carregar_pacientes'):
                                    # Se encontrarmos o método carregar_pacientes, chamamos ele
                                    widget.carregar_pacientes()
                                    break
                            
                # Alterar para a aba de clientes
                parent.select(0)  # Assumindo que a aba de clientes é a primeira
                
            except Exception as e:
                print(f"Aviso: Não foi possível atualizar a aba de clientes: {e}")
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo(
                "Guardar", 
                f"Evaluación guardada correctamente.\nID: {avaliacao_id}",
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