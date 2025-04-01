import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import datetime
import threading
import queue  # Adicione esta importação
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import sys
import os
import time
# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import concurrent.futures

# Importar o banco de dados
from server.database import BancoDadosFisioterapia

# Importar as configurações
from config import CORES, FONTES, TAMANHOS

from client.ui.detalhes_paciente import DetalhesPacienteWindow
from client.styles.treeview_style import configurar_estilo_treeview, alternar_cores_linhas


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
        
        # Otimizar o banco de dados com índices
        self.otimizar_banco_dados()
        
        # Configurações
        self.cores = CORES

        # Criar referência para janela de detalhes ativa
        self.janela_detalhes = None
        # Função para atualização de cores das linhas
        self.atualizar_cores_linhas = None
        
        # Estado atual
        self.paciente_selecionado = None
        self.avaliacao_id = None
        
        # Flags para otimização
        self.ultima_atualizacao = 0
        self.pacientes_carregados = False
        self._scroll_timer = None
        
        # Fila para comunicação entre threads
        self.queue = queue.Queue()
        self.executando = True  # Flag para controlar loops e threads
        
        # Adicionar pool de threads
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        
        # Configurar o layout da aba
        self.configurar_aba()
        
        # Iniciar o verificador de fila
        self.verificar_fila()
        
        # Carregar dados iniciais
        self.carregar_pacientes()
        
        # Configurar evento para quando a aba for destruída
        self.frame.bind("<Destroy>", self._ao_destruir)

    def verificar_fila(self):
        """Verifica periodicamente a fila de tarefas"""
        if not self.executando:
            return
        
        try:
            # Verificar se há tarefas na fila (non-blocking)
            tarefa, args = self.queue.get(block=False)
            # Executar a tarefa
            tarefa(*args)
        except queue.Empty:
            # Se não houver tarefas, verificar novamente depois
            pass
        
        # Reagendar a verificação
        if self.executando:
            self.frame.after(100, self.verificar_fila)
    
    def otimizar_banco_dados(self):
        """Adiciona índices para melhorar o desempenho do banco de dados"""
        try:
            # Verifica se o método existe no objeto db
            if hasattr(self.db, "otimizar_banco_dados"):
                self.db.otimizar_banco_dados()
            else:
                conn, cursor = self.db._conectar()
                
                # Adicionar índices para busca por nome e data
                cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_pacientes_nome ON pacientes (nome);
                ''')
                
                cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_avaliacoes_data ON avaliacoes (data_avaliacao);
                ''')
                
                cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_avaliacoes_paciente ON avaliacoes (paciente_id);
                ''')
                
                conn.commit()
                conn.close()
            
            return True
        except Exception as e:
            print(f"Erro ao otimizar banco de dados: {e}")
            return False
    
    def configurar_aba(self):
        """Configura o layout da aba de clientes com apenas a lista de pacientes"""
        # Frame principal com uma única coluna
        self.frame_principal = tk.Frame(self.frame, bg=self.cores["fundo"])
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # IMPORTANTE: Configurar o frame principal para expandir verticalmente
        self.frame_principal.rowconfigure(0, weight=1)

        # Configurar coluna do frame principal - AGORA UMA ÚNICA COLUNA
        self.frame_principal.columnconfigure(0, weight=1)  # Lista de pacientes - ocupa todo o espaço
        
        # ======= LISTA DE PACIENTES =======
        self.frame_lista = tk.Frame(self.frame_principal, bg=self.cores["secao_bg"], bd=1, relief=tk.SOLID)
        self.frame_lista.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
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
        estilo = configurar_estilo_treeview(self.cores, FONTES)        

        # Criar scrollbar
        scrollbar = tk.Scrollbar(frame_treeview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Criar Treeview (tabela)
        self.treeview = ttk.Treeview(
            frame_treeview,
            columns=('id', 'nome', 'idade', 'genero', 'data', 'proxima_avaliacao'),
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            height=15
        )
        scrollbar.config(command=self.treeview.yview)

        # Configurar colunas
        self.treeview.heading('id', text='ID')
        self.treeview.heading('nome', text='Nome')
        self.treeview.heading('idade', text='Idade')
        self.treeview.heading('genero', text='Gênero')
        self.treeview.heading('data', text='Data Cadastro')
        self.treeview.heading('proxima_avaliacao', text='Próxima Avaliação')

        # Ajustar largura das colunas
        self.treeview.column('id', width=50, minwidth=50)
        self.treeview.column('nome', width=180, minwidth=150)
        self.treeview.column('idade', width=50, minwidth=50)
        self.treeview.column('genero', width=60, minwidth=50)
        self.treeview.column('data', width=90, minwidth=80)
        self.treeview.column('proxima_avaliacao', width=110, minwidth=100)
        
        # Empacotar Treeview
        self.treeview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.atualizar_cores_linhas = alternar_cores_linhas(self.treeview)
        
        # Vincular evento de seleção
        self.treeview.bind('<<TreeviewSelect>>', self.ao_selecionar_paciente)

        # Adicionar evento de duplo clique
        self.treeview.bind('<Double-1>', self.ao_clicar_duplo)
        
        # Vincular evento para detecção de rolagem
        self.treeview.bind("<Motion>", self._verificar_scroll_treeview)

        # Adicionar variáveis de controle para paginação
        self._carregando_mais_itens = False
        self._pagina_atual = 1

        # Botões de ação para a lista
        frame_botoes_lista = tk.Frame(self.frame_lista, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_botoes_lista.pack(fill=tk.X)
        
        btn_atualizar = tk.Button(
            frame_botoes_lista, 
            text="Atualizar Lista", 
            command=lambda: self.carregar_pacientes(forcar=True),
            bg=self.cores["secundaria"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5
        )
        btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Botão para ver detalhes
        btn_detalhes = tk.Button(
            frame_botoes_lista, 
            text="Ver Detalhes", 
            command=self.abrir_detalhes_paciente,
            bg=self.cores["primaria"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5
        )
        btn_detalhes.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Botão para nova avaliação
        btn_nova_avaliacao = tk.Button(
            frame_botoes_lista, 
            text="Nova Avaliação", 
            command=self.abrir_nova_avaliacao,
            bg=self.cores["sucesso"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5
        )
        btn_nova_avaliacao.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Botão para editar avaliação
        btn_editar = tk.Button(
            frame_botoes_lista, 
            text="Editar Avaliação", 
            command=self.editar_avaliacao,
            bg=self.cores["aviso"],
            fg=self.cores["texto_destaque"],
            font=FONTES["botao"],
            padx=10,
            pady=5
        )
        btn_editar.pack(side=tk.RIGHT, padx=5, pady=5)
        
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

    def carregar_pacientes(self, forcar=False):
        """Carrega a lista de pacientes do banco de dados com otimização"""
        # Verificar se já carregamos recentemente (dentro de 5 segundos)
        tempo_atual = time.time()
        
        if not forcar and self.pacientes_carregados and (tempo_atual - self.ultima_atualizacao < 5):
            # Pular o recarregamento se já carregamos recentemente
            return
        
        # Limpar Treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Exibir indicador de carregamento
        self.treeview.insert('', 'end', values=('', 'Carregando...', '', '', '', ''))
        
        # Adicionar barra de progresso
        progresso = ttk.Progressbar(self.frame_lista, mode='indeterminate')
        progresso.pack(fill=tk.X, padx=5, pady=5)
        progresso.start(10)
        
        self.treeview.update()
        
        # Usar thread para carregar dados
        thread = threading.Thread(
            target=lambda: self._thread_carregar_pacientes_com_progresso(progresso, limite=20), 
            daemon=True
        )
        thread.start()

    def _thread_carregar_pacientes_com_progresso(self, barra_progresso, limite=20):
        """Thread otimizada para carregar dados com menos registros iniciais"""
        try:
            # Criar instância local do banco
            db_thread = BancoDadosFisioterapia(self.db.nome_db)
            avaliacoes = db_thread.listar_avaliacoes(limite=limite)
            
            # Liberar recursos do banco IMEDIATAMENTE após uso
            db_thread.fechar_conexao()
            
            if self.executando:
                self.queue.put((self._atualizar_lista_pacientes, [avaliacoes]))
                self.queue.put((self._remover_barra_progresso, [barra_progresso]))
        except Exception as e:
            print(f"Erro ao carregar pacientes: {e}")
            if self.executando:
                self.queue.put((messagebox.showerror, ["Erro", f"Erro ao carregar pacientes: {e}"]))
                self.queue.put((self._remover_barra_progresso, [barra_progresso]))

    def _remover_barra_progresso(self, barra):
        """Remove a barra de progresso"""
        try:
            barra.stop()
            barra.destroy()
        except:
            pass

    def _thread_carregar_pacientes(self):
        """Realiza o carregamento em uma thread separada"""
        try:
            # Criar nova instância do banco para esta thread
            db_thread = BancoDadosFisioterapia(self.db.nome_db)
            
            # Limitar o número de registros iniciais
            avaliacoes = db_thread.listar_avaliacoes(limite=30)
            
            # Verificar se o aplicativo ainda está executando antes de atualizar a interface
            if not self.executando:
                return
                
            self.queue.put((self._atualizar_lista_pacientes, [avaliacoes]), block=False)
            
        except Exception as e:
            print(f"Erro ao carregar pacientes: {e}")
            if self.executando:
                self.queue.put((messagebox.showerror, ["Erro", f"Erro ao carregar pacientes: {e}"]), block=False)
    
    def _atualizar_lista_pacientes_seguro(self):
        """Versão thread-safe para atualizar a lista de pacientes"""
        if hasattr(self, 'thread_avaliacoes'):
            self._atualizar_lista_pacientes(self.thread_avaliacoes)
            # Limpar referência após uso
            del self.thread_avaliacoes

    def _mostrar_erro_seguro(self, mensagem):
        """Mostra uma mensagem de erro de forma thread-safe"""
        from tkinter import messagebox
        messagebox.showerror("Erro", mensagem)
    
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
    
    def pesquisar_pacientes(self, evento=None):
        """Filtra a lista de pacientes com base no texto de pesquisa"""
        # Obter texto de pesquisa
        texto_pesquisa = self.entry_pesquisa.get().strip().lower()
        
        # Limpar Treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # Exibir indicador de carregamento
        self.treeview.insert('', 'end', values=('', 'Pesquisando...', '', '', '', ''))
        self.treeview.update()
        
        # Usar pool de threads
        self.thread_pool.submit(self._thread_pesquisar_pacientes, texto_pesquisa)
    
    def _thread_pesquisar_pacientes(self, texto_pesquisa):
        """Realiza a pesquisa em uma thread separada"""
        try:
            # Criar nova instância do banco para esta thread
            db_thread = BancoDadosFisioterapia(self.db.nome_db)
            
            if not texto_pesquisa:
                # Se não houver texto de pesquisa, mostrar todos
                avaliacoes = db_thread.listar_avaliacoes(limite=100)
            else:
                # Realizar a pesquisa filtrada
                avaliacoes = db_thread.listar_avaliacoes(filtro=texto_pesquisa)
            
            # Verificamos se a aplicação ainda está em execução antes de atualizar a interface
            if self.frame.winfo_exists():
                # Adicionar à fila para atualizar na thread principal
                self.queue.put((self._atualizar_lista_pacientes, [avaliacoes]))
            
        except Exception as e:
            print(f"Erro ao pesquisar pacientes: {e}")
            if self.frame.winfo_exists():
                self.queue.put((self._mostrar_erro_seguro, [f"Erro ao pesquisar pacientes: {e}"]))
    
    def ao_selecionar_paciente(self, evento=None):
        """Chamado quando um paciente é selecionado na lista"""
        # Obter item selecionado
        selecao = self.treeview.selection()
        if not selecao:
            return
        
        # Obter ID da avaliação
        item = self.treeview.item(selecao[0])
        if not item['values'] or item['values'][0] == '':
            return  # Evitar selecionar item de carregamento
                
        avaliacao_id = item['values'][0]
        
        # Armazenar ID da avaliação selecionada
        self.avaliacao_id = avaliacao_id
        
        # Usar thread para carregar os dados sem travar a interface
        thread = threading.Thread(target=self._carregar_dados_paciente, args=(avaliacao_id,))
        thread.daemon = True
        thread.start()

    def _carregar_dados_paciente(self, avaliacao_id):
        """Carrega os dados do paciente em uma thread separada"""
        # Obter dados completos da avaliação
        dados = self.db.obter_avaliacao(avaliacao_id)
        
        # Verificamos se a aplicação ainda está em execução antes de atualizar a interface
        if self.frame.winfo_exists():
            # Armazenar os dados do paciente para uso posterior
            self.paciente_selecionado = dados

    def _atualizar_lista_pacientes(self, avaliacoes):
        """Atualiza a lista de pacientes na thread principal"""
        # Limpar lista
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
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
        
        # Atualizar flags
        self.ultima_atualizacao = time.time()
        self.pacientes_carregados = True

        if hasattr(self, 'atualizar_cores_linhas') and self.atualizar_cores_linhas:
            self.atualizar_cores_linhas()
    
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
                    
                    # Atualizar lista
                    self.carregar_pacientes(forcar=True)
                    
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

    def _ao_destruir(self, evento=None):
        """Chamado quando a aba for destruída"""
        # Indicar que a aplicação está sendo encerrada
        self.executando = False
        
        # Desvincula eventos para evitar chamadas após destruição
        try:
            self.treeview.unbind('<Double-1>')
            self.treeview.unbind('<<TreeviewSelect>>')
            self.treeview.unbind('<Motion>')
            if hasattr(self, 'entry_pesquisa'):
                self.entry_pesquisa.unbind("<KeyRelease>")
        except:
            pass
        
        # Limpar referências circulares
        self.janela_detalhes = None
        self.paciente_selecionado = None
        
        # Esvaziar a fila
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                pass
        
        # Encerrar pool de threads
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=False)
        
        # Interromper qualquer thread em execução
        for thread in threading.enumerate():
            if thread.name.startswith('ThreadPool') or thread.name.startswith('Thread-'):
                try:
                    if thread.is_alive() and thread is not threading.current_thread():
                        # Não podemos forçar o término, mas podemos marcar a flag
                        # para que as threads se encerrem na próxima verificação
                        pass
                except:
                    pass
        
        # Fechar conexão com banco de dados
        if hasattr(self, 'db') and hasattr(self.db, 'fechar_conexao'):
            self.db.fechar_conexao()

    def ao_clicar_duplo(self, evento):
        """Abre a janela de detalhes quando um paciente é clicado duas vezes"""
        self.abrir_detalhes_paciente()

    def abrir_detalhes_paciente(self):
        """Abre uma janela popup com os detalhes do paciente selecionado"""
        # Verificar se há paciente selecionado
        if not self.paciente_selecionado or not self.avaliacao_id:
            messagebox.showwarning("Aviso", "Selecione um paciente para ver seus detalhes.")
            return
        
        # Verificar e fechar janela anterior se existir
        if hasattr(self, 'janela_detalhes') and self.janela_detalhes and hasattr(self.janela_detalhes, 'window') and self.janela_detalhes.window.winfo_exists():
            self.janela_detalhes.window.destroy()
        
        # Criar nova janela de detalhes
        self.janela_detalhes = DetalhesPacienteWindow(
            self.frame, 
            self.paciente_selecionado, 
            self.cores, 
            FONTES
        )

    def _debounce(self, func, delay=300):
        """Implementa debouncing para eventos frequentes"""
        if hasattr(self, '_timer_id') and self._timer_id:
            self.frame.after_cancel(self._timer_id)
        self._timer_id = self.frame.after(delay, func)

    def _verificar_scroll_treeview(self, evento=None):
        """Verifica se o usuário rolou até o final da lista e carrega mais itens"""
        if hasattr(self, '_carregando_mais') and self._carregando_mais:
            return
            
        # Se estiver próximo do final da visualização
        try:
            if self.treeview.yview()[1] >= 0.9 and not self._carregando_mais_itens:
                self._carregando_mais_itens = True
                self._debounce(self._carregar_mais_itens)
        except:
            pass

    def _carregar_mais_itens(self):
        """Carrega mais itens quando o usuário rolar até o final"""
        try:
            # Calculamos a página atual
            itens_por_pagina = 30
            pagina_atual = (len(self.treeview.get_children()) // itens_por_pagina) + 1
            
            # Inicia thread para carregar a próxima página
            threading.Thread(
                target=self._thread_carregar_mais_itens, 
                args=(pagina_atual,), 
                daemon=True
            ).start()
        except Exception as e:
            print(f"Erro ao iniciar carregamento de mais itens: {e}")
        finally:
            self._carregando_mais_itens = False

    def _thread_carregar_mais_itens(self, pagina):
        """Thread para carregar mais itens"""
        try:
            # Criar nova instância do banco para esta thread
            db_thread = BancoDadosFisioterapia(self.db.nome_db)
            
            filtro = self.entry_pesquisa.get().strip().lower() if hasattr(self, 'entry_pesquisa') else ""
            
            # Modificar para usar paginação corretamente
            # e evitar duplicação dos mesmos pacientes
            avaliacoes = db_thread.listar_avaliacoes(filtro=filtro, pagina=pagina)
            
            # Verificar se já temos essas avaliações
            ids_existentes = set()
            if hasattr(self, 'treeview') and self.treeview.winfo_exists():
                for item in self.treeview.get_children():
                    item_values = self.treeview.item(item, 'values')
                    if item_values and item_values[0]:
                        ids_existentes.add(str(item_values[0]))
            
            # Filtrar apenas avaliações novas
            avaliacoes_novas = [av for av in avaliacoes if str(av.get('id', '')) not in ids_existentes]
            
            if not self.executando or not avaliacoes_novas:
                return
                
            # Adiciona somente os novos itens
            self.queue.put((self._adicionar_itens_treeview, [avaliacoes_novas]), block=False)
        except Exception as e:
            print(f"Erro ao carregar mais itens: {e}")

    def _adicionar_itens_treeview(self, avaliacoes):
        """Adiciona itens ao treeview sem limpar os existentes"""
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
        
        if hasattr(self, 'atualizar_cores_linhas') and self.atualizar_cores_linhas:
            self.atualizar_cores_linhas()

    def fechar_threads(self):
        """Método específico para forçar o encerramento de todas as threads"""
        self.executando = False
        
        # Cancelar timers e binds pendentes
        if hasattr(self, '_timer_id') and self._timer_id:
            try:
                self.frame.after_cancel(self._timer_id)
                self._timer_id = None
            except:
                pass
        
        if hasattr(self, '_scroll_timer') and self._scroll_timer:
            try:
                self.frame.after_cancel(self._scroll_timer)
                self._scroll_timer = None
            except:
                pass
        
        # Encerrar thread pool
        if hasattr(self, 'thread_pool'):
            try:
                self.thread_pool.shutdown(wait=False)
            except:
                pass
        
        # Limpar fila
        try:
            while not self.queue.empty():
                self.queue.get_nowait()
        except:
            pass
        
        # Fechar janela de detalhes se estiver aberta
        if hasattr(self, 'janela_detalhes') and self.janela_detalhes:
            try:
                if hasattr(self.janela_detalhes, 'window') and self.janela_detalhes.window.winfo_exists():
                    self.janela_detalhes.window.destroy()
                self.janela_detalhes = None
            except:
                pass
        
        # Fechar conexão do banco
        if hasattr(self, 'db') and self.db:
            self.db.fechar_conexao()
            self.db = None
        
        print("Threads e recursos da AbaClientes encerrados com sucesso")


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