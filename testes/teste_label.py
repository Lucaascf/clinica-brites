import tkinter as tk
from tkinter import font as tkFont

# Constantes
PLACEHOLDER_COLOR = "gray"
FONTES = {
    "campo": ("Courier New", 10)
}

class EditableLabel(tk.Frame):
    def __init__(
        self,
        master,
        min_lines=3,
        width=None,
        max_chars=None,
        placeholder=None,
        placeholder_color=PLACEHOLDER_COLOR,
        font=FONTES["campo"],
        **kwargs
    ):
        super().__init__(master)
        
        self.max_chars = max_chars
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        
        # Configuração para cálculo preciso da largura
        self.font = tkFont.Font(family=font[0], size=font[1])
        char_width = self.font.measure("0")
        
        # Calcula largura baseada em max_chars se não houver width específico
        widget_width = width
        if max_chars is not None and width is None:
            widget_width = max_chars + 2  # Margem de 2 caracteres
            
            # Ajuste fino baseado na largura real da fonte
            text_width = self.font.measure("0" * max_chars)
            padding = self.font.measure("  ")  # Espaço para padding
            widget_width = (text_width + padding) // char_width
        
        # Widget Text com configuração otimizada
        self.text = tk.Text(
            self,
            wrap=tk.NONE if max_chars else tk.WORD,  # Desabilita wrap quando tem limite
            height=min_lines,
            width=widget_width if (width or max_chars) else 40,  # Default 40 se nenhum width
            font=font,
            padx=5,
            pady=5,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#d3d3d3",
            highlightcolor="#4a90d9",
            **kwargs
        )
        
        # Barra de rolagem (só horizontal quando tem limite de caracteres)
        self.scroll_x = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        self.scroll_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        
        self.text.config(
            xscrollcommand=self.scroll_x.set if max_chars else None,
            yscrollcommand=self.scroll_y.set
        )
        
        # Layout otimizado
        self.text.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Esconde as scrollbars inicialmente
        self.scroll_x.grid_remove()
        self.scroll_y.grid_remove()
        
        # Configuração de grid
        self.grid_rowconfigure(0, weight=1)
        if max_chars is None:
            self.grid_columnconfigure(0, weight=1)
        else:
            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=0)
        
        # Configuração de eventos
        self.text.bind("<FocusIn>", self._on_focus_in)
        self.text.bind("<FocusOut>", self._on_focus_out)
        self.text.bind("<Key>", lambda e: self.after(10, self._update_scrollbar))
        
        # Controle de foco e eventos de scroll
        self._has_focus = False
        self.text.bind("<FocusIn>", self._set_focus_true, add="+")
        self.text.bind("<FocusOut>", self._set_focus_false, add="+")
        
        # Bindings de scroll são ativados/desativados conforme o foco
        self._setup_scroll_bindings()
        
        # Identificador do binding para poder removê-lo quando necessário
        self.binding_id = None
        
        # Configurar evento quando o texto recebe foco
        self.text.bind("<FocusIn>", self._on_text_focus_in, add="+")
        
        # Configurar placeholder se fornecido
        if self.placeholder:
            self.text.insert('1.0', self.placeholder)
            self.text.config(fg=self.placeholder_color)
            
            # Bind eventos para o comportamento do placeholder
            self.text.bind('<FocusIn>', self._on_focus_in_placeholder, add="+")
            self.text.bind('<FocusOut>', self._on_focus_out_placeholder, add="+")
        
        # Validação de limite de caracteres (apenas se max_chars for especificado)
        if self.max_chars is not None:
            self.text.bind("<KeyPress>", self._check_limit)
    
    def _on_focus_in_placeholder(self, event):
        if self.text.get('1.0', 'end-1c') == self.placeholder:
            self.text.delete('1.0', tk.END)
            self.text.config(fg='black')

    def _on_focus_out_placeholder(self, event):
        if not self.text.get('1.0', 'end-1c'):
            self.text.insert('1.0', self.placeholder)
            self.text.config(fg=self.placeholder_color)

    def _update_scrollbars(self):
        """Atualiza a visibilidade das scrollbars conforme necessidade"""
        # Scrollbar vertical
        if self.text.yview() != (0.0, 1.0):
            self.scroll_y.grid()
        else:
            self.scroll_y.grid_remove()
        
        # Scrollbar horizontal (só aparece se tiver max_chars)
        if self.max_chars is not None and self.text.xview() != (0.0, 1.0):
            self.scroll_x.grid()
        else:
            self.scroll_x.grid_remove()

    def _check_limit(self, event):
        """Verifica se o texto excede o limite de caracteres"""
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Tab', 'Home', 'End', 'Return'):
            return
        
        current_text = self.text.get('1.0', 'end-1c')
        if len(current_text) >= self.max_chars:
            return "break"
    
    def _set_focus_true(self, event):
        """Marca o campo como tendo foco"""
        self._has_focus = True
        self._setup_scroll_bindings()
    
    def _set_focus_false(self, event):
        """Marca o campo como não tendo foco"""
        self._has_focus = False
        self._setup_scroll_bindings()
    
    def _setup_scroll_bindings(self):
        """Configura os bindings de scroll baseado no estado de foco"""
        # Primeiro remove qualquer binding existente
        self.text.unbind("<MouseWheel>")
        self.text.unbind("<Button-4>")
        self.text.unbind("<Button-5>")
        
        # Se o campo tem foco, adiciona os bindings para scroll
        if self._has_focus:
            self.text.bind("<MouseWheel>", self._on_mouse_scroll)
            self.text.bind("<Button-4>", self._on_scroll_up)
            self.text.bind("<Button-5>", self._on_scroll_down)
        else:
            # Quando não tem foco, bloqueia o scroll no campo e repassa para o formulário principal
            self.text.bind("<MouseWheel>", self._pass_scroll_to_parent)
            self.text.bind("<Button-4>", self._pass_scroll_up_to_parent)
            self.text.bind("<Button-5>", self._pass_scroll_down_to_parent)
    
    def _pass_scroll_to_parent(self, event):
        """Repassa o scroll para o formulário principal"""
        self.winfo_toplevel().event_generate("<MouseWheel>", 
                                           delta=event.delta,
                                           x=event.x_root, 
                                           y=event.y_root)
        return "break"  # Bloqueia o scroll no campo
    
    def _pass_scroll_up_to_parent(self, event):
        """Repassa o scroll para cima para o formulário principal (Linux)"""
        self.winfo_toplevel().event_generate("<Button-4>", 
                                           x=event.x_root, 
                                           y=event.y_root)
        return "break"  # Bloqueia o scroll no campo
    
    def _pass_scroll_down_to_parent(self, event):
        """Repassa o scroll para baixo para o formulário principal (Linux)"""
        self.winfo_toplevel().event_generate("<Button-5>", 
                                           x=event.x_root, 
                                           y=event.y_root)
        return "break"  # Bloqueia o scroll no campo
    
    def _on_text_focus_in(self, event):
        """Quando o texto recebe foco, configuramos o binding global"""
        # Remove binding anterior se existir
        if self.binding_id:
            self.winfo_toplevel().unbind("<Button-1>", self.binding_id)
        
        # Adiciona novo binding
        self.binding_id = self.winfo_toplevel().bind("<Button-1>", self._handle_global_click, add="+")
    
    def _handle_global_click(self, event):
        """Trata cliques em qualquer lugar da aplicação"""
        click_widget = event.widget
        
        # Se o clique foi em outro widget Text, não faz nada (permite que o foco mude)
        if isinstance(click_widget, tk.Text):
            return
            
        # Se o clique não foi no texto nem em seus filhos
        # E o texto está com foco, remove o foco
        if self.text.focus_displayof() and click_widget != self.text:
            # Verifica também se não é um filho do widget de texto
            parent = click_widget
            is_child = False
            
            # Verifica a hierarquia de widgets
            while parent and not is_child:
                if parent == self.text:
                    is_child = True
                    break
                try:
                    parent = parent.master
                except:
                    break
            
            # Se não for filho, remove o foco
            if not is_child:
                # Apenas remove o foco do texto
                self.master.focus_set()
    
    def _on_focus_in(self, event=None):
        """Quando o campo ganha foco"""
        self.text.config(highlightbackground="#4a90d9")
    
    def _on_focus_out(self, event=None):
        """Quando o campo perde foco"""
        self.text.config(highlightbackground="#d3d3d3")
    
    def _on_mouse_scroll(self, event):
        """Scroll do mouse (Windows/MacOS)"""
        self.text.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"  # Impede a propagação
    
    def _on_scroll_up(self, event):
        """Scroll para cima (Linux)"""
        self.text.yview_scroll(-1, "units")
        return "break"  # Impede a propagação
    
    def _on_scroll_down(self, event):
        """Scroll para baixo (Linux)"""
        self.text.yview_scroll(1, "units")
        return "break"  # Impede a propagação
    
    def _update_scrollbar(self):
        """Atualiza a visibilidade da scrollbar"""
        if self.text.yview() != (0.0, 1.0):
            self.scrollbar.grid()
        else:
            self.scrollbar.grid_remove()
    
    def get(self):
        """Retorna o texto sem a quebra de linha final"""
        text = self.text.get('1.0', 'end-1c')
        return text if text != self.placeholder else ""
    
    def insert(self, index, text):
        """Insere texto no campo"""
        self.text.insert(index, text)
        self._update_scrollbar()
    
    def delete(self, start, end):
        """Remove texto do campo"""
        self.text.delete(start, end)
        self._update_scrollbar()

# Exemplo de uso (mantido igual)
class MinhaAplicacao:
    def __init__(self, root):
        self.root = root
        self.cores = {
            "secao_bg": "#f0f0f0",
            "campo_bg": "white",
            "texto_destaque": "#333333"
        }
        self.campos = {}
        
        self.criar_interface()
    
    def criar_interface(self):
        frame_conteudo_secao = tk.Frame(self.root, bg=self.cores["secao_bg"], padx=10, pady=10)
        frame_conteudo_secao.pack(fill=tk.BOTH, expand=True)
        
        # Label e Campo de Contato
        label_contato = tk.Label(
            frame_conteudo_secao, 
            text="Contacto", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_contato.grid(row=2, column=0, padx=(0, 5), pady=(0, 10), sticky="w")
        
        # Campo COM limite de caracteres
        campo_contato = EditableLabel(
            frame_conteudo_secao,
            max_chars=30,
            min_lines=1,
            bg="white",
            placeholder="Ingrese contacto..."
        )
        campo_contato.grid(
            row=2, 
            column=1, 
            padx=(0, 20), 
            pady=(0, 10), 
            sticky="w"  # Alinha à esquerda para campos com limite
        )
        campo_contato.text.bind("<KeyRelease>", lambda e: self.marcar_modificado("Contacto"))
        self.campos["Contacto"] = campo_contato.text
        
        # Label e Campo de Descrição
        label_descricao = tk.Label(
            frame_conteudo_secao, 
            text="Descrição", 
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_descricao.grid(row=3, column=0, padx=(0, 5), pady=(0, 10), sticky="nw")
        
        # Campo COM limite curto de caracteres
        campo_descricao = EditableLabel(
            frame_conteudo_secao,
            max_chars=50,
            min_lines=3,
            bg=self.cores["campo_bg"],
            placeholder="Ingrese descrição (limitada a 10 caracteres)...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_descricao.grid(
            row=3, 
            column=1, 
            padx=(0, 20), 
            pady=(0, 10), 
            sticky="w"  # Alinha à esquerda para campos com limite
        )
        campo_descricao.text.bind("<KeyRelease>", lambda e: self.marcar_modificado("Descrição"))
        self.campos["Descrição"] = campo_descricao.text
        
        # Label e Campo de Observações (adicionando o rótulo como nos outros campos)
        label_observacoes = tk.Label(
            frame_conteudo_secao, 
            text="Observações",  # Texto do rótulo
            bg=self.cores["secao_bg"],
            fg=self.cores["texto_destaque"],
            font=FONTES["campo"]
        )
        label_observacoes.grid(row=4, column=0, padx=(0, 5), pady=(0, 10), sticky="nw")

        # Campo SEM limite de caracteres - se expande com o frame
        campo_observacoes = EditableLabel(
            frame_conteudo_secao,
            max_chars=20,
            min_lines=4,
            bg=self.cores["campo_bg"],
            placeholder="Ingrese observações (sem limite)...",
            placeholder_color=PLACEHOLDER_COLOR
        )
        campo_observacoes.grid(
            row=4, 
            column=1, 
            padx=(0, 20), 
            pady=(0, 10), 
            sticky="w"  # Alinha à esquerda
        )
        campo_observacoes.text.bind("<KeyRelease>", lambda e: self.marcar_modificado("Observações"))
        self.campos["Observações"] = campo_observacoes.text
        
        # Configuração de grid para expansão
        frame_conteudo_secao.columnconfigure(1, weight=1)
    
    def marcar_modificado(self, campo):
        print(f"Campo {campo} modificado:", self.campos[campo].get('1.0', 'end-1c'))

# Teste
if __name__ == "__main__":
    root = tk.Tk()
    app = MinhaAplicacao(root)
    root.mainloop()