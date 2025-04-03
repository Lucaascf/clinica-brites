import tkinter as tk
from tkinter import font


class EditableLabel(tk.Text):
    def __init__(self, master, width=None, **kwargs):
        # Configuração inicial para parecer uma label
        kwargs.setdefault('wrap', tk.WORD)
        kwargs.setdefault('height', 1)
        kwargs.setdefault('padx', 5) 
        kwargs.setdefault('pady', 5)
        kwargs.setdefault('relief', tk.FLAT)
        kwargs.setdefault('highlightthickness', 1)
        kwargs.setdefault('highlightbackground', "#d3d3d3")
        
        # Se width foi especificado, converte para pixels
        if width is not None:
            kwargs['width'] = width
            
        super().__init__(master, **kwargs)
        
        # Eventos para controle do comportamento
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Key>", self.on_key_press)
        self.bind("<Configure>", self.on_configure)  # Evento de redimensionamento
        
        self.texto_original = ""
        self.is_editing = False
        self._last_width = 0
    
    def on_focus_in(self, event):
        """Quando clicado, mostra borda de edição"""
        self.config(highlightbackground="#4a90d9")
        self.is_editing = True
    
    def on_focus_out(self, event):
        """Quando perde foco, volta a parecer uma label"""
        self.config(highlightbackground="#d3d3d3")
        self.is_editing = False
        self.resize()
    
    def on_key_press(self, event):
        """Redimensiona dinamicamente enquanto digita"""
        self.resize()  # Chama resize diretamente, sem delay\\\
    
    def on_configure(self, event):
        """Quando o widget é redimensionado, recalcula o layout"""
        if event.width != self._last_width:
            self._last_width = event.width
            self.after(10, self.resize)
    
    def resize(self):
        """Ajusta a altura com base no conteúdo e largura atual"""
        texto = self.get("1.0", "end-1c")  # Pega todo o texto
        
        # Força uma atualização do layout antes de calcular
        self.update_idletasks()
        
        # Calcula quantas linhas são necessárias
        linhas = self._calcular_numero_linhas(texto)
        
        # Define a nova altura (mínimo 1 linha)
        self.config(height=max(1, linhas))
        
        # Atualiza imediatamente
        self.update_idletasks()
    
    def _calcular_numero_linhas(self, texto):
        """
        Estima o número de linhas do texto com base na largura atual do widget.
        """
        if not texto:
            return 1
            
        # Obtém a fonte atual
        fonte = font.Font(self, self.cget("font"))
        
        # Largura disponível para texto (descontando padding e bordas)
        largura_disponivel = self.winfo_width() - 2 * (int(self.cget('padx')) + int(self.cget('highlightthickness')))
        
        # Se ainda não tem largura definida ou é muito pequena, use um valor razoável
        if largura_disponivel <= 20:
            largura_disponivel = 400  # Valor padrão razoável
            
        linhas = 1
        largura_atual = 0
        
        # Divide o texto em palavras
        palavras = texto.split()
        
        for palavra in palavras:
            palavra_largura = fonte.measure(palavra + " ")
            
            if largura_atual + palavra_largura > largura_disponivel:
                # Se a palavra não cabe na linha atual, quebra para próxima linha
                linhas += 1
                largura_atual = palavra_largura
            else:
                largura_atual += palavra_largura
        
        # Adiciona uma linha extra para garantir espaço suficiente
        return max(1, linhas + 1)
    
    def definir_texto(self, novo_texto):
        """
        Define o texto e ajusta a altura automaticamente conforme a quebra de linha.
        """
        self.texto_original = novo_texto
        self.delete('1.0', tk.END)
        self.insert('1.0', novo_texto)
        
        # Chamar resize imediatamente
        self.resize()
        
        # Programar mais alguns resize com atraso crescente para garantir que ocorra após o layout completo
        self.after(50, self.resize)
        self.after(100, self.resize)
        self.after(300, self.resize)
