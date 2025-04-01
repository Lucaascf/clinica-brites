import tkinter as tk
from tkinter import messagebox

class ControleAcesso:
    """Controla as permissões de acesso baseado no perfil do usuário."""
    
    def __init__(self, usuario=None):
        """Inicializa o controle de acesso."""
        self.usuario = usuario
        self.permissoes = {}
        
        # Definir permissões baseado no perfil do usuário
        if usuario and 'perfil' in usuario:
            self.perfil = usuario['perfil']
            self.permissoes = self.obter_permissoes(self.perfil)
        else:
            self.perfil = None
    
    def obter_permissoes(self, perfil):
        """Retorna as permissões para o perfil especificado."""
        permissoes = {}
        
        if perfil == 'medico':
            # Permissões para médico (acesso total)
            permissoes = {
                'aba_clientes': True,
                'aba_formulario': True,
                'adicionar_cliente': True,
                'editar_cliente': True,
                'excluir_cliente': True,
                'gerenciar_usuarios': True,
                'configuracoes': True
            }
        elif perfil == 'recepcionista':
            # Permissões para recepcionista (acesso limitado)
            permissoes = {
                'aba_clientes': True,
                'aba_formulario': False,
                'adicionar_cliente': True,
                'editar_cliente': False,
                'excluir_cliente': False,
                'gerenciar_usuarios': False,
                'configuracoes': False
            }
        
        return permissoes
    
    def verificar_permissao(self, permissao):
        """Verifica se o usuário atual tem a permissão especificada."""
        if not self.permissoes:
            return False
        
        return self.permissoes.get(permissao, False)
    
    def configurar_interface(self, janela_principal):
        """Configura a interface baseada nas permissões do usuário."""
        if not self.usuario or not self.perfil:
            return
        
        # Atualizar título da janela
        if hasattr(janela_principal, 'title'):
            nome_perfil = "Médico" if self.perfil == "medico" else "Recepcionista"
            janela_principal.title(f"Sistema de Avaliação Fisioterapêutica - {self.usuario['nome']} ({nome_perfil})")
    
    def configurar_notebook(self, notebook):
        """Configura a visibilidade das abas no notebook baseado nas permissões."""
        if not self.perfil or not self.permissoes:
            return
        
        # Verificar todas as abas
        for i in range(notebook.index('end')):
            tab_nome = notebook.tab(i, "text")
            
            # Ocultar abas sem permissão
            if tab_nome == "Evaluación" and not self.verificar_permissao('aba_formulario'):
                notebook.tab(i, state="hidden")
            
            # Ocultar aba de usuários para recepcionistas
            if tab_nome == "Usuários" and not self.verificar_permissao('gerenciar_usuarios'):
                notebook.tab(i, state="hidden")
    
    def configurar_botoes(self, container):
        """Configura os botões dentro do container baseado nas permissões."""
        if not self.perfil or not self.permissoes:
            return
        
        # Aplicar configurações recursivamente
        self._configurar_widgets_recursivamente(container)
    
    def _configurar_widgets_recursivamente(self, parent):
        """Configura widgets recursivamente baseado nas permissões."""
        for widget in parent.winfo_children():
            # Verificar se é um botão
            if isinstance(widget, tk.Button):
                texto = widget.cget('text')
                
                # Desabilitar botões baseados no texto
                if "Editar" in texto and not self.verificar_permissao('editar_cliente'):
                    widget.config(state="disabled")
                elif "Excluir" in texto and not self.verificar_permissao('excluir_cliente'):
                    widget.config(state="disabled")
                elif "Nova Avaliação" in texto and not self.verificar_permissao('aba_formulario'):
                    widget.config(state="disabled")
                elif "Usuários" in texto and not self.verificar_permissao('gerenciar_usuarios'):
                    widget.config(state="disabled")
            
            # Continuar recursivamente para widgets filhos
            if hasattr(widget, 'winfo_children'):
                self._configurar_widgets_recursivamente(widget)
    
    def mostrar_erro_permissao(self, permissao_nome):
        """Mostra mensagem de erro quando o usuário não tem permissão."""
        nome_amigavel = {
            'aba_formulario': 'Acesso ao formulário de avaliação',
            'editar_cliente': 'Editar pacientes',
            'excluir_cliente': 'Excluir pacientes',
            'gerenciar_usuarios': 'Gerenciar usuários',
            'configuracoes': 'Acessar configurações'
        }.get(permissao_nome, permissao_nome)
        
        messagebox.showerror(
            "Acesso Negado", 
            f"Você não tem permissão para esta ação.\n\nPermissão necessária: {nome_amigavel}"
        )

# Classe para exibir informações do usuário logado
class InfoUsuario:
    """Widget para exibir informações do usuário logado e botão de logout."""
    
    def __init__(self, parent, usuario, callback_logout=None):
        """Inicializa o widget de informações do usuário."""
        self.parent = parent
        self.usuario = usuario
        self.callback_logout = callback_logout
        
        # Criar frame principal
        self.frame = tk.Frame(parent, padx=5, pady=5)
        
        # Criar widgets
        self.criar_widgets()
    
    def criar_widgets(self):
        """Cria os widgets de informação e botão de logout."""
        # Nome do perfil
        perfil_nome = "Médico" if self.usuario['perfil'] == 'medico' else "Recepcionista"
        
        # Label com informações do usuário
        info_label = tk.Label(
            self.frame,
            text=f"{self.usuario['nome']} ({perfil_nome})",
            font=("Arial", 10)
        )
        info_label.pack(side=tk.LEFT, padx=5)
        
        # Separador vertical
        separador = tk.Frame(self.frame, width=1, bg="gray")
        separador.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)
        
        # Botão de logout
        btn_logout = tk.Button(
            self.frame,
            text="Sair",
            command=self.fazer_logout,
            bg="#F44336",
            fg="white",
            font=("Arial", 8),
            padx=5,
            pady=2
        )
        btn_logout.pack(side=tk.LEFT)
    
    def fazer_logout(self):
        """Realiza o logout do sistema."""
        if messagebox.askyesno("Logout", "Deseja realmente sair do sistema?"):
            if self.callback_logout:
                self.callback_logout()

# Função para obter uma instância do controle de acesso
def obter_controle_acesso(usuario=None):
    """Retorna uma instância do controle de acesso com o usuário especificado."""
    return ControleAcesso(usuario)

# Para testes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Teste de Controle de Acesso")
    root.geometry("500x400")
    
    # Frame principal
    frame_principal = tk.Frame(root, padx=20, pady=20)
    frame_principal.pack(fill=tk.BOTH, expand=True)
    
    # Combo para selecionar perfil
    tk.Label(frame_principal, text="Selecione um perfil para testar:").pack(anchor="w")
    
    perfil_var = tk.StringVar(value="medico")
    perfil_frame = tk.Frame(frame_principal)
    perfil_frame.pack(fill=tk.X, pady=10)
    
    tk.Radiobutton(perfil_frame, text="Médico", variable=perfil_var, value="medico").pack(side=tk.LEFT)
    tk.Radiobutton(perfil_frame, text="Recepcionista", variable=perfil_var, value="recepcionista").pack(side=tk.LEFT)
    
    # Frame para exibir permissões
    permissoes_frame = tk.LabelFrame(frame_principal, text="Permissões", padx=10, pady=10)
    permissoes_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # Lista de permissões
    lista_permissoes = []
    
    # Função para atualizar a lista de permissões
    def atualizar_permissoes():
        # Limpar frame
        for widget in permissoes_frame.winfo_children():
            widget.destroy()
        
        # Obter permissões para o perfil selecionado
        usuario_teste = {'perfil': perfil_var.get(), 'nome': 'Usuário Teste'}
        controle = ControleAcesso(usuario_teste)
        
        # Exibir cada permissão
        row = 0
        for permissao, valor in controle.permissoes.items():
            # Ícone de status
            status = "✓" if valor else "✗"
            cor = "green" if valor else "red"
            
            tk.Label(permissoes_frame, text=status, fg=cor).grid(row=row, column=0, padx=5, pady=2)
            tk.Label(permissoes_frame, text=permissao).grid(row=row, column=1, sticky="w", padx=5, pady=2)
            tk.Label(permissoes_frame, text="Permitido" if valor else "Negado", fg=cor).grid(row=row, column=2, padx=5, pady=2)
            
            row += 1
    
    # Botão para atualizar permissões
    tk.Button(
        frame_principal,
        text="Atualizar Permissões",
        command=atualizar_permissoes,
        bg="#2196F3",
        fg="white"
    ).pack(pady=10)
    
    # Atualizar permissões iniciais
    atualizar_permissoes()
    
    # Vincular mudança de perfil para atualizar permissões
    perfil_var.trace_add("write", lambda *args: atualizar_permissoes())
    
    root.mainloop()