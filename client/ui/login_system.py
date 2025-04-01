import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import datetime
import os

class LoginSystem:
    """Sistema de login simples usando banco de dados SQLite."""
    
    def __init__(self, root, callback_sucesso=None, db_path="fisioterapia.db"):
        """Inicializa o sistema de login."""
        # Configurações iniciais
        self.root = root
        self.callback_sucesso = callback_sucesso
        self.db_path = db_path
        
        # Esconder janela principal
        if hasattr(self.root, 'withdraw'):
            self.root.withdraw()
        
        # Verificar banco de dados e tabela de usuários
        self.verificar_banco_dados()
        
        # Criar janela de login
        self.janela_login = tk.Toplevel(self.root)
        self.janela_login.title("Login - Sistema de Fisioterapia")
        self.janela_login.geometry("400x300")
        self.janela_login.protocol("WM_DELETE_WINDOW", self.ao_fechar)
        self.janela_login.resizable(False, False)
        
        # Centralizar na tela
        largura_tela = self.janela_login.winfo_screenwidth()
        altura_tela = self.janela_login.winfo_screenheight()
        x = (largura_tela - 400) // 2
        y = (altura_tela - 300) // 2
        self.janela_login.geometry(f"400x300+{x}+{y}")
        
        # Criar interface
        self.criar_interface()
        
        # Focar na janela de login
        self.janela_login.focus_force()
    
    def verificar_banco_dados(self):
        """Verifica se o banco de dados e a tabela de usuários existem."""
        try:
            # Verificar se o banco existe
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se a tabela de usuários existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
            if not cursor.fetchone():
                # Criar tabela
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    perfil TEXT NOT NULL,
                    ultimo_acesso TEXT,
                    data_criacao TEXT
                )
                ''')
                
                # Criar usuários padrão
                data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Admin
                cursor.execute(
                    "INSERT INTO usuarios (username, senha, perfil, data_criacao) VALUES (?, ?, ?, ?)",
                    ('admin', self.hash_senha('admin123'), 'medico', data_atual)
                )
                
                # Médico
                cursor.execute(
                    "INSERT INTO usuarios (username, senha, perfil, data_criacao) VALUES (?, ?, ?, ?)",
                    ('medico', self.hash_senha('medico123'), 'medico', data_atual)
                )
                
                # Recepcionista
                cursor.execute(
                    "INSERT INTO usuarios (username, senha, perfil, data_criacao) VALUES (?, ?, ?, ?)",
                    ('recepcao', self.hash_senha('recepcao123'), 'recepcionista', data_atual)
                )
                
                conn.commit()
                print("Tabela de usuários criada com sucesso!")
            
            conn.close()
            
        except Exception as e:
            print(f"Erro ao verificar banco de dados: {e}")
    
    def hash_senha(self, senha):
        """Cria um hash da senha usando SHA-256."""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def criar_interface(self):
        """Cria a interface de login."""
        # Frame principal
        frame = tk.Frame(self.janela_login, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(
            frame,
            text="SISTEMA DE FISIOTERAPIA",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Separador
        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # Usuário
        tk.Label(frame, text="Usuário:", anchor="w").pack(fill=tk.X, pady=(10, 0))
        self.usuario_entry = tk.Entry(frame)
        self.usuario_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Senha
        tk.Label(frame, text="Senha:", anchor="w").pack(fill=tk.X, pady=(10, 0))
        self.senha_entry = tk.Entry(frame, show="*")
        self.senha_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Botão de login
        self.btn_login = tk.Button(
            frame,
            text="Entrar",
            command=self.fazer_login,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        )
        self.btn_login.pack(fill=tk.X, pady=10)
        
        # Vincular Enter para login
        self.usuario_entry.bind("<Return>", lambda event: self.senha_entry.focus())
        self.senha_entry.bind("<Return>", lambda event: self.fazer_login())
        
        # Focar no primeiro campo
        self.usuario_entry.focus()
    
    def fazer_login(self):
        """Valida as credenciais e faz o login."""
        usuario = self.usuario_entry.get().strip()
        senha = self.senha_entry.get().strip()
        
        # Validar campos
        if not usuario or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return
        
        try:
            # Conectar ao banco
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar usuário
            cursor.execute("SELECT * FROM usuarios WHERE username = ?", (usuario,))
            user = cursor.fetchone()
            
            # Verificar se usuário existe
            if not user:
                messagebox.showerror("Erro", "Usuário não encontrado.")
                conn.close()
                return
            
            # Verificar senha
            if self.hash_senha(senha) != user['senha']:
                messagebox.showerror("Erro", "Senha incorreta.")
                conn.close()
                return
            
            # Registrar acesso
            data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "UPDATE usuarios SET ultimo_acesso = ? WHERE id = ?",
                (data_atual, user['id'])
            )
            conn.commit()
            
            # Montar dados do usuário para retorno
            dados_usuario = {
                'id': user['id'],
                'username': user['username'],
                'nome': user['username'],  # Poderia ter um campo nome, mas usamos username
                'perfil': user['perfil']
            }
            
            conn.close()
            
            # Fechar janela de login e mostrar janela principal
            self.janela_login.destroy()
            if hasattr(self.root, 'deiconify'):
                self.root.deiconify()
            
            # Chamar callback de sucesso
            if self.callback_sucesso:
                self.callback_sucesso(dados_usuario)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fazer login: {str(e)}")
    
    def ao_fechar(self):
        """Ação ao fechar a janela de login."""
        try:
            # Verificar se a janela raiz ainda existe antes de mostrar o diálogo
            if not self.root.winfo_exists():
                # A janela principal já foi destruída, então apenas feche
                self.janela_login.destroy()
                import sys
                sys.exit(0)
                return
                
            # Se chegou aqui, a janela principal ainda existe
            resposta = messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?")
            if resposta:
                try:
                    self.root.quit()
                    self.root.destroy()
                except:
                    pass
                    
                try:
                    self.janela_login.destroy()
                except:
                    pass
                    
                import sys
                sys.exit(0)
        except Exception as e:
            # Em caso de qualquer erro, apenas force o fechamento
            print(f"Erro ao fechar: {e}")
            import sys
            sys.exit(0)

# Função para iniciar o login
def iniciar_login(root, callback_sucesso=None, db_path="fisioterapia.db"):
    """Inicia o sistema de login."""
    return LoginSystem(root, callback_sucesso, db_path)

# Para testes
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    def ao_logar(usuario):
        """Callback chamado após login bem-sucedido."""
        root.deiconify()
        root.title(f"Bem-vindo, {usuario['nome']} ({usuario['perfil']})")
        
        # Interface de teste
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text=f"Logado como: {usuario['nome']}",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        tk.Label(
            frame,
            text=f"Perfil: {usuario['perfil']}",
            font=("Arial", 12)
        ).pack(pady=5)
        
        tk.Button(
            frame,
            text="Sair",
            command=root.destroy,
            bg="#F44336",
            fg="white",
            padx=10,
            pady=5
        ).pack(pady=20)
    
    login = iniciar_login(root, ao_logar)
    
    root.mainloop()