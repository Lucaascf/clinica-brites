import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from config import CORES
from server.database import BancoDadosFisioterapia

def main():
    """Função principal que inicia o sistema"""
    try:
        # Configurar janela principal
        root = tk.Tk()
        root.title("Sistema de Avaliação Fisioterapêutica")
        
        # Abordagem simplificada para tela cheia
        largura = root.winfo_screenwidth()
        altura = root.winfo_screenheight()
        root.geometry(f"{largura}x{altura}+0+0")
        
        # Tentar maximizar a janela
        try:
            root.state('zoomed')  # Funciona no Windows e em alguns ambientes Linux
        except:
            pass  # Ignora se não funcionar
        
        # Configurar as cores da interface
        root.config(bg=CORES["fundo"])
        
        # Verificar se o banco de dados existe ou criá-lo
        db = BancoDadosFisioterapia()
        
        # Notebook principal
        notebook = ttk.Notebook(root)
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
        
        # Importar os módulos necessários
        from aba_clientes import AbaClientes
        from formulario import FormularioFisioterapia
        from server.database import modificar_salvar_formulario
        
        # Criar as abas
        aba_clientes = AbaClientes(notebook)
        formulario = FormularioFisioterapia(notebook)
        
        # Modificar o método salvar do formulário para usar o banco de dados
        modificar_salvar_formulario(formulario)
        
        # Importar IntegradorSistema para vincular as ações entre abas
        from integracao_aba_client import IntegradorSistema
        
        # Criar um integrador e usar os elementos que já criamos
        class IntegradorPersonalizado(IntegradorSistema):
            def __init__(self, root, notebook, aba_clientes, formulario):
                self.root = root
                self.notebook = notebook
                self.aba_clientes = aba_clientes
                self.formulario = formulario
                self.db = BancoDadosFisioterapia()
                self._configurar_acoes_aba_clientes()
        
        # Inicializar o integrador personalizado
        integrador = IntegradorPersonalizado(root, notebook, aba_clientes, formulario)
        
        # Configurar evento de fechamento da janela
        def ao_fechar():
            """Confirma antes de fechar se houver modificações não salvas no formulário"""
            if hasattr(formulario, 'modificado') and formulario.modificado:
                resposta = messagebox.askyesno(
                    "Sair", 
                    "Há alterações não salvas no formulário. Deseja realmente sair?",
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
        # Capturar qualquer erro e mostrar uma mensagem amigável
        traceback_str = traceback.format_exc()
        erro_detalhado = f"{str(e)}\n\nDetalhes técnicos:\n{traceback_str}"
        
        # Tentar criar uma janela de erro mesmo se o tkinter não estiver funcionando
        try:
            messagebox.showerror(
                "Erro ao Iniciar", 
                f"Ocorreu um erro ao iniciar a aplicação:\n\n{str(e)}\n\nVerifique o console para mais detalhes.",
                icon='error'
            )
        except:
            print("============== ERRO AO INICIAR O SISTEMA ==============")
            print(erro_detalhado)
            print("======================================================")
            
            # Em último caso, salvar log de erro em arquivo
            try:
                with open("erro_sistema.log", "w", encoding="utf-8") as f:
                    f.write(erro_detalhado)
                print("Log de erro salvo em 'erro_sistema.log'")
            except:
                pass
        
        print(erro_detalhado)

# Executar a função principal quando este script for executado diretamente
if __name__ == "__main__":
    main()