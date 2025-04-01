import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import datetime
import os

class AdminUsuarios:
    """Interface simplificada para gerenciar usuários no banco de dados SQLite."""
    
    def __init__(self, db_path="fisioterapia.db"):
        # Criar a janela principal
        self.window = tk.Tk()
        self.window.title("Gerenciamento de Usuários")
        self.window.geometry("800x500")
        
        # Caminho do banco de dados
        self.db_path = db_path
        
        # Verificar e criar tabela de usuários se necessário
        self.verificar_tabela_usuarios()
        
        # Criar interface
        self.criar_interface()
        
        # Carregar usuários
        self.carregar_usuarios()
    
    def verificar_tabela_usuarios(self):
        """Verifica se a tabela de usuários existe e cria se necessário."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
            if not cursor.fetchone():
                # Criar tabela de usuários
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
                
                # Administrador
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
            messagebox.showerror("Erro", f"Erro ao verificar tabela de usuários: {str(e)}")
    
    def hash_senha(self, senha):
        """Cria um hash da senha usando SHA-256."""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def criar_interface(self):
        """Cria a interface com lista de usuários e botões de ação."""
        # Frame principal
        frame_principal = tk.Frame(self.window)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(
            frame_principal, 
            text="GERENCIAMENTO DE USUÁRIOS",
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Frame da tabela
        frame_tabela = tk.Frame(frame_principal)
        frame_tabela.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tabela de usuários (Treeview)
        colunas = ("id", "username", "perfil", "ultimo_acesso")
        self.tabela = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Configurar cabeçalhos
        self.tabela.heading("id", text="ID")
        self.tabela.heading("username", text="Usuário")
        self.tabela.heading("perfil", text="Perfil")
        self.tabela.heading("ultimo_acesso", text="Último Acesso")
        
        # Configurar larguras
        self.tabela.column("id", width=50, anchor="center")
        self.tabela.column("username", width=150)
        self.tabela.column("perfil", width=150)
        self.tabela.column("ultimo_acesso", width=200)
        
        # Vincular scrollbar
        scrollbar.config(command=self.tabela.yview)
        
        # Empacotar tabela
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(fill=tk.X, pady=10)
        
        # Botões
        tk.Button(
            frame_botoes,
            text="Adicionar",
            command=self.adicionar_usuario,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            frame_botoes,
            text="Editar",
            command=self.editar_usuario,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            frame_botoes,
            text="Excluir",
            command=self.excluir_usuario,
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            frame_botoes,
            text="Atualizar",
            command=self.carregar_usuarios,
            bg="#607D8B",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=5
        ).pack(side=tk.RIGHT, padx=5)
    
    def carregar_usuarios(self):
        """Carrega os usuários do banco de dados para a tabela."""
        # Limpar tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        try:
            # Conectar ao banco
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar usuários
            cursor.execute("SELECT * FROM usuarios ORDER BY username")
            usuarios = cursor.fetchall()
            
            # Adicionar à tabela
            for usuario in usuarios:
                # Formatar perfil para exibição
                perfil_exibicao = "Médico" if usuario['perfil'] == 'medico' else "Recepcionista"
                
                # Formatar último acesso
                ultimo_acesso = usuario['ultimo_acesso'] if usuario['ultimo_acesso'] else "Nunca acessou"
                
                # Inserir na tabela
                self.tabela.insert('', 'end', values=(
                    usuario['id'],
                    usuario['username'],
                    perfil_exibicao,
                    ultimo_acesso
                ))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {str(e)}")
    
    def adicionar_usuario(self):
        """Abre janela para adicionar novo usuário."""
        # Janela de diálogo
        dialog = tk.Toplevel(self.window)
        dialog.title("Adicionar Usuário")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Campos
        tk.Label(dialog, text="Nome de usuário:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        nome_usuario = tk.Entry(dialog, width=25)
        nome_usuario.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Senha:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        senha = tk.Entry(dialog, width=25, show="*")
        senha.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Perfil:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        perfil = ttk.Combobox(dialog, width=22, values=["medico", "recepcionista"], state="readonly")
        perfil.grid(row=2, column=1, padx=10, pady=5)
        perfil.current(0)
        
        # Frame de botões
        frame_botoes = tk.Frame(dialog)
        frame_botoes.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Função para salvar
        def salvar():
            # Validar campos
            if not nome_usuario.get() or not senha.get():
                messagebox.showerror("Erro", "Preencha todos os campos.")
                return
            
            try:
                # Conectar ao banco
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Verificar se usuário já existe
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = ?", (nome_usuario.get(),))
                if cursor.fetchone()[0] > 0:
                    messagebox.showerror("Erro", "Nome de usuário já existe.")
                    conn.close()
                    return
                
                # Data atual
                data_atual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Inserir usuário
                cursor.execute(
                    "INSERT INTO usuarios (username, senha, perfil, data_criacao) VALUES (?, ?, ?, ?)",
                    (nome_usuario.get(), self.hash_senha(senha.get()), perfil.get(), data_atual)
                )
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Sucesso", "Usuário adicionado com sucesso!")
                dialog.destroy()
                self.carregar_usuarios()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar usuário: {str(e)}")
        
        # Botões
        tk.Button(frame_botoes, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Salvar", command=salvar, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
    
    def editar_usuario(self):
        """Edita o usuário selecionado."""
        # Verificar se há seleção
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para editar.")
            return
        
        # Obter ID do usuário selecionado
        user_id = self.tabela.item(selecionado[0], "values")[0]
        
        try:
            # Buscar dados do usuário
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                messagebox.showerror("Erro", "Usuário não encontrado.")
                conn.close()
                return
            
            # Janela de diálogo
            dialog = tk.Toplevel(self.window)
            dialog.title(f"Editar Usuário: {usuario['username']}")
            dialog.geometry("350x200")
            dialog.resizable(False, False)
            dialog.transient(self.window)
            dialog.grab_set()
            
            # Campos
            tk.Label(dialog, text="Nome de usuário:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            tk.Label(dialog, text=usuario['username']).grid(row=0, column=1, padx=10, pady=5, sticky="w")
            
            tk.Label(dialog, text="Nova senha:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
            senha = tk.Entry(dialog, width=25, show="*")
            senha.grid(row=1, column=1, padx=10, pady=5)
            
            tk.Label(dialog, text="Perfil:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
            perfil = ttk.Combobox(dialog, width=22, values=["medico", "recepcionista"], state="readonly")
            perfil.grid(row=2, column=1, padx=10, pady=5)
            perfil.set(usuario['perfil'])
            
            # Frame de botões
            frame_botoes = tk.Frame(dialog)
            frame_botoes.grid(row=3, column=0, columnspan=2, pady=15)
            
            # Função para salvar
            def salvar():
                try:
                    # Verificar se está alterando o perfil do último médico
                    if usuario['perfil'] == 'medico' and perfil.get() != 'medico':
                        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'medico'")
                        if cursor.fetchone()[0] <= 1:
                            messagebox.showerror("Erro", "Não é possível alterar o perfil do último médico.")
                            return
                    
                    # Atualizar usuário
                    if senha.get():  # Se forneceu nova senha
                        cursor.execute(
                            "UPDATE usuarios SET perfil = ?, senha = ? WHERE id = ?",
                            (perfil.get(), self.hash_senha(senha.get()), user_id)
                        )
                    else:  # Sem alteração de senha
                        cursor.execute(
                            "UPDATE usuarios SET perfil = ? WHERE id = ?",
                            (perfil.get(), user_id)
                        )
                    
                    conn.commit()
                    messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                    dialog.destroy()
                    self.carregar_usuarios()
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao atualizar usuário: {str(e)}")
            
            # Botões
            tk.Button(frame_botoes, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            tk.Button(frame_botoes, text="Salvar", command=salvar, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados do usuário: {str(e)}")
    
    def excluir_usuario(self):
        """Exclui o usuário selecionado."""
        # Verificar se há seleção
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir.")
            return
        
        # Obter dados do usuário selecionado
        user_id = self.tabela.item(selecionado[0], "values")[0]
        username = self.tabela.item(selecionado[0], "values")[1]
        
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmar", f"Deseja realmente excluir o usuário '{username}'?"):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Verificar perfil do usuário
            cursor.execute("SELECT perfil FROM usuarios WHERE id = ?", (user_id,))
            perfil = cursor.fetchone()['perfil']
            
            # Verificar se é o último médico
            if perfil == 'medico':
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'medico'")
                if cursor.fetchone()[0] <= 1:
                    messagebox.showerror("Erro", "Não é possível excluir o último usuário médico.")
                    conn.close()
                    return
            
            # Excluir usuário
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
            conn.commit()
            
            messagebox.showinfo("Sucesso", f"Usuário '{username}' excluído com sucesso!")
            self.carregar_usuarios()
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")
    
    def executar(self):
        """Inicia a aplicação."""
        self.window.mainloop()

# Executar quando rodado diretamente
if __name__ == "__main__":
    app = AdminUsuarios()
    app.executar()