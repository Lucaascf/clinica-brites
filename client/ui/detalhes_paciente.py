import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import threading

class DetalhesPacienteWindow:
    """
    Janela separada (Toplevel) para mostrar os detalhes do paciente de forma organizada.
    """
    def __init__(self, parent, dados, cores, fontes):
        """Inicializa a janela de detalhes do paciente"""
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title(f"Detalhes - {dados.get('Nombre Completo', 'Paciente')}")

        self._thread_running = True
        
        # Configurações
        self.cores = cores
        self.fontes = fontes
        
        # Armazenar apenas dados essenciais, não todo o dicionário
        self.dados = {k: dados[k] for k in dados if dados[k]}
        
        # Configurar tamanho da janela
        largura = min(1000, parent.winfo_screenwidth() - 100)
        altura = min(700, parent.winfo_screenheight() - 100)
        
        # Centralizar a janela
        pos_x = parent.winfo_rootx() + (parent.winfo_width() - largura) // 2
        pos_y = parent.winfo_rooty() + (parent.winfo_height() - altura) // 2
        
        self.window.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        self.window.minsize(800, 600)
        
        # Remover grab_set() e manter apenas focus_set()
        self.window.focus_set()
        
        # Criar sistema de rolagem
        self.criar_sistema_rolagem()
        
        # Preencher com os dados do paciente em uma thread
        threading.Thread(target=self.exibir_dados_paciente, daemon=True).start()
        
        # Botões de ação
        self.criar_botoes_acao()
        
        # Adicionar método para desvinculação de eventos
        self.window.protocol("WM_DELETE_WINDOW", self.fechar)
    
    def criar_sistema_rolagem(self):
        """Cria o sistema de rolagem para a janela"""
        # Frame principal para o conteúdo
        self.frame_principal = tk.Frame(self.window, bg=self.cores["fundo"])
        self.frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para rolagem
        self.canvas = tk.Canvas(self.frame_principal, bg=self.cores["fundo"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.frame_principal, orient="vertical", command=self.canvas.yview)
        
        # Configurar canvas para usar scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para conteúdo
        self.frame_conteudo = tk.Frame(self.canvas, bg=self.cores["secao_bg"])
        self.frame_conteudo.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Criar janela no canvas para o conteúdo
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame_conteudo, anchor="nw", width=self.canvas.winfo_width())
        
        # Ajustar largura do conteúdo quando o canvas for redimensionado
        self.canvas.bind('<Configure>', self._ao_configurar_canvas)
        
        # Configurar eventos de rolagem específicos do canvas e da janela
        self._configurar_eventos_rolagem()
        
        # Adicionar método para limpar eventos quando a janela for fechada
        self.window.protocol("WM_DELETE_WINDOW", self.fechar)
    
    def _ao_configurar_canvas(self, evento):
        """Ajusta a largura da janela de conteúdo quando o canvas é redimensionado"""
        self.canvas.itemconfig(self.canvas_window, width=evento.width)
    
    def _formatar_data(self, data_str):
        """Formata a data para exibição"""
        try:
            # Converter string para datetime
            if '-' in data_str:  # Formato SQL: 2025-03-30 17:56:02
                data = datetime.datetime.strptime(data_str.split(' ')[0], '%Y-%m-%d')
            elif '/' in data_str:  # Formato brasileiro: 30/03/2025
                data = datetime.datetime.strptime(data_str, '%d/%m/%Y')
            else:
                return data_str
            
            # Retornar formato brasileiro
            return data.strftime('%d/%m/%Y')
        except:
            return data_str
    
    def exibir_dados_paciente(self):
        """"Exibe os dados do paciente de forma organizada"""
        # Verificar a flag e se a janela ainda existe
        try:
            if not self._thread_running or not self.window.winfo_exists():
                return
        except:
            return
        
        # Mapeamento de campos para nomes mais amigáveis em português
        mapeamento_campos = {
            "Nombre Completo": "Nome Completo",
            "Edad": "Idade",
            "Genero": "Gênero",
            "Contacto": "Contato",
            "Fecha Nasc.": "Data de Nascimento",
            "Área de consulta": "Área de Consulta",
            "Alergias": "Alergias",
            "data_avaliacao": "Data da Avaliação",
            "Motivo de consulta": "Motivo da Consulta",
            "Antecedentes": "Antecedentes",
            "Efermedad actual": "Doença Atual",
            "Cirurgías previas": "Cirurgias Prévias",
            "Medicamentos actuales": "Medicamentos Atuais",
            "PA": "Pressão Arterial",
            "Pulso": "Pulso",
            "Talla": "Altura",
            "Peso": "Peso",
            "T": "Temperatura",
            "FR": "Frequência Respiratória",
            "Sat.O2": "Saturação de O2",
            "IDx": "Diagnóstico",
            "Conducta": "Conduta",
            "Postura": "Postura",
            "Simetría corporal": "Simetria Corporal",
            "Deformidades aparentes": "Deformidades Aparentes",
            "Puntos dolorosos": "Pontos Dolorosos",
            "Tensión muscular": "Tensão Muscular",
            "Curvas Fisiológicas": "Curvas Fisiológicas",
            "Presencia de Escoliosis": "Presença de Escoliose",
            "Cifosis o Lordosis": "Cifose ou Lordose",
            "Movimiento Activo": "Movimento Ativo",
            "Movimiento Pasivo": "Movimento Passivo",
            "Evaluación de articulaciones": "Avaliação de Articulações",
            "Fuerza Muscular": "Força Muscular",
            "Evaluación de grupos musculares": "Avaliação de Grupos Musculares",
            "Reflejos": "Reflexos",
            "Coordinación motora": "Coordenação Motora",
            "Equilibrio": "Equilíbrio",
            "Capacidad para realizar actividades diarias": "Capacidade para Atividades Diárias",
            "Limitaciones y dificultades": "Limitações e Dificuldades",
            "Ejercicios con dedos": "Exercícios com Dedos",
            "Precisión en movimientos": "Precisão nos Movimentos",
            "Marcha": "Marcha",
            "Equilibrio Dinámico": "Equilíbrio Dinâmico",
            "Pruebas ortopédicas": "Testes Ortopédicos",
            "Pruebas neurológicas": "Testes Neurológicos",
            "Pruebas de estabilidad": "Testes de Estabilidade",
            "escala_eva": "Escala de Dor (EVA)",
            "observaciones_dolor": "Observações sobre a Dor",
            "Resumen del problema": "Resumo do Problema",
            "Objetivos del tratamiento": "Objetivos do Tratamento",
            "sesiones_semana": "Sessões por Semana",
            "duracion_sesion": "Duração da Sessão",
            "obs_frecuencia": "Observações de Frequência",
            "Ejercicios recomendados": "Exercícios Recomendados",
            "programacion_seguimiento": "Programação de Seguimento",
            "fecha_evaluacion": "Data da Próxima Avaliação",
            "criterio_revision": "Critério de Revisão",
            "criterios_adicionales": "Critérios Adicionais"
        }
        
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
                    {"titulo": "Diagnóstico e Conduta", 
                    "campos": ["IDx", "Conducta"]},
                    {"titulo": "Inspeção e Palpação", 
                    "campos": ["Postura", "Simetría corporal", "Deformidades aparentes", 
                            "Puntos dolorosos", "Tensión muscular"]},
                    {"titulo": "Coluna Vertebral", 
                    "campos": ["Curvas Fisiológicas", "Presencia de Escoliosis", "Cifosis o Lordosis"]},
                    {"titulo": "Mobilidade Articular", 
                    "campos": ["Movimiento Activo", "Movimiento Pasivo", "Evaluación de articulaciones"]},
                    {"titulo": "Força e Avaliação Neuromuscular", 
                    "campos": ["Fuerza Muscular", "Evaluación de grupos musculares", "Reflejos", 
                            "Coordinación motora", "Equilibrio"]},
                    {"titulo": "Avaliação Funcional", 
                    "campos": ["Capacidad para realizar actividades diarias", "Limitaciones y dificultades"]}
                ]
            },
            {
                "titulo": "COORDENAÇÃO",
                "campos": ["Ejercicios con dedos", "Precisión en movimientos", "Marcha", "Equilibrio Dinámico"]
            },
            {
                "titulo": "TESTES ESPECIAIS",
                "campos": ["Pruebas ortopédicas", "Pruebas neurológicas", "Pruebas de estabilidad"]
            },
            {
                "titulo": "AVALIAÇÃO DA DOR",
                "campos": ["escala_eva", "observaciones_dolor"]
            },
            {
                "titulo": "DIAGNÓSTICO E TRATAMENTO",
                "campos": ["Resumen del problema", "Objetivos del tratamiento", 
                        "sesiones_semana", "duracion_sesion", "obs_frecuencia", 
                        "Ejercicios recomendados"]
            },
            {
                "titulo": "SEGUIMENTO E REAVALIAÇÃO",
                "campos": ["programacion_seguimiento", "fecha_evaluacion", 
                        "criterio_revision", "criterios_adicionales"]
            }
        ]
        
        # Definir melhor espaçamento entre seções
        padding_secao = 12
        
        # Percorrer cada seção e criar os componentes visuais
        for secao in secoes:
            # Verificar se há algum dado para esta seção
            tem_dados = False
            
            # Se a seção tem subsecoes, verificar em cada uma
            if 'subsecoes' in secao:
                for subsecao in secao['subsecoes']:
                    if any(self.dados.get(campo) for campo in subsecao['campos']):
                        tem_dados = True
                        break
            else:
                # Verificar nos campos da seção
                if any(self.dados.get(campo) for campo in secao['campos']):
                    tem_dados = True
            
            # Se não tiver dados relevantes, pular esta seção
            if not tem_dados:
                continue
            
            # Criar o frame da seção
            frame_secao = tk.Frame(
                self.frame_conteudo, 
                bg=self.cores["secao_bg"], 
                bd=1, 
                relief=tk.RIDGE,
                borderwidth=2
            )
            frame_secao.pack(fill=tk.X, expand=False, padx=10, pady=8)
            
            # Título da seção
            frame_titulo = tk.Frame(frame_secao, bg=self.cores["titulo_bg"])
            frame_titulo.pack(fill=tk.X)
            
            titulo = tk.Label(
                frame_titulo, 
                text=secao["titulo"], 
                bg=self.cores["titulo_bg"],
                fg=self.cores["texto_destaque"],
                font=self.fontes["subtitulo_secao"],
                padx=15,
                pady=10
            )
            titulo.pack(side=tk.LEFT, padx=5)
            
            # Frame para os dados da seção
            frame_dados = tk.Frame(frame_secao, bg=self.cores["secao_bg"], 
                                padx=padding_secao, pady=padding_secao)
            frame_dados.pack(fill=tk.X)
            
            # Se tiver subsecoes, criar cada uma
            if 'subsecoes' in secao:
                for i, subsecao in enumerate(secao['subsecoes']):
                    # Verificar se há dados nesta subseção
                    if not any(self.dados.get(campo) for campo in subsecao['campos']):
                        continue
                    
                    # Adicionar um separador entre subseções (exceto na primeira)
                    if i > 0:
                        separador = tk.Frame(frame_dados, height=2, bg=self.cores["separador"])
                        separador.pack(fill=tk.X, pady=10, padx=15)
                    
                    # Título da subseção
                    label_subsecao = tk.Label(
                        frame_dados, 
                        text=subsecao["titulo"].upper(), 
                        bg=self.cores["secao_bg"],
                        fg=self.cores["primaria"],
                        font=self.fontes["subtitulo_secao"]
                    )
                    label_subsecao.pack(anchor="w", padx=15, pady=8)
                    
                    # Grid para os campos desta subseção
                    grid_campos = tk.Frame(frame_dados, bg=self.cores["secao_bg"])
                    grid_campos.pack(fill=tk.X, padx=20, pady=5)
                    
                    # Configurar colunas do grid
                    grid_campos.columnconfigure(0, weight=0, minsize=220)  # Coluna para labels - maior largura
                    grid_campos.columnconfigure(1, weight=1)              # Coluna para valores
                    
                    # Adicionar os campos
                    for j, campo in enumerate(subsecao['campos']):
                        if self.dados.get(campo):
                            # Usar o nome traduzido se disponível
                            nome_campo = mapeamento_campos.get(campo, campo)
                            
                            # Label do campo
                            label_campo = tk.Label(
                                grid_campos, 
                                text=f"{nome_campo}:", 
                                bg=self.cores["secao_bg"],
                                fg=self.cores["texto_rotulo"],
                                font=self.fontes["campo_destaque"]
                            )
                            label_campo.grid(row=j, column=0, padx=15, pady=8, sticky="nw")
                            
                            # Valor do campo (com tratamento especial para listas)
                            valor = self.dados.get(campo)
                            if isinstance(valor, list):
                                valor = ", ".join(valor)
                            
                            # Para todos os campos, usar Text widget para exibir o valor completo com quebra de linha
                            text_valor = tk.Text(
                                grid_campos,
                                height=min(10, max(1, len(str(valor)) // 70 + 1)),  # Altura dinâmica baseada no conteúdo
                                width=60,  # Largura fixa para o widget
                                wrap=tk.WORD,  # Quebra de linha por palavra
                                bg=self.cores["secao_bg"],
                                fg=self.cores["texto"],
                                font=self.fontes["campo"],
                                relief=tk.FLAT,
                                borderwidth=0,
                                highlightthickness=0
                            )
                            text_valor.insert("1.0", str(valor))
                            text_valor.config(state=tk.DISABLED)  # Somente leitura
                            text_valor.grid(row=j, column=1, padx=15, pady=8, sticky="nw")
            else:
                # Grid para os campos desta seção
                grid_campos = tk.Frame(frame_dados, bg=self.cores["secao_bg"])
                grid_campos.pack(fill=tk.X, padx=15)
                
                # Configurar colunas do grid
                grid_campos.columnconfigure(0, weight=0, minsize=220)  # Coluna para labels - maior largura
                grid_campos.columnconfigure(1, weight=1)              # Coluna para valores
                
                # Tratar campos da escala EVA de forma especial
                if secao["titulo"] == "AVALIAÇÃO DA DOR" and self.dados.get("escala_eva") is not None:
                    # Escala EVA com visualização especial
                    valor_eva = self.dados.get("escala_eva", 0)
                    
                    # Label da escala
                    label_eva = tk.Label(
                        grid_campos, 
                        text="Escala de Dor (EVA):", 
                        bg=self.cores["secao_bg"],
                        fg=self.cores["texto_rotulo"],
                        font=self.fontes["campo_destaque"]
                    )
                    label_eva.grid(row=0, column=0, padx=15, pady=10, sticky="nw")
                    
                    # Valor da escala com cor dependendo da intensidade
                    cor_intensidade = "#4CAF50" if valor_eva < 4 else "#FF9800" if valor_eva < 7 else "#F44336"
                    
                    label_valor = tk.Label(
                        grid_campos, 
                        text=f"{valor_eva}/10", 
                        bg=self.cores["secao_bg"],
                        fg=cor_intensidade,
                        font=self.fontes["subtitulo_secao"]
                    )
                    label_valor.grid(row=0, column=1, padx=15, pady=10, sticky="nw")
                    
                    # Exibir barra visual da dor
                    frame_barra = tk.Frame(grid_campos, bg=self.cores["secao_bg"], height=30)
                    frame_barra.grid(row=1, column=0, columnspan=2, padx=30, pady=10, sticky="ew")
                    
                    # Desenhar barra de progresso com largura relativa à coluna
                    largura_total = 400
                    
                    # Fundo da barra com borda para mais contraste
                    barra_background = tk.Frame(
                        frame_barra, 
                        bg="#F0F0F0", 
                        height=25, 
                        width=largura_total,
                        bd=1,
                        relief=tk.SUNKEN
                    )
                    barra_background.pack(fill=tk.X, padx=20)
                    
                    # Calcular largura preenchida
                    largura_preenchida = int(largura_total * (valor_eva / 10))
                    
                    # Barra colorida
                    barra_valor = tk.Frame(
                        barra_background, 
                        bg=cor_intensidade, 
                        height=25, 
                        width=largura_preenchida
                    )
                    barra_valor.place(x=0, y=0)
                    
                    # Exibir observações sobre a dor
                    if self.dados.get('observaciones_dolor', ''):
                        label_obs = tk.Label(
                            grid_campos, 
                            text="Observações sobre a dor:", 
                            bg=self.cores["secao_bg"],
                            fg=self.cores["texto_rotulo"],
                            font=self.fontes["campo_destaque"]
                        )
                        label_obs.grid(row=2, column=0, padx=15, pady=(20, 5), sticky="nw")
                        
                        # Usar Text widget para exibir o valor completo
                        texto_obs = self.dados.get('observaciones_dolor', '')
                        text_obs = tk.Text(
                            grid_campos,
                            height=min(10, max(1, len(texto_obs) // 70 + 1)),  # Altura dinâmica baseada no conteúdo
                            width=60,  # Largura fixa para o widget
                            wrap=tk.WORD,  # Quebra de linha por palavra
                            bg=self.cores["secao_bg"],
                            fg=self.cores["texto"],
                            font=self.fontes["campo"],
                            relief=tk.FLAT, 
                            borderwidth=0,
                            highlightthickness=0
                        )
                        text_obs.insert("1.0", texto_obs)
                        text_obs.config(state=tk.DISABLED)  # Somente leitura
                        text_obs.grid(row=2, column=1, padx=15, pady=(20, 5), sticky="nw")
                else:
                    # Para todas as outras seções, mostrar campos usando Text widget
                    row_count = 0
                    
                    for campo in secao['campos']:
                        if self.dados.get(campo) is not None and self.dados.get(campo) != '':
                            # Para campos de frequência do tratamento
                            if campo == 'sesiones_semana' and self.dados.get('duracion_sesion'):
                                nome_campo = "Frequência do Tratamento"
                                
                                # Label do campo
                                label_campo = tk.Label(
                                    grid_campos, 
                                    text=f"{nome_campo}:", 
                                    bg=self.cores["secao_bg"],
                                    fg=self.cores["texto_rotulo"],
                                    font=self.fontes["campo_destaque"]
                                )
                                label_campo.grid(row=row_count, column=0, padx=15, pady=8, sticky="nw")
                                
                                # Valor formatado
                                valor_campo = tk.Label(
                                    grid_campos, 
                                    text=f"{self.dados.get('sesiones_semana')} vez(es) por semana, {self.dados.get('duracion_sesion')} por sessão", 
                                    bg=self.cores["secao_bg"],
                                    fg=self.cores["texto"],
                                    font=self.fontes["campo"],
                                    wraplength=450,
                                    justify=tk.LEFT
                                )
                                valor_campo.grid(row=row_count, column=1, padx=15, pady=8, sticky="nw")
                                row_count += 1
                                
                            # Para campos normais
                            elif campo != 'duracion_sesion':  # Evitando duplicação do campo duração
                                # Usar o nome traduzido se disponível
                                nome_campo = mapeamento_campos.get(campo, campo)
                                
                                # Label do campo
                                label_campo = tk.Label(
                                    grid_campos, 
                                    text=f"{nome_campo}:", 
                                    bg=self.cores["secao_bg"],
                                    fg=self.cores["texto_rotulo"],
                                    font=self.fontes["campo_destaque"]
                                )
                                label_campo.grid(row=row_count, column=0, padx=15, pady=8, sticky="nw")
                                
                                # Valor do campo (com tratamento especial para listas)
                                valor = self.dados.get(campo)
                                if isinstance(valor, list):
                                    valor = ", ".join(valor)
                                
                                # Formatação especial para datas
                                if campo in ['data_avaliacao', 'fecha_evaluacion'] and valor:
                                    valor = self._formatar_data(valor)
                                
                                # Lista de campos especiais que devem ser tratados normalmente
                                campos_curtos = [
                                    'Nombre Completo', 'Edad', 'Genero', 'Contacto', 'Fecha Nasc.', 
                                    'Área de consulta', 'data_cadastro', 'data_avaliacao', 'fisioterapeuta',
                                    'PA', 'Pulso', 'Talla', 'Peso', 'T', 'FR', 'Sat.O2', 'IDx',
                                    'escala_eva', 'sesiones_semana', 'duracion_sesion', 
                                    'programacion_seguimiento', 'fecha_evaluacion'
                                ]
                                
                                # Para qualquer campo, mesmo curto, usar Text widget para garantir exibição completa
                                if valor:
                                    texto_str = str(valor)
                                    # Calcular altura baseada no conteúdo
                                    num_linhas = min(15, max(1, len(texto_str) // 70 + texto_str.count('\n') + 1))
                                    
                                    text_display = tk.Text(
                                        grid_campos,
                                        height=num_linhas,
                                        width=60,
                                        wrap=tk.WORD,
                                        bg=self.cores["secao_bg"],
                                        fg=self.cores["texto"],
                                        font=self.fontes["campo"],
                                        relief=tk.FLAT,
                                        borderwidth=0,
                                        highlightthickness=0
                                    )
                                    text_display.insert("1.0", texto_str)
                                    text_display.config(state=tk.DISABLED)  # Somente leitura
                                    text_display.grid(row=row_count, column=1, padx=15, pady=8, sticky="nw")
                                
                                row_count += 1
                                
    def criar_botoes_acao(self):
        """Cria os botões de ação na parte inferior da janela"""
        frame_botoes = tk.Frame(self.window, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_botoes.pack(fill=tk.X, side=tk.BOTTOM)
        
        btn_imprimir = tk.Button(
            frame_botoes, 
            text="Imprimir Avaliação", 
            command=self.imprimir_avaliacao,
            bg=self.cores["secundaria"],
            fg=self.cores["texto_destaque"],
            font=self.fontes["botao"],
            padx=10,
            pady=5
        )
        btn_imprimir.pack(side=tk.LEFT, padx=5, pady=5)
        
        btn_fechar = tk.Button(
            frame_botoes, 
            text="Fechar", 
            command=self.fechar,
            bg=self.cores["aviso"],
            fg=self.cores["texto_destaque"],
            font=self.fontes["botao"],
            padx=10,
            pady=5
        )
        btn_fechar.pack(side=tk.RIGHT, padx=5, pady=5)
        
        btn_editar = tk.Button(
            frame_botoes, 
            text="Editar Avaliação", 
            command=self.editar_avaliacao,
            bg=self.cores["primaria"],
            fg=self.cores["texto_destaque"],
            font=self.fontes["botao"],
            padx=10,
            pady=5
        )
        btn_editar.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def imprimir_avaliacao(self):
        """Exporta a avaliação para impressão (placeholder)"""
        messagebox.showinfo("Imprimir", "Funcionalidade de impressão será implementada em breve.")
    
    def editar_avaliacao(self):
        """Abre a interface de edição (placeholder)"""
        messagebox.showinfo("Editar", "Funcionalidade de edição será implementada em breve.")

    def _on_mousewheel(self, event):
        """Manipulador de evento para rolagem do mouse no Windows"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_button4(self, event):
        """Manipulador de evento para rolagem do mouse para cima no Linux"""
        self.canvas.yview_scroll(-1, "units")

    def _on_button5(self, event):
        """Manipulador de evento para rolagem do mouse para baixo no Linux"""
        self.canvas.yview_scroll(1, "units")

    def _configurar_eventos_rolagem(self):
        """Configura os eventos de rolagem para funcionar no Linux e Windows"""
        # Rolagem para Windows/Mac - evento MouseWheel
        self.window.bind("<MouseWheel>", self._on_mousewheel_windows)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel_windows)
        
        # Rolagem para Linux - eventos Button-4 e Button-5
        self.window.bind("<Button-4>", self._on_mousewheel_linux_up)
        self.window.bind("<Button-5>", self._on_mousewheel_linux_down)
        self.canvas.bind("<Button-4>", self._on_mousewheel_linux_up)
        self.canvas.bind("<Button-5>", self._on_mousewheel_linux_down)

    def _on_mousewheel_windows(self, event):
        """Manipulador para evento de rolagem no Windows/Mac"""
        # No Windows, event.delta é positivo ao rolar para cima e negativo ao rolar para baixo
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # Previne propagação do evento
        return "break"

    def _on_mousewheel_linux_up(self, event):
        """Manipulador para evento de rolagem para cima no Linux"""
        self.canvas.yview_scroll(-1, "units")
        # Previne propagação do evento
        return "break"

    def _on_mousewheel_linux_down(self, event):
        """Manipulador para evento de rolagem para baixo no Linux"""
        self.canvas.yview_scroll(1, "units")
        # Previne propagação do evento
        return "break"

    def fechar(self):
        """Fecha a janela e limpa adequadamente"""
        # Indicar à thread que deve parar
        self._thread_running = False 
        
        # Desvincular eventos de rolagem
        try:
            self.window.unbind("<MouseWheel>")
            self.window.unbind("<Button-4>")
            self.window.unbind("<Button-5>")
            self.canvas.unbind("<MouseWheel>")
            self.canvas.unbind("<Button-4>")
            self.canvas.unbind("<Button-5>")
            
            # Limpar referências a widgets
            self.canvas = None
            self.frame_conteudo = None
            self.scrollbar = None
            
            # Limpar dados
            self.dados = None
        except:
            pass
        
        # Fechar a janela
        try:
            self.window.destroy()
        except:
            pass