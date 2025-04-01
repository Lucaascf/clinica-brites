# integracao_aba_client.py
"""
Módulo responsável por integrar a aba de clientes com o formulário de avaliação.
Este módulo permite que a aba de clientes possa abrir o formulário de avaliação
para editar uma avaliação existente ou criar uma nova avaliação para um paciente.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from client.ui.aba_clientes import AbaClientes
from server.database import BancoDadosFisioterapia, modificar_salvar_formulario

class IntegradorSistema:
    """
    Classe responsável por integrar os diferentes componentes do sistema:
    - Aba de clientes
    - Formulário de avaliação
    """
    def __init__(self, root):
        """
        Inicializa o integrador
        
        Args:
            root: Janela principal do Tkinter
        """
        self.root = root
        self.notebook = None
        self.aba_clientes = None
        self.formulario = None
        self.db = BancoDadosFisioterapia()
        
        # Configurar o sistema
        self.configurar_sistema()
    
    def configurar_sistema(self):
        """Configura o sistema com todas as abas e funcionalidades"""
        # Criar o notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        
        # Importação dinâmica dentro do método
        from client.ui.formulario import FormularioFisioterapia
        
        # Inicializar aba de clientes e formulário
        self.aba_clientes = AbaClientes(self.notebook)
        self.formulario = FormularioFisioterapia(self.notebook)
        
        # Modificar o método salvar do formulário para usar o banco de dados
        modificar_salvar_formulario(self.formulario)
        
        # Sobrescrever os métodos de ação na aba de clientes
        self._configurar_acoes_aba_clientes()
    
    def _configurar_acoes_aba_clientes(self):
        """Configura as ações da aba de clientes para interagir com o formulário"""
        # Substituir o método de nova avaliação
        def nova_avaliacao(self_aba):
            if not self_aba.paciente_selecionado:
                messagebox.showwarning("Aviso", "Selecione um paciente para criar uma nova avaliação.")
                return
            
            # Mudar para a aba do formulário
            self.notebook.select(1)  # Índice da aba do formulário
            
            # Limpar o formulário atual
            self.formulario.limpar_formulario()
            
            # Preencher os dados básicos do paciente
            self._preencher_dados_basicos_paciente(self.formulario, self_aba.paciente_selecionado)
            
            # Feedback
            messagebox.showinfo(
                "Nova Avaliação",
                f"Criando nova avaliação para o paciente: {self_aba.paciente_selecionado.get('Nombre Completo', 'Paciente')}"
            )
        
        # Substituir o método de editar avaliação
        def editar_avaliacao(self_aba):
            if not self_aba.paciente_selecionado or not self_aba.avaliacao_id:
                messagebox.showwarning("Aviso", "Selecione um paciente para editar sua avaliação.")
                return
            
            # Mudar para a aba do formulário
            self.notebook.select(1)  # Índice da aba do formulário
            
            # Limpar o formulário atual
            self.formulario.limpar_formulario()
            
            # Preencher todos os dados da avaliação
            self._preencher_formulario_com_avaliacao(self.formulario, self_aba.avaliacao_id)
            
            # Feedback
            messagebox.showinfo(
                "Editar Avaliação",
                f"Editando avaliação do paciente: {self_aba.paciente_selecionado.get('Nombre Completo', 'Paciente')}"
            )
        
        # Configurar a referência da aba de clientes no formulário
        self.formulario.aba_clientes = self.aba_clientes
        
        # Substituir os métodos na instância da aba de clientes
        import types
        self.aba_clientes.abrir_nova_avaliacao = types.MethodType(nova_avaliacao, self.aba_clientes)
        self.aba_clientes.editar_avaliacao = types.MethodType(editar_avaliacao, self.aba_clientes)
    
    def _preencher_dados_basicos_paciente(self, formulario, dados_paciente):
        """
        Preenche os dados básicos do paciente no formulário
        
        Args:
            formulario: Instância do FormularioFisioterapia
            dados_paciente: Dicionário com os dados do paciente
        """
        # Mapear campos básicos do paciente
        campos_basicos = {
            'Nombre Completo': 'Nombre Completo',
            'Edad': 'Edad',
            'Genero': 'Genero',
            'Contacto': 'Contacto',
            'Fecha Nasc.': 'Fecha Nasc.',
            'Área de consulta': 'Área de consulta',
            'Alergias': 'Alergias'
        }
        
        # Preencher os campos mapeados
        for campo_form, campo_dados in campos_basicos.items():
            if campo_dados in dados_paciente and campo_form in formulario.campos:
                valor = dados_paciente.get(campo_dados, '')
                
                if hasattr(formulario.campos[campo_form], 'definir'):
                    # Para campos de texto
                    formulario.campos[campo_form].definir(valor)
                elif hasattr(formulario.campos[campo_form], 'set_date'):
                    # Para campos de data
                    try:
                        # Assumindo que a data está no formato DD/MM/YYYY
                        import datetime
                        partes = valor.split('/')
                        if len(partes) == 3:
                            dia, mes, ano = partes
                            data = datetime.datetime(int(ano), int(mes), int(dia))
                            formulario.campos[campo_form].set_date(data)
                    except:
                        # Se falhar, deixa a data atual
                        pass
    
    def _preencher_formulario_com_avaliacao(self, formulario, avaliacao_id):
        """
        Preenche todos os campos do formulário com os dados de uma avaliação existente
        
        Args:
            formulario: Instância do FormularioFisioterapia
            avaliacao_id: ID da avaliação a ser carregada
        """
        # Obter dados da avaliação
        dados = self.db.obter_avaliacao(avaliacao_id)
        if not dados:
            messagebox.showerror("Erro", "Não foi possível carregar os dados da avaliação.")
            return
        
        # Preencher dados básicos primeiro
        self._preencher_dados_basicos_paciente(formulario, dados)
        
        # Preencher os demais campos do formulário
        for campo, valor in dados.items():
            if campo in formulario.campos:
                # Pular campos já preenchidos pelos dados básicos
                if campo in ['Nombre Completo', 'Edad', 'Genero', 'Contacto', 'Fecha Nasc.', 'Área de consulta', 'Alergias']:
                    continue
                
                if hasattr(formulario.campos[campo], 'definir'):
                    # Para campos de texto
                    formulario.campos[campo].definir(valor)
                elif isinstance(formulario.campos[campo], tk.Scale):
                    # Para escala de dor
                    formulario.campos[campo].set(valor)
                elif isinstance(formulario.campos[campo], tk.StringVar):
                    # Para variáveis de string (combobox, etc)
                    formulario.campos[campo].set(valor)
        
        # Preencher checkbuttons de força muscular
        if 'Fuerza Muscular' in dados and hasattr(formulario, 'checkbuttons'):
            for check, var in formulario.checkbuttons:
                texto = check.cget('text')
                if texto in dados['Fuerza Muscular']:
                    var.set(True)
        
        # Preencher radio buttons
        if hasattr(formulario, 'radio_buttons'):
            for nome_var, variavel in formulario.radio_buttons.items():
                if nome_var in dados:
                    variavel.set(dados[nome_var])
        
        # Marcar como não modificado inicialmente
        formulario.modificado = False


def iniciar_sistema():
    """Inicia o sistema completo"""
    # Configurar janela principal
    root = tk.Tk()
    root.title("Sistema de Avaliação Fisioterapêutica")
    
    # Configurar tamanho da janela
    largura = root.winfo_screenwidth()
    altura = root.winfo_screenheight()
    root.geometry(f"{largura}x{altura}+0+0")
    
    try:
        root.state('zoomed')  # Funciona no Windows
    except:
        pass  # Ignora se não funcionar
    
    # Iniciar sistema integrado
    sistema = IntegradorSistema(root)
    
    # Iniciar loop principal
    root.mainloop()


# Executar se este arquivo for o principal
if __name__ == "__main__":
    iniciar_sistema()