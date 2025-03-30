# aba_clientes.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import datetime
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import sys
import os
# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o banco de dados
from server.database import BancoDadosFisioterapia

# Importar as configurações
from config import CORES, FONTES, TAMANHOS

class AbaClientes:
    """
    Classe responsável pela aba de visualização e gerenciamento de clientes/pacientes.
    Permite visualizar a lista de todos os pacientes e seus dados cadastrados.
    """
    
    def __init__(self, parent):
        """Inicializa a aba de clientes"""
        # Criar frame principal
        self.frame = tk.Frame(parent, bg=CORES["fundo"])
        parent.add(self.frame, text="Clientes")
        
        # Instanciar o banco de dados
        self.db = BancoDadosFisioterapia()
        
        # Configurações
        self.cores = CORES
        
        # Estado atual
        self.paciente_selecionado = None
        self.avaliacao_id = None
        
        # Configurar o layout da aba
        self.configurar_aba()
        
        # Carregar dados iniciais
        self.carregar_pacientes()
    
    def configurar_aba(self):
        """Configura o layout da aba de clientes com tamanho expandido verticalmente"""
        # Frame principal com duas colunas
        self.frame_principal = tk.Frame(self.frame, bg=self.cores["fundo"])
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # IMPORTANTE: Configurar o frame principal para expandir verticalmente
        self.frame_principal.rowconfigure(0, weight=1)

        # Configurar colunas do frame principal - AJUSTAR PROPORÇÃO
        self.frame_principal.columnconfigure(0, weight=2, minsize=450)  # Lista de pacientes - mais larga
        self.frame_principal.columnconfigure(1, weight=3)  # Detalhes do paciente
        
        # ======= COLUNA ESQUERDA: LISTA DE PACIENTES =======
        self.frame_lista = tk.Frame(self.frame_principal, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        self.frame_lista.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # FIXAR LARGURA DA LISTA - AUMENTAR PARA MOSTRAR TODAS COLUNAS
        self.frame_lista.grid_propagate(False)  # Impede que o frame cresça além do tamanho definido
        self.frame_lista.config(width=450)      # Define uma largura maior para a lista
        
        # Título da lista
        frame_titulo_lista = tk.Frame(self.frame_lista, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo_lista.pack(fill=tk.X, padx=0, pady=0)
        
        titulo_lista = tk.Label(
            frame_titulo_lista, 
            text="LISTA DE PACIENTES", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        titulo_lista.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame de pesquisa
        frame_pesquisa = tk.Frame(self.frame_lista, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_pesquisa.pack(fill=tk.X)
        
        # Campo de pesquisa
        label_pesquisa = tk.Label(
            frame_pesquisa, 
            text="Pesquisar:", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_pesquisa.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.entry_pesquisa = tk.Entry(
            frame_pesquisa, 
            font=FONTES["campo"], 
            bg=self.cores["campo_bg"],
            fg=self.cores["texto"],
            width=20
        )
        self.entry_pesquisa.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.entry_pesquisa.bind("<KeyRelease>", self.pesquisar_pacientes)
        
        # Botão de pesquisa
        btn_pesquisar = tk.Button(
            frame_pesquisa, 
            text="Buscar", 
            command=lambda: self.pesquisar_pacientes(None),
            bg=self.cores["primaria"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"],
            padx=10,
            pady=2
        )
        btn_pesquisar.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame para o Treeview
        frame_treeview = tk.Frame(self.frame_lista, bg=self.cores["secao_bg"], padx=10, pady=5)
        frame_treeview.pack(fill=tk.BOTH, expand=True)
        
        # Configurar layout interno do frame_treeview para expansão
        frame_treeview.columnconfigure(0, weight=1)
        frame_treeview.rowconfigure(0, weight=1)
        
        # Configurar estilo do Treeview
        estilo = ttk.Style()
        estilo.configure(
            "Treeview", 
            background=self.cores["secao_bg"],
            foreground=self.cores["texto"],
            rowheight=25,
            font=FONTES["campo"]
        )
        estilo.configure(
            "Treeview.Heading", 
            background=self.cores["secundaria"],
            foreground=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        
        # Criar scrollbar
        scrollbar = tk.Scrollbar(frame_treeview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Criar Treeview (tabela) - ISTO DEVE VIR ANTES DE CONFIGURAR AS COLUNAS
        self.treeview = ttk.Treeview(
            frame_treeview,
            columns=('id', 'nome', 'idade', 'genero', 'data', 'proxima_avaliacao'),
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        scrollbar.config(command=self.treeview.yview)

        # Configurar colunas
        self.treeview.heading('id', text='ID')
        self.treeview.heading('nome', text='Nome')
        self.treeview.heading('idade', text='Idade')
        self.treeview.heading('genero', text='Gênero')
        self.treeview.heading('data', text='Data Cadastro')
        self.treeview.heading('proxima_avaliacao', text='Próxima Avaliação')

        # Ajustar largura das colunas - AGORA ISTO VEM DEPOIS DE CRIAR O TREEVIEW
        self.treeview.column('id', width=50, minwidth=50)
        self.treeview.column('nome', width=180, minwidth=150)  # Mais espaço para o nome
        self.treeview.column('idade', width=50, minwidth=50)
        self.treeview.column('genero', width=60, minwidth=50)
        self.treeview.column('data', width=90, minwidth=80)    # Mais espaço para data
        self.treeview.column('proxima_avaliacao', width=110, minwidth=100)  # Mais espaço para próxima avaliação
        
        # Empacotar Treeview
        self.treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Vincular evento de seleção
        self.treeview.bind('<<TreeviewSelect>>', self.ao_selecionar_paciente)
        
        # Botões de ação para a lista
        frame_botoes_lista = tk.Frame(self.frame_lista, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_botoes_lista.pack(fill=tk.X)
        
        btn_atualizar = tk.Button(
            frame_botoes_lista, 
            text="Atualizar Lista", 
            command=self.carregar_pacientes,
            bg=self.cores["secundaria"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5
        )
        btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)
        
        btn_excluir = tk.Button(
            frame_botoes_lista, 
            text="Excluir Paciente", 
            command=self.confirmar_excluir_paciente,
            bg=self.cores["erro"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5
        )
        btn_excluir.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # ======= COLUNA DIREITA: DETALHES DO PACIENTE =======
        self.frame_detalhes = tk.Frame(self.frame_principal, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        self.frame_detalhes.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Garantir que o frame_detalhes expanda
        self.frame_detalhes.grid_propagate(False)  # Impede que o frame encolha para o tamanho do conteúdo
        
        # Título dos detalhes
        frame_titulo_detalhes = tk.Frame(self.frame_detalhes, bg=self.cores["titulo_bg"], bd=0)
        frame_titulo_detalhes.pack(fill=tk.X, padx=0, pady=0)
        
        self.titulo_detalhes = tk.Label(
            frame_titulo_detalhes, 
            text="DETALHES DO PACIENTE", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["titulo"]
        )
        self.titulo_detalhes.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame para rolagem
        self.frame_rolagem = tk.Frame(self.frame_detalhes, bg=self.cores["secao_bg"])
        self.frame_rolagem.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Canvas para rolagem
        self.canvas_detalhes = tk.Canvas(
            self.frame_rolagem, 
            bg=self.cores["secao_bg"], 
            highlightthickness=0
        )
        self.scrollbar_detalhes = tk.Scrollbar(
            self.frame_rolagem, 
            orient="vertical", 
            command=self.canvas_detalhes.yview
        )
        
        # Configurar canvas
        self.canvas_detalhes.configure(yscrollcommand=self.scrollbar_detalhes.set)
        
        # Layout dos componentes
        self.scrollbar_detalhes.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_detalhes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para conteúdo dos detalhes
        self.frame_conteudo_detalhes = tk.Frame(
            self.canvas_detalhes, 
            bg=self.cores["secao_bg"], 
            padx=TAMANHOS["padding_padrao"], 
            pady=TAMANHOS["padding_padrao"]
        )
        
        # Vincular frame ao canvas
        self.frame_conteudo_detalhes.bind(
            "<Configure>", 
            lambda e: self.canvas_detalhes.configure(scrollregion=self.canvas_detalhes.bbox("all"))
        )
        
        # Criar janela para conteúdo
        self.canvas_window = self.canvas_detalhes.create_window(
            (0, 0), 
            window=self.frame_conteudo_detalhes, 
            anchor="nw",
            width=self.canvas_detalhes.winfo_width()
        )
        
        # Ajustar largura do conteúdo quando o canvas for redimensionado
        self.canvas_detalhes.bind('<Configure>', self._ao_configurar_canvas)
        
        # Configurar eventos de scroll
        self.canvas_detalhes.bind_all("<MouseWheel>", self._ao_rolar_mouse_windows)
        self.canvas_detalhes.bind_all("<Button-4>", self._ao_rolar_mouse_linux_cima)
        self.canvas_detalhes.bind_all("<Button-5>", self._ao_rolar_mouse_linux_baixo)
        
        # Mensagem inicial
        self.label_selecione = tk.Label(
            self.frame_conteudo_detalhes, 
            text="Selecione um paciente para visualizar seus dados", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto"],
            font=FONTES["subtitulo_secao"]
        )
        self.label_selecione.pack(padx=20, pady=50)
        
        # Botões de ação para os detalhes
        self.frame_botoes_detalhes = tk.Frame(self.frame_detalhes, bg=self.cores["secao_bg"], padx=10, pady=10)
        self.frame_botoes_detalhes.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.btn_imprimir = tk.Button(
            self.frame_botoes_detalhes, 
            text="Imprimir Avaliação", 
            command=self.imprimir_avaliacao,
            bg=self.cores["secundaria"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5,
            state=tk.DISABLED  # Inicialmente desabilitado
        )
        self.btn_imprimir.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_nova_avaliacao = tk.Button(
            self.frame_botoes_detalhes, 
            text="Nova Avaliação", 
            command=self.abrir_nova_avaliacao,
            bg=self.cores["sucesso"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5,
            state=tk.DISABLED  # Inicialmente desabilitado
        )
        self.btn_nova_avaliacao.pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.btn_editar = tk.Button(
            self.frame_botoes_detalhes, 
            text="Editar Avaliação", 
            command=self.editar_avaliacao,
            bg=self.cores["aviso"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5,
            state=tk.DISABLED  # Inicialmente desabilitado
        )
        self.btn_editar.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def _ao_configurar_canvas(self, evento):
        """Ajusta o tamanho da janela do conteúdo quando o canvas é redimensionado"""
        # Definir a largura total do conteúdo
        canvas_width = evento.width
        
        # Atualizar a largura do frame interno
        self.canvas_detalhes.itemconfig(self.canvas_window, width=canvas_width)
        
        # Garantir que a região de rolagem cubra todo o conteúdo
        self.canvas_detalhes.configure(scrollregion=self.canvas_detalhes.bbox("all"))

    def _ao_rolar_mouse_windows(self, evento):
        """Otimizado para reduzir a carga durante a rolagem"""
        if hasattr(self, '_scroll_timer'):
            self.after_cancel(self._scroll_timer)
        
        # Executa a rolagem imediatamente
        self.canvas_detalhes.yview_scroll(int(-1 * (evento.delta / 120)), "units")
        
        # Define um temporizador para atualizar a região de rolagem após o término da rolagem
        self._scroll_timer = self.after(150, lambda: self.canvas_detalhes.configure(
            scrollregion=self.canvas_detalhes.bbox("all")))
    
    def _ao_rolar_mouse_linux_cima(self, evento):
        """Trata evento de rolagem para cima no Linux"""
        self.canvas_detalhes.yview_scroll(-1, "units")
    
    def _ao_rolar_mouse_linux_baixo(self, evento):
        """Trata evento de rolagem para baixo no Linux"""
        self.canvas_detalhes.yview_scroll(1, "units")
    
    def carregar_pacientes(self):
        """Carrega a lista de pacientes do banco de dados com virtualização"""
        # Limpar Treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Obter lista de avaliações (limitada a 100 por vez para desempenho)
        avaliacoes = self.db.listar_avaliacoes(limite=100)
        
        # Preencher Treeview
        for avaliacao in avaliacoes:
            data_formatada = self._formatar_data(avaliacao.get('data', ''))
            proxima_avaliacao = self._formatar_data(avaliacao.get('fecha_evaluacion', ''))
            
            self.treeview.insert(
                '', 
                'end', 
                values=(
                    avaliacao.get('id', ''),
                    avaliacao.get('nome', ''),
                    avaliacao.get('idade', ''),
                    avaliacao.get('genero', ''),
                    data_formatada,
                    proxima_avaliacao
                )
            )
    
    def _formatar_data(self, data_str):
        """Formata a data para exibição"""
        try:
            # Converter string para datetime
            data = datetime.datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
            # Retornar formato brasileiro
            return data.strftime('%d/%m/%Y')
        except:
            return data_str
    
    def pesquisar_pacientes(self, evento=None):
        """Filtra a lista de pacientes com base no texto de pesquisa"""
        # Obter texto de pesquisa
        texto_pesquisa = self.entry_pesquisa.get().strip().lower()
        
        # Limpar Treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        if not texto_pesquisa:
            # Se não houver texto de pesquisa, mostrar todos
            self.carregar_pacientes()
            return
        
        # Obter lista de avaliações (que contém os pacientes)
        avaliacoes = self.db.listar_avaliacoes(filtro=texto_pesquisa)
        
        # Preencher Treeview com resultados filtrados
        for avaliacao in avaliacoes:
            data_formatada = self._formatar_data(avaliacao['data'])
            
            self.treeview.insert(
                '', 
                'end', 
                values=(
                    avaliacao['id'],
                    avaliacao['nome'],
                    avaliacao['idade'],
                    avaliacao['genero'],
                    data_formatada
                )
            )
    
    def ao_selecionar_paciente(self, evento=None):
        """Chamado quando um paciente é selecionado na lista"""
        # Obter item selecionado
        selecao = self.treeview.selection()
        if not selecao:
            return
        
        # Obter ID da avaliação
        item = self.treeview.item(selecao[0])
        avaliacao_id = item['values'][0]
        
        # Armazenar ID da avaliação selecionada
        self.avaliacao_id = avaliacao_id
        
        # Obter dados completos da avaliação
        dados = self.db.obter_avaliacao(avaliacao_id)
        if not dados:
            messagebox.showerror("Erro", "Não foi possível carregar os dados do paciente.")
            return
        
        # Depuração - verificar todos os dados recebidos
        print(f"Dados recebidos para o paciente: {dados.keys()}")
        
        # Armazenar paciente selecionado
        self.paciente_selecionado = dados
        
        # Atualizar título com nome do paciente
        self.titulo_detalhes.config(text=f"DETALHES: {dados.get('Nombre Completo', 'Paciente')}")
        
        # Limpar conteúdo atual
        for widget in self.frame_conteudo_detalhes.winfo_children():
            widget.destroy()
        
        # Habilitar botões de ação
        self.btn_imprimir.config(state=tk.NORMAL)
        self.btn_nova_avaliacao.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.NORMAL)
        
        # Mostrar dados do paciente organizados em seções
        self.exibir_dados_paciente(dados)
        
        # Garantir atualização da região de rolagem
        self.canvas_detalhes.update_idletasks()
        self.canvas_detalhes.configure(scrollregion=self.canvas_detalhes.bbox("all"))
    
    def exibir_dados_paciente(self, dados):
        """Exibe os dados do paciente selecionado de forma organizada e completa"""
        # Limpar o conteúdo atual
        for widget in self.frame_conteudo_detalhes.winfo_children():
            widget.destroy()
        
        # Usar padding mais compacto para acomodar mais conteúdo
        padding_secao = 5
        
        # Criar uma lista ordenada de todas as seções e seus campos
        secoes = [
            {
                "titulo": "INFORMAÇÕES BÁSICAS",
                "campos": ["Nombre Completo", "Edad", "Genero", "Contacto", "Fecha Nasc.", 
                        "Área de consulta", "Alergias", "data_avaliacao"]
            },
            {
                "titulo": "HISTÓRIA CLÍNICA",
                "campos": ["Motivo de consulta", "Antecedentes", "Efermedad actual", 
                        "Cirurgías previas", "Medicamentos actuales"]
            },
            {
                "titulo": "AVALIAÇÃO FÍSICA",
                "subsecoes": [
                    {"titulo": "Parâmetros Vitais", 
                    "campos": ["PA", "Pulso", "Talla", "Peso", "T", "FR", "Sat.O2"]},
                    {"titulo": "Inspeção e Palpação", 
                    "campos": ["Postura", "Simetría corporal", "Deformidades aparentes", 
                            "Puntos dolorosos", "Tensión muscular"]},
                    {"titulo": "Coluna Vertebral", 
                    "campos": ["Curvas Fisiológicas", "Presencia de Escoliosis", "Cifosis o Lordosis"]},
                    {"titulo": "Mobilidade Articular", 
                    "campos": ["Movimiento Activo", "Movimiento Pasivo", "Evaluación de articulaciones"]},
                    {"titulo": "Força e Avaliação Neuromuscular", 
                    "campos": ["Fuerza Muscular", "Evaluación de grupos musculares", "Reflejos", 
                            "Coordinación motora", "Equilibrio"]}
                ]
            },
            {
                "titulo": "TESTES ESPECIAIS",
                "campos": ["Pruebas ortopédicas", "Pruebas neurológicas", "Pruebas de estabilidad"]
            },
            {
                "titulo": "AVALIAÇÃO FUNCIONAL E DOR",
                "campos": ["Capacidad para realizar actividades diarias", "Limitaciones y dificultades", 
                        "escala_eva", "observaciones_dolor"]
            },
            {
                "titulo": "DIAGNÓSTICO E TRATAMENTO",
                "campos": ["IDx", "Conducta", "Resumen del problema", "Objetivos del tratamiento", 
                        "sesiones_semana", "duracion_sesion", "obs_frecuencia", 
                        "Ejercicios recomendados"]
            },
            {
                "titulo": "SEGUIMENTO E REAVALIAÇÃO",
                "campos": ["programacion_seguimiento", "fecha_evaluacion", 
                        "criterio_revision", "criterios_adicionales"]
            }
        ]
        
        # Percorrer cada seção e criar os componentes visuais
        for secao in secoes:
            # Verificar se há algum dado para esta seção
            tem_dados = False
            
            # Se a seção tem subsecoes, verificar em cada uma
            if 'subsecoes' in secao:
                for subsecao in secao['subsecoes']:
                    if any(dados.get(campo) for campo in subsecao['campos']):
                        tem_dados = True
                        break
            else:
                # Verificar nos campos da seção
                if any(dados.get(campo) for campo in secao['campos']):
                    tem_dados = True
            
            # Se não tiver dados relevantes, pular esta seção
            if not tem_dados:
                continue
            
            # Criar o frame da seção
            frame_secao = tk.Frame(self.frame_conteudo_detalhes, 
                                bg=self.cores["secao_bg"], 
                                bd=1, 
                                relief=tk.SOLID)
            frame_secao.pack(fill=tk.X, expand=False, padx=5, pady=3)
            
            # Título da seção
            frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
            frame_titulo.pack(fill=tk.X)
            
            titulo = tk.Label(
                frame_titulo, 
                text=secao["titulo"], 
                bg=self.cores["titulo_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["subtitulo_secao"]
            )
            titulo.pack(side=tk.LEFT, padx=10, pady=5)
            
            # Frame para os dados da seção
            frame_dados = tk.Frame(frame_secao, bg=self.cores["secao_bg"], 
                                padx=padding_secao, pady=padding_secao)
            frame_dados.pack(fill=tk.X)
            
            # Se tiver subsecoes, criar cada uma
            if 'subsecoes' in secao:
                for i, subsecao in enumerate(secao['subsecoes']):
                    # Verificar se há dados nesta subseção
                    if not any(dados.get(campo) for campo in subsecao['campos']):
                        continue
                    
                    # Adicionar um separador entre subseções (exceto na primeira)
                    if i > 0:
                        separador = tk.Frame(frame_dados, height=1, bg="#cccccc")
                        separador.pack(fill=tk.X, pady=5)
                    
                    # Título da subseção
                    label_subsecao = tk.Label(
                        frame_dados, 
                        text=subsecao["titulo"], 
                        bg=self.cores["secao_bg"],
                        fg=self.cores["texto_destaque"],
                        font=FONTES["campo"]
                    )
                    label_subsecao.pack(anchor="w", padx=5, pady=3)
                    
                    # Grid para os campos desta subseção
                    grid_campos = tk.Frame(frame_dados, bg=self.cores["secao_bg"])
                    grid_campos.pack(fill=tk.X, padx=10)
                    
                    # Adicionar os campos
                    for j, campo in enumerate(subsecao['campos']):
                        if dados.get(campo):
                            # Label do campo
                            label_campo = tk.Label(
                                grid_campos, 
                                text=f"{campo}:", 
                                bg=self.cores["secao_bg"],
                                fg=self.cores["texto_destaque"],
                                font=FONTES["campo_pequeno"]
                            )
                            label_campo.grid(row=j, column=0, padx=5, pady=2, sticky="w")
                            
                            # Valor do campo (com tratamento especial para listas)
                            valor = dados.get(campo)
                            if isinstance(valor, list):
                                valor = ", ".join(valor)
                            
                            valor_campo = tk.Label(
                                grid_campos, 
                                text=str(valor), 
                                bg=self.cores["secao_bg"],
                                fg=self.cores["texto"],
                                font=FONTES["campo_pequeno"],
                                wraplength=350,
                                justify=tk.LEFT
                            )
                            valor_campo.grid(row=j, column=1, padx=5, pady=2, sticky="w")
            else:
                # Grid para os campos desta seção
                for i, campo in enumerate(secao['campos']):
                    if dados.get(campo):
                        # Label do campo
                        label_campo = tk.Label(
                            frame_dados, 
                            text=f"{campo}:", 
                            bg=self.cores["secao_bg"],
                            fg=self.cores["texto_destaque"],
                            font=FONTES["campo"]
                        )
                        label_campo.grid(row=i, column=0, padx=5, pady=2, sticky="w")
                        
                        # Valor do campo
                        valor = dados.get(campo)
                        if isinstance(valor, list):
                            valor = ", ".join(valor)
                        
                        valor_campo = tk.Label(
                            frame_dados, 
                            text=str(valor), 
                            bg=self.cores["secao_bg"],
                            fg=self.cores["texto"],
                            font=FONTES["campo"],
                            wraplength=350,
                            justify=tk.LEFT
                        )
                        valor_campo.grid(row=i, column=1, padx=5, pady=2, sticky="w")
        
        # Atualizar região de rolagem
        self.canvas_detalhes.update_idletasks()
        self.canvas_detalhes.configure(scrollregion=self.canvas_detalhes.bbox("all"))
        
        # Voltar ao topo da visualização
        self.canvas_detalhes.yview_moveto(0)
    
    def _criar_secao_info_basica(self, dados, padding=10):
        """Cria a seção de informações básicas do paciente"""
        frame_secao = tk.Frame(self.frame_conteudo_detalhes, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X)
        
        titulo = tk.Label(
            frame_titulo, 
            text="INFORMAÇÕES BÁSICAS", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame para os dados
        frame_dados = tk.Frame(frame_secao, bg=self.cores["secao_bg"], padx=padding, pady=padding)
        frame_dados.pack(fill=tk.X)
        
        # Grid para organizar os dados
        frame_dados.columnconfigure(0, weight=0, minsize=120)  # Rótulos
        frame_dados.columnconfigure(1, weight=1)               # Valores
        frame_dados.columnconfigure(2, weight=0, minsize=120)  # Rótulos adicionais
        frame_dados.columnconfigure(3, weight=1)               # Valores adicionais
        
        # Linha 1: Nome e Idade
        self._adicionar_campo_grid(frame_dados, "Nome:", dados.get('Nombre Completo', '-'), 0, 0)
        self._adicionar_campo_grid(frame_dados, "Idade:", dados.get('Edad', '-'), 0, 2)
        
        # Linha 2: Gênero e Contato
        self._adicionar_campo_grid(frame_dados, "Gênero:", dados.get('Genero', '-'), 1, 0)
        self._adicionar_campo_grid(frame_dados, "Contato:", dados.get('Contacto', '-'), 1, 2)
        
        # Linha 3: Data de Nascimento e Área de Consulta
        self._adicionar_campo_grid(frame_dados, "Data Nasc.:", dados.get('Fecha Nasc.', '-'), 2, 0)
        self._adicionar_campo_grid(frame_dados, "Área:", dados.get('Área de consulta', '-'), 2, 2)
        
        # Linha 4: Alergias (ocupando toda a largura)
        self._adicionar_campo_grid(frame_dados, "Alergias:", dados.get('Alergias', '-'), 3, 0, colspan=3)
        
        # Linha 5: Data de Avaliação
        self._adicionar_campo_grid(frame_dados, "Avaliação:", self._formatar_data(dados.get('data_avaliacao', '-')), 4, 0)
    
    def _criar_secao_historia_clinica(self, dados, padding=10):
        """Cria a seção de história clínica"""
        # Verificar se há dados relevantes
        tem_dados = any([
            dados.get('Motivo de consulta', ''),
            dados.get('Antecedentes', ''),
            dados.get('Efermedad actual', ''),
            dados.get('Cirurgías previas', ''),
            dados.get('Medicamentos actuales', '')
        ])
        
        if not tem_dados:
            return
        
        frame_secao = tk.Frame(self.frame_conteudo_detalhes, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X)
        
        titulo = tk.Label(
            frame_titulo, 
            text="HISTÓRIA CLÍNICA", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame para os dados
        frame_dados = tk.Frame(frame_secao, bg=self.cores["secao_bg"], padx=padding, pady=padding)
        frame_dados.pack(fill=tk.X)
        
        # Grid para organizar os dados
        frame_dados.columnconfigure(0, weight=0, minsize=120)  # Rótulos
        frame_dados.columnconfigure(1, weight=1)               # Valores
        
        # Adicionar campos se existirem
        linha = 0
        if dados.get('Motivo de consulta', ''):
            self._adicionar_campo_grid(frame_dados, "Motivo:", dados['Motivo de consulta'], linha, 0, wraplength=500)
            linha += 1
            
        if dados.get('Antecedentes', ''):
            self._adicionar_campo_grid(frame_dados, "Antecedentes:", dados['Antecedentes'], linha, 0, wraplength=500)
            linha += 1
            
        if dados.get('Efermedad actual', ''):
            self._adicionar_campo_grid(frame_dados, "Enfermidade:", dados['Efermedad actual'], linha, 0, wraplength=500)
            linha += 1
            
        if dados.get('Cirurgías previas', ''):
            self._adicionar_campo_grid(frame_dados, "Cirurgias:", dados['Cirurgías previas'], linha, 0, wraplength=500)
            linha += 1
            
        if dados.get('Medicamentos actuales', ''):
            self._adicionar_campo_grid(frame_dados, "Medicamentos:", dados['Medicamentos actuales'], linha, 0, wraplength=500)
            linha += 1
    
    def _criar_secao_avaliacao_fisica(self, dados, padding=10):
        """Cria a seção de avaliação física com todas as informações"""
        # Verificar se há pelo menos algum dado da avaliação física
        tem_exame = any([
            dados.get('PA', ''), dados.get('Pulso', ''), dados.get('Talla', ''),
            dados.get('Peso', ''), dados.get('T', ''), dados.get('FR', ''),
            dados.get('Sat.O2', ''), dados.get('IDx', ''), dados.get('Conducta', '')
        ])
        
        tem_inspecao = any([
            dados.get('Postura', ''), dados.get('Simetría corporal', ''),
            dados.get('Deformidades aparentes', ''), dados.get('Puntos dolorosos', ''),
            dados.get('Tensión muscular', '')
        ])
        
        # Mesmo que não tenha dados específicos, criar a seção se tiver escala EVA
        tem_avaliacao = tem_exame or tem_inspecao or 'escala_eva' in dados
        
        if not tem_avaliacao:
            print("Sem dados de avaliação física detectados.")
            return
        
        frame_secao = tk.Frame(self.frame_conteudo_detalhes, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X)
        
        titulo = tk.Label(
            frame_titulo, 
            text="AVALIAÇÃO FÍSICA", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame para os dados
        frame_dados = tk.Frame(frame_secao, bg=self.cores["secao_bg"], padx=padding, pady=padding)
        frame_dados.pack(fill=tk.X)
        
        # Verificar e exibir a escala de dor
        if dados.get('escala_eva') is not None:
            # Frame para a escala EVA
            frame_eva = tk.Frame(frame_dados, bg=self.cores["secao_bg"], padx=5, pady=5)
            frame_eva.pack(fill=tk.X, padx=5, pady=5)
            
            # Título da escala
            label_eva = tk.Label(
                frame_eva, 
                text="Escala de Dor (EVA):", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label_eva.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Valor da escala
            valor_eva = dados.get('escala_eva', 0)
            label_valor = tk.Label(
                frame_eva, 
                text=f"{valor_eva}/10", 
                bg=self.cores["secao_bg"],
                fg=self.cores["primaria"],
                font=FONTES["campo_destaque"]
            )
            label_valor.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Observações sobre a dor
            if dados.get('observaciones_dolor', ''):
                label_obs = tk.Label(
                    frame_dados, 
                    text="Observações sobre a dor:", 
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto_destaque"],
                    font=FONTES["campo"]
                )
                label_obs.pack(anchor="w", padx=5, pady=(10, 0))
                
                text_obs = tk.Label(
                    frame_dados, 
                    text=dados.get('observaciones_dolor', ''),
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto"],
                    font=FONTES["campo"],
                    wraplength=500,
                    justify=tk.LEFT
                )
                text_obs.pack(anchor="w", padx=15, pady=5)
        
        # Adicionar parâmetros do exame físico se existirem
        if tem_exame:
            # Separador
            separador = tk.Frame(frame_dados, height=1, bg="#cccccc")
            separador.pack(fill=tk.X, pady=10)
            
            # Título do exame físico
            label_exame = tk.Label(
                frame_dados, 
                text="Exame Físico:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["subtitulo_campo"]
            )
            label_exame.pack(anchor="w", padx=5, pady=5)
            
            # Frame para parâmetros vitais
            frame_parametros = tk.Frame(frame_dados, bg=self.cores["secao_bg"])
            frame_parametros.pack(fill=tk.X, padx=5, pady=5)
            
            # Grid para organizar os parâmetros
            frame_parametros.columnconfigure(0, weight=0)  # Rótulo
            frame_parametros.columnconfigure(1, weight=0)  # Valor
            frame_parametros.columnconfigure(2, weight=0)  # Unidade
            frame_parametros.columnconfigure(3, weight=0)  # Espaço
            frame_parametros.columnconfigure(4, weight=0)  # Rótulo
            frame_parametros.columnconfigure(5, weight=0)  # Valor
            frame_parametros.columnconfigure(6, weight=0)  # Unidade
            frame_parametros.columnconfigure(7, weight=1)  # Preenchimento
            
            # Linha 1: PA e Pulso
            col = 0
            if dados.get('PA', ''):
                self._adicionar_parametro(frame_parametros, "PA:", dados['PA'], "mmHg", 0, col)
                col += 4
                
            if dados.get('Pulso', ''):
                self._adicionar_parametro(frame_parametros, "Pulso:", dados['Pulso'], "lpm", 0, col)
            
            # Linha 2: Talla e Peso
            col = 0
            if dados.get('Talla', ''):
                self._adicionar_parametro(frame_parametros, "Altura:", dados['Talla'], "cm", 1, col)
                col += 4
                
            if dados.get('Peso', ''):
                self._adicionar_parametro(frame_parametros, "Peso:", dados['Peso'], "kg", 1, col)
            
            # Linha 3: Temperatura e FR
            col = 0
            if dados.get('T', ''):
                self._adicionar_parametro(frame_parametros, "Temp:", dados['T'], "°C", 2, col)
                col += 4
                
            if dados.get('FR', ''):
                self._adicionar_parametro(frame_parametros, "FR:", dados['FR'], "rpm", 2, col)
            
            # Linha 4: Sat.O2 e IDx
            col = 0
            if dados.get('Sat.O2', ''):
                self._adicionar_parametro(frame_parametros, "Sat.O2:", dados['Sat.O2'], "%", 3, col)
            
            # Adicionar Conduta se existir
            if dados.get('Conducta', ''):
                # Separador
                separador_conducta = tk.Frame(frame_dados, height=1, bg="#dddddd")
                separador_conducta.pack(fill=tk.X, pady=5)
                
                # Rótulo
                label_conducta = tk.Label(
                    frame_dados, 
                    text="Conduta:", 
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto_destaque"],
                    font=FONTES["campo"]
                )
                label_conducta.pack(anchor="w", padx=5, pady=5)
                
                # Valor
                text_conducta = tk.Label(
                    frame_dados, 
                    text=dados.get('Conducta', ''),
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto"],
                    font=FONTES["campo"],
                    wraplength=500,
                    justify=tk.LEFT
                )
                text_conducta.pack(anchor="w", padx=15, pady=5)
        
        # Adicionar dados de inspeção e palpação se existirem
        if tem_inspecao:
            # Separador
            separador = tk.Frame(frame_dados, height=1, bg="#cccccc")
            separador.pack(fill=tk.X, pady=10)
            
            # Título da inspeção
            label_inspecao = tk.Label(
                frame_dados, 
                text="Inspeção e Palpação:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["subtitulo_campo"]
            )
            label_inspecao.pack(anchor="w", padx=5, pady=5)
            
            # Grid para inspeção e palpação
            frame_inspecao = tk.Frame(frame_dados, bg=self.cores["secao_bg"], padx=10, pady=5)
            frame_inspecao.pack(fill=tk.X)
            
            linha = 0
            # Adicionar campos de inspeção se existirem
            campos_inspecao = [
                ('Postura', 'Postura'),
                ('Simetría corporal', 'Simetria corporal'),
                ('Deformidades aparentes', 'Deformidades aparentes'),
                ('Puntos dolorosos', 'Pontos dolorosos'),
                ('Tensión muscular', 'Tensão muscular')
            ]
            
            for chave, rotulo in campos_inspecao:
                if dados.get(chave, ''):
                    label = tk.Label(
                        frame_inspecao, 
                        text=f"{rotulo}:", 
                        bg=self.cores["secao_bg"],
                        fg=self.cores["texto_destaque"],
                        font=FONTES["campo"]
                    )
                    label.grid(row=linha, column=0, padx=5, pady=3, sticky="w")
                    
                    valor = tk.Label(
                        frame_inspecao, 
                        text=dados.get(chave, ''),
                        bg=self.cores["secao_bg"],
                        fg=self.cores["texto"],
                        font=FONTES["campo"],
                        wraplength=450,
                        justify=tk.LEFT
                    )
                    valor.grid(row=linha, column=1, padx=5, pady=3, sticky="w")
                    
                    linha += 1
    
    def _criar_secao_diagnostico_tratamento(self, dados, padding=10):
        """Cria a seção de diagnóstico e tratamento"""
        # Verificar se há dados relevantes
        tem_dados = any([
            dados.get('Resumen del problema', ''),
            dados.get('Objetivos del tratamiento', ''),
            dados.get('sesiones_semana', ''),
            dados.get('duracion_sesion', ''),
            dados.get('Ejercicios recomendados', '')
        ])
        
        if not tem_dados:
            return
        
        frame_secao = tk.Frame(self.frame_conteudo_detalhes, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X)
        
        titulo = tk.Label(
            frame_titulo, 
            text="DIAGNÓSTICO E TRATAMENTO", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame para os dados
        frame_dados = tk.Frame(frame_secao, bg=self.cores["secao_bg"], padx=padding, pady=padding)
        frame_dados.pack(fill=tk.X)
        
        # Adicionar diagnóstico se existir
        if dados.get('Resumen del problema', ''):
            label_problema = tk.Label(
                frame_dados, 
                text="Resumo do problema:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label_problema.pack(anchor="w", padx=5, pady=5)
            
            text_problema = tk.Label(
                frame_dados, 
                text=dados.get('Resumen del problema', ''),
                bg=self.cores["secao_bg"],
                fg=self.cores["texto"],
                font=FONTES["campo"],
                wraplength=500,
                justify=tk.LEFT
            )
            text_problema.pack(anchor="w", padx=15, pady=5)
        
        # Adicionar objetivos do tratamento se existir
        if dados.get('Objetivos del tratamiento', ''):
            label_objetivos = tk.Label(
                frame_dados, 
                text="Objetivos do tratamento:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label_objetivos.pack(anchor="w", padx=5, pady=(10, 5))
            
            text_objetivos = tk.Label(
                frame_dados, 
                text=dados.get('Objetivos del tratamiento', ''),
                bg=self.cores["secao_bg"],
                fg=self.cores["texto"],
                font=FONTES["campo"],
                wraplength=500,
                justify=tk.LEFT
            )
            text_objetivos.pack(anchor="w", padx=15, pady=5)
        
        # Adicionar frequência de sessões se existir
        if dados.get('sesiones_semana', '') or dados.get('duracion_sesion', ''):
            # Separador
            separador = tk.Frame(frame_dados, height=1, bg="#cccccc")
            separador.pack(fill=tk.X, pady=10)
            
            # Título da frequência
            label_frequencia = tk.Label(
                frame_dados, 
                text="Frequência do tratamento:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["subtitulo_campo"]
            )
            label_frequencia.pack(anchor="w", padx=5, pady=5)
            
            # Frame para a frequência
            frame_freq = tk.Frame(frame_dados, bg=self.cores["secao_bg"])
            frame_freq.pack(fill=tk.X, padx=15, pady=5)
            
            # Sessões por semana
            if dados.get('sesiones_semana', ''):
                label_sessoes = tk.Label(
                    frame_freq, 
                    text="Sessões por semana:", 
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto_destaque"],
                    font=FONTES["campo"]
                )
                label_sessoes.pack(side=tk.LEFT, padx=5, pady=5)
                
                valor_sessoes = tk.Label(
                    frame_freq, 
                    text=dados.get('sesiones_semana', ''),
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto"],
                    font=FONTES["campo"]
                )
                valor_sessoes.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Duração da sessão
            if dados.get('duracion_sesion', ''):
                label_duracao = tk.Label(
                    frame_freq, 
                    text="Duração da sessão:", 
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto_destaque"],
                    font=FONTES["campo"]
                )
                label_duracao.pack(side=tk.LEFT, padx=(20, 5), pady=5)
                
                valor_duracao = tk.Label(
                    frame_freq, 
                    text=dados.get('duracion_sesion', ''),
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto"],
                    font=FONTES["campo"]
                )
                valor_duracao.pack(side=tk.LEFT, padx=5, pady=5)
            
            # Observações sobre a frequência
            if dados.get('obs_frecuencia', ''):
                label_obs_freq = tk.Label(
                    frame_dados, 
                    text="Observações sobre a frequência:", 
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto_destaque"],
                    font=FONTES["campo"]
                )
                label_obs_freq.pack(anchor="w", padx=5, pady=(10, 5))
                
                text_obs_freq = tk.Label(
                    frame_dados, 
                    text=dados.get('obs_frecuencia', ''),
                    bg=self.cores["secao_bg"],
                    fg=self.cores["texto"],
                    font=FONTES["campo"],
                    wraplength=500,
                    justify=tk.LEFT
                )
                text_obs_freq.pack(anchor="w", padx=15, pady=5)
        
        # Adicionar exercícios recomendados se existir
        if dados.get('Ejercicios recomendados', ''):
            # Separador
            separador = tk.Frame(frame_dados, height=1, bg="#cccccc")
            separador.pack(fill=tk.X, pady=10)
            
            label_exercicios = tk.Label(
                frame_dados, 
                text="Exercícios recomendados:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["subtitulo_campo"]
            )
            label_exercicios.pack(anchor="w", padx=5, pady=5)
            
            text_exercicios = tk.Label(
                frame_dados, 
                text=dados.get('Ejercicios recomendados', ''),
                bg=self.cores["secao_bg"],
                fg=self.cores["texto"],
                font=FONTES["campo"],
                wraplength=500,
                justify=tk.LEFT
            )
            text_exercicios.pack(anchor="w", padx=15, pady=5)
    
    def _criar_secao_seguimento(self, dados, padding=10):
        """Cria a seção de seguimento e reavaliação"""
        # Verificar se há dados relevantes
        tem_dados = any([
            dados.get('programacion_seguimiento', ''),
            dados.get('fecha_evaluacion', ''),
            dados.get('criterio_revision', ''),
            dados.get('criterios_adicionales', '')
        ])
        
        if not tem_dados:
            return
        
        frame_secao = tk.Frame(self.frame_conteudo_detalhes, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        frame_secao.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Título da seção
        frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
        frame_titulo.pack(fill=tk.X, padx=0, pady=0)
        
        titulo = tk.Label(
            frame_titulo, 
            text="SEGUIMIENTO Y REEVALUACIÓN", 
            bg=self.cores["titulo_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["subtitulo_secao"]
        )
        titulo.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Frame para os dados
        frame_dados = tk.Frame(frame_secao, bg=self.cores["secao_bg"], padx=padding, pady=padding)
        frame_dados.pack(fill=tk.X)
        
        # Data da próxima avaliação
        if dados.get('fecha_evaluacion', ''):
            frame_data = tk.Frame(frame_dados, bg=self.cores["secao_bg"])
            frame_data.pack(fill=tk.X, padx=5, pady=5)
            
            label_data = tk.Label(
                frame_data, 
                text="Próxima evaluación:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label_data.pack(side=tk.LEFT, padx=5, pady=5)
            
            valor_data = tk.Label(
                frame_data, 
                text=dados.get('fecha_evaluacion', ''),
                bg=self.cores["secao_bg"],
                fg=self.cores["secundaria"],
                font=FONTES["campo_destaque"]
            )
            valor_data.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Programação do seguimento
        if dados.get('programacion_seguimiento', ''):
            label_prog = tk.Label(
                frame_dados, 
                text="Programación del seguimiento:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label_prog.pack(anchor="w", padx=5, pady=(10, 5))
            
            text_prog = tk.Label(
                frame_dados, 
                text=dados.get('programacion_seguimiento', ''),
                bg=self.cores["secao_bg"],
                fg=self.cores["texto"],
                font=FONTES["campo"],
                wraplength=500,
                justify=tk.LEFT
            )
            text_prog.pack(anchor="w", padx=15, pady=5)
        
        # Critérios de revisão
        if dados.get('criterio_revision', ''):
            # Separador
            separador = tk.Frame(frame_dados, height=1, bg="#cccccc")
            separador.pack(fill=tk.X, pady=10)
            
            label_criterio = tk.Label(
                frame_dados, 
                text="Criterio para revisión del plan:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label_criterio.pack(anchor="w", padx=5, pady=5)
            
            # Mapear valores para texto legível
            criterios_map = {
                'no_mejora': "No hay mejora en 3 sesiones",
                'mejora_significativa': "Hay mejora significativa",
                'empeoramiento': "Hay empeoramiento",
                'personalizado': "Criterio personalizado"
            }
            
            valor_criterio = tk.Label(
                frame_dados, 
                text=criterios_map.get(dados.get('criterio_revision', ''), dados.get('criterio_revision', '')),
                bg=self.cores["secao_bg"],
                fg=self.cores["texto"],
                font=FONTES["campo"]
            )
            valor_criterio.pack(anchor="w", padx=15, pady=5)
        
        # Critérios adicionais
        if dados.get('criterios_adicionales', ''):
            label_adic = tk.Label(
                frame_dados, 
                text="Criterios adicionales:", 
                bg=self.cores["secao_bg"],
                fg=self.cores["texto_destaque"],
                font=FONTES["campo"]
            )
            label_adic.pack(anchor="w", padx=5, pady=(10, 5))
            
            text_adic = tk.Label(
                frame_dados, 
                text=dados.get('criterios_adicionales', ''),
                bg=self.cores["secao_bg"],
                fg=self.cores["texto"],
                font=FONTES["campo"],
                wraplength=500,
                justify=tk.LEFT
            )
            text_adic.pack(anchor="w", padx=15, pady=5)
    
    def _adicionar_campo_grid(self, parent, label_text, valor_text, row, col, colspan=1, wraplength=None):
        """Adiciona um campo de rótulo e valor no grid com suporte a quebra de linha"""
        # Rótulo
        label = tk.Label(
            parent, 
            text=label_text, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label.grid(row=row, column=col, padx=5, pady=3, sticky="ne")
        
        # Valor com quebra de linha opcional
        valor = tk.Label(
            parent, 
            text=valor_text,
            bg=self.cores["secao_bg"],
            fg=self.cores["texto"],
            font=FONTES["campo"],
            justify=tk.LEFT
        )
        
        # Aplicar quebra de linha se necessário
        if wraplength:
            valor.config(wraplength=wraplength)
        elif len(str(valor_text)) > 50:  # Quebrar textos muito longos automaticamente
            valor.config(wraplength=400)
        
        valor.grid(row=row, column=col+1, columnspan=colspan, padx=5, pady=3, sticky="nw")
    
    def _adicionar_parametro(self, parent, label_text, valor_text, unidade_text, row, col):
        """Adiciona um parâmetro com unidade no grid"""
        # Rótulo
        label = tk.Label(
            parent, 
            text=label_text, 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label.grid(row=row, column=col, padx=5, pady=3, sticky="e")
        
        # Valor
        valor = tk.Label(
            parent, 
            text=valor_text,
            bg=self.cores["secao_bg"],
            fg=self.cores["texto"],
            font=FONTES["campo"]
        )
        valor.grid(row=row, column=col+1, padx=(5, 2), pady=3, sticky="w")
        
        # Unidade - usando 'texto' em vez de 'texto_secundario'
        unidade = tk.Label(
            parent, 
            text=unidade_text,
            bg=self.cores["secao_bg"],
            fg=self.cores["texto"],  # Modificado para usar 'texto' em vez de 'texto_secundario'
            font=FONTES["campo_pequeno"]
        )
        unidade.grid(row=row, column=col+2, padx=(0, 15), pady=3, sticky="w")

    def depurar_campos_disponveis(self, dados):
        """Função para depurar os campos disponíveis nos dados"""
        print("\n=== CAMPOS DISPONÍVEIS ===")
        for chave, valor in dados.items():
            if valor:  # Mostrar apenas campos com valores
                print(f"Campo: {chave} = {valor}")
        print("=========================\n")
        
        # Adicione um log específico para verificar as seções de maior interesse
        print("Avaliação Física:")
        campos_fisica = ['PA', 'Pulso', 'Talla', 'Peso', 'T', 'FR', 'Sat.O2', 'escala_eva']
        for campo in campos_fisica:
            print(f"  - {campo}: {dados.get(campo, 'Não encontrado')}")
        
        print("\nDiagnóstico:")
        campos_diag = ['Resumen del problema', 'Objetivos del tratamiento']
        for campo in campos_diag:
            print(f"  - {campo}: {dados.get(campo, 'Não encontrado')}")
    
    def confirmar_excluir_paciente(self):
        """Confirma antes de excluir um paciente"""
        # Verificar se há paciente selecionado
        if not self.paciente_selecionado or not self.avaliacao_id:
            messagebox.showwarning("Aviso", "Selecione um paciente para excluir.")
            return
        
        nome_paciente = self.paciente_selecionado.get('Nombre Completo', 'Paciente')
        
        # Confirmar exclusão
        resposta = messagebox.askyesno(
            "Excluir Paciente", 
            f"Deseja realmente excluir o paciente {nome_paciente} e todos os seus dados?\n\nEsta ação não pode ser desfeita.",
            icon='warning'
        )
        
        if resposta:
            try:
                # Excluir do banco de dados
                sucesso = self.db.excluir_avaliacao(self.avaliacao_id)
                
                if sucesso:
                    messagebox.showinfo("Sucesso", f"Paciente {nome_paciente} excluído com sucesso.")
                    
                    # Resetar seleção
                    self.paciente_selecionado = None
                    self.avaliacao_id = None
                    
                    # Limpar detalhes
                    for widget in self.frame_conteudo_detalhes.winfo_children():
                        widget.destroy()
                    
                    # Desabilitar botões
                    self.btn_imprimir.config(state=tk.DISABLED)
                    self.btn_nova_avaliacao.config(state=tk.DISABLED)
                    self.btn_editar.config(state=tk.DISABLED)
                    
                    # Restaurar mensagem inicial
                    self.label_selecione = tk.Label(
                        self.frame_conteudo_detalhes, 
                        text="Selecione um paciente para visualizar seus dados", 
                        bg=self.cores["secao_bg"],
                        fg=self.cores["texto"],
                        font=FONTES["subtitulo_secao"]
                    )
                    self.label_selecione.pack(padx=20, pady=50)
                    
                    # Atualizar lista
                    self.carregar_pacientes()
                    
                    # Restaurar título
                    self.titulo_detalhes.config(text="DETALHES DO PACIENTE")
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o paciente.")
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao excluir o paciente: {str(e)}")
    
    def imprimir_avaliacao(self):
        """Prepara a avaliação para impressão"""
        if not self.paciente_selecionado or not self.avaliacao_id:
            messagebox.showwarning("Aviso", "Selecione um paciente para imprimir sua avaliação.")
            return
        
        try:
            # Exportar para JSON (pode ser modificado para gerar PDF ou outro formato para impressão)
            diretorio_exportacao = "exportacoes"
            if not os.path.exists(diretorio_exportacao):
                os.makedirs(diretorio_exportacao)
            
            nome_paciente = self.paciente_selecionado.get('Nombre Completo', '').replace(' ', '_').lower()
            if not nome_paciente:
                nome_paciente = 'paciente'
            
            data_atual = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"{nome_paciente}_{data_atual}.json"
            caminho_arquivo = os.path.join(diretorio_exportacao, nome_arquivo)
            
            # Exportar usando o método do banco de dados
            sucesso = self.db.exportar_avaliacao_json(self.avaliacao_id, caminho_arquivo)
            
            if sucesso:
                messagebox.showinfo(
                    "Exportar", 
                    f"Avaliação exportada com sucesso para impressão.\n\nArquivo: {nome_arquivo}\nDiretório: {os.path.abspath(diretorio_exportacao)}"
                )
            else:
                messagebox.showerror("Erro", "Não foi possível exportar a avaliação.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao preparar a impressão: {str(e)}")
    
    def abrir_nova_avaliacao(self):
        """Abre uma nova avaliação para o paciente selecionado"""
        # Esta função deve ser implementada para abrir o formulário de avaliação
        # com os dados básicos do paciente já preenchidos
        if not self.paciente_selecionado:
            messagebox.showwarning("Aviso", "Selecione um paciente para criar uma nova avaliação.")
            return
        
        messagebox.showinfo(
            "Nova Avaliação", 
            "Esta funcionalidade permitirá criar uma nova avaliação para o paciente selecionado.\n\nImplementação pendente: Deve abrir o formulário com os dados básicos do paciente preenchidos."
        )
    
    def editar_avaliacao(self):
        """Edita a avaliação atual do paciente selecionado"""
        # Esta função deve ser implementada para abrir o formulário de avaliação
        # com todos os dados da avaliação atual para edição
        if not self.paciente_selecionado or not self.avaliacao_id:
            messagebox.showwarning("Aviso", "Selecione um paciente para editar sua avaliação.")
            return
        
        messagebox.showinfo(
            "Editar Avaliação", 
            "Esta funcionalidade permitirá editar a avaliação atual do paciente.\n\nImplementação pendente: Deve abrir o formulário com todos os dados da avaliação preenchidos."
        )


# Função para adicionar a aba ao notebook principal
def adicionar_aba_clientes(notebook):
    """
    Adiciona a aba de clientes ao notebook principal
    
    Args:
        notebook: Notebook (ttk.Notebook) onde a aba será adicionada
        
    Returns:
        AbaClientes: Instância da aba criada
    """
    return AbaClientes(notebook)


# Para testes diretos deste módulo
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sistema de Avaliação Fisioterapêutica - Aba de Clientes")
    
    # Abordagem para tela cheia
    largura = root.winfo_screenwidth()
    altura = root.winfo_screenheight()
    root.geometry(f"{largura}x{altura}+0+0")
    
    try:
        root.state('zoomed')  # Funciona no Windows
    except:
        pass  # Ignora se não funcionar
    
    # Configurar cores da interface
    root.config(bg=CORES["fundo"])
    
    # Frame principal com margem
    frame_principal = tk.Frame(root, bg=CORES["fundo"], padx=10, pady=10)
    frame_principal.pack(expand=True, fill="both")
    
    # Notebook principal
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
    
    # Adicionar aba de clientes
    aba_clientes = AbaClientes(notebook)
    
    # Iniciar loop principal
    root.mainloop()