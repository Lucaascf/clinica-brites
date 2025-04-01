import tkinter as tk
import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o sistema de login
from client.ui.login_system import iniciar_login

# Importar o controle de acesso
from client.ui.perfis_acesso import obter_controle_acesso, InfoUsuario

def integrar_login_sistema(root):
    """
    Integra o sistema de login à aplicação principal
    
    Args:
        root: Janela raiz do tkinter
        
    Returns:
        objeto: Instância do integrador com callbacks configuráveis
    """
    class IntegradorLogin:
        def __init__(self, root):
            self.root = root
            self.login_system = None
            self.dados_usuario = None
            self.controle_acesso = None
            self.info_widget = None
            self.callback_login_sucesso = None
            self.ativo = True  # Flag para controlar se o integrador está ativo
            
            # Iniciar o sistema de login
            self.iniciar_login()
        
        def iniciar_login(self):
            """Inicia o sistema de login"""
            if self.ativo:  # Só inicia o login se o integrador estiver ativo
                self.login_system = iniciar_login(self.root, self.on_login_sucesso)
        
        def on_login_sucesso(self, dados_usuario):
            """Callback chamado após login bem-sucedido"""
            if not self.ativo:  # Verifica se o integrador ainda está ativo
                return
                
            self.dados_usuario = dados_usuario
            
            # Inicializar controle de acesso
            self.controle_acesso = obter_controle_acesso(dados_usuario)
            
            # Configurar interface baseada nas permissões
            self.controle_acesso.configurar_interface(self.root)
            
            # Adicionar widget com informações do usuário
            # Localizar o frame onde será colocado o widget de informações
            frame_superior = None
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame) and widget.winfo_height() < 100:
                    frame_superior = widget
                    break
            
            # Se não encontrou, criar um frame
            if not frame_superior:
                frame_superior = tk.Frame(self.root)
                frame_superior.pack(fill=tk.X, pady=5)
            
            # Criar widget de informações do usuário
            self.info_widget = InfoUsuario(
                frame_superior, 
                dados_usuario, 
                self.fazer_logout
            )
            self.info_widget.frame.pack(side=tk.RIGHT, padx=10)
            
            # Callback configurável para ações adicionais
            if self.callback_login_sucesso:
                self.callback_login_sucesso(dados_usuario)
        
        def desativar(self):
            """Desativa o integrador para evitar que ele reinicie o login"""
            self.ativo = False
            if self.login_system and hasattr(self.login_system, 'janela_login'):
                if self.login_system.janela_login and hasattr(self.login_system.janela_login, 'winfo_exists'):
                    if self.login_system.janela_login.winfo_exists():
                        try:
                            self.login_system.janela_login.destroy()
                        except:
                            pass
        
        def fazer_logout(self):
            """Faz logout e reinicia o sistema de login"""
            if not self.ativo:  # Verifica se o integrador ainda está ativo
                return
                
            # Limpar interface atual
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Reiniciar o sistema de login
            self.iniciar_login()
    
    # Retornar integrador que pode ser configurado pelo chamador
    return IntegradorLogin(root)