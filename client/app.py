import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from config import CORES
from server.database import BancoDadosFisioterapia
import threading

# Importar o sistema de login
from client.crontrollers.integracao_login import integrar_login_sistema


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
        
        # Integrar sistema de login (isso controlará quando a janela principal será exibida)
        integrador_login = integrar_login_sistema(root)
        
        # Importante: O restante da configuração do sistema será executado somente após o login bem-sucedido
        # Isso é gerenciado pelo integrador de login, que chamará seu callback após autenticação
        
        # Configurar as abas e componentes após login
        def configurar_sistema_apos_login(dados_usuario):
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
            from client.ui.aba_clientes import adicionar_aba_clientes
            from client.ui.formulario import adicionar_formulario_fisioterapia
            from server.database import modificar_salvar_formulario
            from preencher_formulario_script import adicionar_botao_preenchimento


            # Criar as abas
            aba_clientes = adicionar_aba_clientes(notebook)
            formulario = adicionar_formulario_fisioterapia(notebook)

            # adicionar_botao_preenchimento(root)
            
            # Modificar o método salvar do formulário para usar o banco de dados
            modificar_salvar_formulario(formulario)
            
            
            # Importar IntegradorSistema para vincular as ações entre abas
            from client.crontrollers.integracao_aba_client import IntegradorSistema
            
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
            
            # Aplicar restrições de acesso conforme o perfil do usuário
            if dados_usuario and "perfil" in dados_usuario:
                if dados_usuario["perfil"] == "recepcionista":
                    # Recepcionista não pode acessar a aba de formulário
                    for i in range(notebook.index('end')):
                        tab_name = notebook.tab(i, "text")
                        if tab_name == "Evaluación":
                            notebook.tab(i, state="hidden")
                    
                    # Desabilitar botões específicos na aba de clientes
                    desabilitar_botoes_aba_clientes(aba_clientes)
            
            # Configurar evento de fechamento da janela
            def ao_fechar():
                """Confirma antes de fechar e garante encerramento limpo"""
                fechar_app = True
                
                # Verificar formulário não salvo
                if hasattr(formulario, 'modificado') and formulario.modificado:
                    resposta = messagebox.askyesno(
                        "Sair", 
                        "Há alterações não salvas no formulário. Deseja realmente sair?",
                        icon='warning'
                    )
                    fechar_app = resposta
                
                if fechar_app:
                    # Desativar eventos e protocolo WM_DELETE_WINDOW para evitar múltiplas chamadas
                    root.protocol("WM_DELETE_WINDOW", lambda: None)
                    
                    try:
                        # Use um cursor válido para o Linux
                        root.config(cursor="watch")
                    except:
                        pass  # Ignora se falhar
                    
                    # Desativar todos os widgets para evitar interações durante fechamento
                    for widget in root.winfo_children():
                        try:
                            widget.config(state="disabled")
                        except:
                            pass
                    
                    # Executar fechamento em uma thread separada para não travar a UI
                    # Modifique a função fechar_recursos em app.py (linha ~183) da seguinte forma:
                    def fechar_recursos():
                        try:
                            # Definir flag global para parar threads
                            if hasattr(aba_clientes, 'executando'):
                                aba_clientes.executando = False
                            
                            # Chamar método específico para fechar threads da aba_clientes
                            if hasattr(aba_clientes, 'fechar_threads'):
                                aba_clientes.fechar_threads()
                            
                            # Fechar conexão com banco de dados imediatamente
                            if hasattr(db, 'fechar_conexao'):
                                db.fechar_conexao()
                            
                            # Desativar o integrador de login para evitar que ele reabra a tela de login
                            if 'integrador_login' in globals():
                                if hasattr(integrador_login, 'desativar'):
                                    integrador_login.desativar()
                                elif hasattr(integrador_login, 'login_system'):
                                    if integrador_login.login_system and hasattr(integrador_login.login_system, 'janela_login'):
                                        if integrador_login.login_system.janela_login and hasattr(integrador_login.login_system.janela_login, 'winfo_exists'):
                                            if integrador_login.login_system.janela_login.winfo_exists():
                                                try:
                                                    integrador_login.login_system.janela_login.destroy()
                                                except:
                                                    pass
                            
                            # Encerrar aplicação após limpar recursos
                            # Use apenas destroy() para evitar problemas de thread com tkinter
                            root.after(100, lambda: root.destroy())
                            
                            # Encerrar o programa completamente após um breve delay
                            # Isso evita problemas com tkinter
                            import threading
                            threading.Timer(0.5, lambda: sys.exit(0)).start()
                            
                        except Exception as e:
                            print(f"Erro ao limpar recursos: {e}")
                            try:
                                root.destroy()
                            except:
                                pass
                            sys.exit(1)
                    
                    # Iniciar thread para fechamento
                    threading.Thread(target=fechar_recursos, daemon=True).start()
            
            # Configurar o protocolo de fechamento da janela
            root.protocol("WM_DELETE_WINDOW", ao_fechar)
        
        # Função para desabilitar botões específicos na aba de clientes para o recepcionista
        def desabilitar_botoes_aba_clientes(aba_clientes):
            # Procurar pelos botões na interface
            for widget in aba_clientes.frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        # Frame com botões
                        if isinstance(child, tk.Frame):
                            for botao in child.winfo_children():
                                if isinstance(botao, tk.Button):
                                    texto = botao.cget('text')
                                    # Desabilitar botões específicos
                                    if "Editar" in texto or "Excluir" in texto or "Nova Avaliação" in texto:
                                        botao.config(state="disabled")
                                        
                                # Procurar mais profundamente
                                if hasattr(botao, 'winfo_children'):
                                    for sub_widget in botao.winfo_children():
                                        if isinstance(sub_widget, tk.Button):
                                            texto = sub_widget.cget('text')
                                            if "Editar" in texto or "Excluir" in texto or "Nova Avaliação" in texto:
                                                sub_widget.config(state="disabled")
        
        # Adicionar o callback de configuração ao integrador de login
        integrador_login.callback_login_sucesso = configurar_sistema_apos_login
        
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