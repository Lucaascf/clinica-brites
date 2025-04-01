import tkinter as tk
from tkinter import messagebox, ttk
import random
import string
import time
from datetime import datetime, timedelta

def gerar_texto(tamanho=50):
    """Gera um texto aleatório com o tamanho especificado"""
    # Frases para fisioterapia para gerar texto mais realista
    frases = [
        "El paciente presenta dolor en la zona lumbar al realizar movimientos de flexión.",
        "Se observa limitación en el rango de movimiento articular.",
        "Presenta debilidad muscular en el cuádriceps izquierdo.",
        "Durante la evaluación, el paciente reportó dolor de intensidad moderada.",
        "Los ejercicios terapéuticos muestran mejoría gradual en la funcionalidad.",
        "El tratamiento incluye técnicas de movilización pasiva y activa.",
        "Se recomienda continuar con el plan de rehabilitación establecido.",
        "La evaluación muestra una disminución de la inflamación en la zona afectada.",
        "El paciente refiere dolor al realizar actividades cotidianas como subir escaleras.",
        "Se observa rigidez matutina que mejora con el movimiento durante el día."
    ]
    
    if tamanho < 30:
        # Para textos cortos, usar palabras aleatorias
        palavras = ["paciente", "dolor", "tratamiento", "evaluación", "fisioterapia", 
                   "movimiento", "muscular", "articulación", "columna", "ejercicio"]
        texto = " ".join(random.choices(palavras, k=tamanho//5+1))
        return texto[:tamanho].capitalize() + "."
    
    # Para textos mais longos, combinar frases
    texto = ""
    while len(texto) < tamanho:
        frase = random.choice(frases)
        if len(texto + frase) > tamanho:
            # Se adicionar a frase inteira ultrapassa o limite, cortar
            espaco_restante = tamanho - len(texto)
            if espaco_restante > 10:  # Só adicionar se tiver espaço razoável
                texto += frase[:espaco_restante]
            break
        texto += frase + " "
        
    return texto.strip()

def gerar_nome_completo():
    """Gera um nome completo aleatório"""
    nomes = ["Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Miguel", "Sofía", 
             "José", "Carmen", "Manuel", "Isabel", "Antonio", "Lucía"]
    
    sobrenomes = ["García", "Rodríguez", "Martínez", "Fernández", "López", "González", 
                  "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera"]
                  
    nome = random.choice(nomes)
    sobrenome1 = random.choice(sobrenomes)
    sobrenome2 = random.choice(sobrenomes)
    
    return f"{nome} {sobrenome1} {sobrenome2}"

def gerar_alergias():
    """Gera informações de alergias aleatórias"""
    alergias = [
        "No presenta alergias conocidas", 
        "Alergia a la penicilina",
        "Alergia al polen y gramíneas", 
        "Intolerancia a antiinflamatorios",
        "Alergia al látex", 
        "Alergia a frutos secos"
    ]
    
    if random.random() < 0.7:  # 70% de chance de não ter alergias
        return alergias[0]
    else:
        return random.choice(alergias[1:])

def gerar_numero(min_val=1, max_val=100):
    """Gera um número aleatório entre min_val e max_val"""
    return str(random.randint(min_val, max_val))

def preencher_formulario(app):
    """
    Preenche todos os campos do formulário com dados aleatórios
    
    Args:
        app: A janela principal da aplicação
    """
    # Solicitar tamanho mínimo de texto
    dialog = tk.Toplevel(app)
    dialog.title("Cantidad de caracteres")
    dialog.geometry("300x100")
    dialog.transient(app)
    dialog.grab_set()
    
    frame = tk.Frame(dialog, padx=10, pady=10)
    frame.pack(fill="both", expand=True)
    
    tk.Label(frame, text="Cantidad mínima de caracteres:").grid(row=0, column=0, sticky="w", pady=5)
    min_entry = tk.Entry(frame, width=10)
    min_entry.grid(row=0, column=1, padx=10, pady=5)
    min_entry.insert(0, "50")
    
    # Variáveis para armazenar o resultado
    resultado = {"min_chars": 50, "confirmed": False}
    
    def confirmar():
        try:
            resultado["min_chars"] = int(min_entry.get())
            resultado["confirmed"] = True
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un número válido")
    
    tk.Button(frame, text="Confirmar", command=confirmar).grid(row=1, column=0, columnspan=2, pady=10)
    
    # Centralizar o diálogo
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (app.winfo_width() // 2) - (width // 2) + app.winfo_x()
    y = (app.winfo_height() // 2) - (height // 2) + app.winfo_y()
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    app.wait_window(dialog)
    
    if not resultado["confirmed"]:
        return
    
    min_chars = resultado["min_chars"]
    
    # Método alternativo: preencher diretamente os campos encontrados
    # Encontrar campos de texto na interface
    def preencher_entrada_texto(widget, min_chars):
        """Preenche campos de entrada de texto"""
        if isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)
            widget.insert(0, gerar_texto(min(30, min_chars)))
            return True
        elif isinstance(widget, tk.Text):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", gerar_texto(min_chars))
            return True
        elif hasattr(widget, 'cget') and widget.winfo_class() == "TCombobox":
            # Combobox - selecionar um valor aleatório
            try:
                valores = widget.cget('values')
                if valores:
                    widget.set(random.choice(valores))
                else:
                    widget.set(gerar_texto(min(15, min_chars)))
                return True
            except:
                return False
        return False
    
    def preencher_objetos_complexos(widget):
        """Tenta preencher widgets personalizados (como CampoTextoAutoExpansivel)"""
        # Tentar identificar objetos específicos do formulário
        if hasattr(widget, 'definir') and hasattr(widget, 'texto'):
            # Parece ser um CampoTextoAutoExpansivel
            widget.definir(gerar_texto(min_chars))
            return True
        elif hasattr(widget, 'set_date'):
            # Parece ser um DateEntry
            data_aleatoria = datetime.now() - timedelta(days=random.randint(0, 365*5))
            widget.set_date(data_aleatoria)
            return True
        elif isinstance(widget, tk.Scale):
            # É um Scale
            widget.set(random.randint(0, widget.cget('to')))
            return True
        elif isinstance(widget, tk.Checkbutton) or (hasattr(widget, 'winfo_class') and widget.winfo_class() == "TCheckbutton"):
            # É um Checkbutton
            try:
                var = widget.cget('variable')
                if var:
                    var.set(random.choice([0, 1]))
                return True
            except:
                return False
        elif isinstance(widget, tk.Radiobutton) or (hasattr(widget, 'winfo_class') and widget.winfo_class() == "TRadiobutton"):
            # É um Radiobutton
            try:
                var = widget.cget('variable')
                if var:
                    val = widget.cget('value')
                    var.set(val)
                return True
            except:
                return False
        return False
    
    # Buscamos todos os widgets e tentamos preenchê-los
    def percorrer_widgets_recursivamente(parent, level=0):
        """Percorre todos os widgets recursivamente e tenta preenchê-los"""
        if level > 15:  # Evitar recursão infinita
            return 0
        
        count = 0
        
        # Verificar se este widget é um campo preenchível
        filled = preencher_entrada_texto(parent, min_chars)
        if not filled:
            filled = preencher_objetos_complexos(parent)
        
        if filled:
            count += 1
        
        # Percorrer todos os widgets filhos
        if hasattr(parent, 'winfo_children'):
            for child in parent.winfo_children():
                count += percorrer_widgets_recursivamente(child, level+1)
                
        return count
    
    # Mostrar mensagem de carregamento
    loading = tk.Toplevel(app)
    loading.title("Procesando")
    loading.geometry("300x80")
    loading.transient(app)
    
    msg = tk.Label(loading, text="Rellenando formulario...\nPor favor, espere.", padx=20, pady=20)
    msg.pack()
    
    loading.update()
    
    # Verificar se estamos na aba correta
    for widget in app.winfo_children():
        if isinstance(widget, ttk.Notebook):
            notebook_principal = widget
            # Encontrar a aba de avaliação
            for i in range(notebook_principal.index('end')):
                tab_name = notebook_principal.tab(i, "text")
                if tab_name == "Evaluación":
                    notebook_principal.select(i)
                    break
            break
    
    # Dar tempo para a UI atualizar
    app.update()
    time.sleep(0.3)
    
    # Preencher todos os campos que encontrarmos
    campos_preenchidos = percorrer_widgets_recursivamente(app)
    
    # Fechar mensagem de carregamento
    loading.destroy()
    
    # Mostrar mensagem de conclusão
    messagebox.showinfo("Éxito", f"¡Formulario rellenado con éxito! Se rellenaron {campos_preenchidos} campos.")

def adicionar_botao_preenchimento(app):
    """
    Adiciona um botão no rodapé da aplicação para iniciar o preenchimento automático
    
    Args:
        app: A janela principal da aplicação
    """
    # Encontrar todos os frames existentes na parte inferior da aplicação
    bottom_frames = []
    for widget in app.winfo_children():
        if isinstance(widget, tk.Frame) and widget.winfo_y() > app.winfo_height() * 0.8:
            bottom_frames.append(widget)
    
    # Se encontramos frames existentes na parte inferior, adicionamos nosso botão ao último
    if bottom_frames:
        btn_frame = bottom_frames[-1]
    else:
        # Criar novo frame
        btn_frame = tk.Frame(app, bg="#f0f0f0")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    btn_preencher = tk.Button(
        btn_frame,
        text="Rellenar Formulario",
        command=lambda: preencher_formulario(app),
        bg="#28a745",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=5
    )
    
    # Verificar se o botão já existe para não criar duplicados
    botao_existe = False
    for widget in btn_frame.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget('text') == "Rellenar Formulario":
            botao_existe = True
            break
    
    if not botao_existe:
        btn_preencher.pack(side=tk.RIGHT, padx=10)
    
    # Verificar se o botão está visível, se não, tentar outra abordagem
    try:
        app.update_idletasks()
        if not btn_preencher.winfo_viewable():
            # Criar um botão flutuante em vez disso
            btn_frame = tk.Toplevel(app)
            btn_frame.title("Herramienta")
            btn_frame.geometry("150x50")
            btn_frame.resizable(False, False)
            btn_frame.attributes('-topmost', True)
            
            btn_float = tk.Button(
                btn_frame,
                text="Rellenar Formulario",
                command=lambda: preencher_formulario(app),
                bg="#28a745",
                fg="white",
                font=("Segoe UI", 9),
                padx=5,
                pady=2
            )
            btn_float.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    except:
        # Se falhar, não fazer nada - o botão principal pode funcionar
        pass
    
    return btn_frame