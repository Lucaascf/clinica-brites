from tkinter import ttk

def configurar_estilo_treeview(cores, fontes):
    """
    Configura um estilo melhorado para o Treeview
    
    Args:
        cores: Dicionário de cores do sistema
        fontes: Dicionário de fontes do sistema
    """
    estilo = ttk.Style()
    
    # Configuração básica do Treeview
    estilo.configure(
        "Treeview", 
        background=cores["secao_bg"],
        foreground=cores["texto"],
        rowheight=30,  # Linhas mais altas
        font=fontes["campo"],
        fieldbackground=cores["secao_bg"]
    )
    
    # Cabeçalhos
    estilo.configure(
        "Treeview.Heading", 
        background=cores["titulo_bg"],
        foreground=cores["texto_destaque"],
        font=fontes["campo_destaque"],
        relief="flat",
        padding=[5, 5]  # Mais espaço no cabeçalho
    )
    
    # Estilo para linha selecionada
    estilo.map("Treeview",
        background=[
            ('selected', cores["primaria"])  # Linha selecionada
        ],
        foreground=[
            ('selected', cores["texto_destaque"])  # Texto linha selecionada
        ]
    )
    
    return estilo

def alternar_cores_linhas(treeview, cor_impar='#f7fcfa', cor_par='#ffffff'):
    """
    Alterna as cores das linhas do Treeview
    
    Args:
        treeview: O widget Treeview
        cor_impar: Cor para linhas ímpares (verde muito suave)
        cor_par: Cor para linhas pares (branco)
    """
    # Função para atualizar as cores das linhas
    def atualizar_cores_linhas():
        # Limpar tags existentes
        for iid in treeview.get_children():
            treeview.item(iid, tags=())
        
        # Definir tags para linhas pares e ímpares
        for index, iid in enumerate(treeview.get_children()):
            if index % 2 == 0:  # Linha par
                treeview.item(iid, tags=('par',))
            else:  # Linha ímpar
                treeview.item(iid, tags=('impar',))
    
    # Configurar as tags de cor
    treeview.tag_configure('impar', background=cor_impar)
    treeview.tag_configure('par', background=cor_par)
    
    # Atualizar as cores inicialmente
    atualizar_cores_linhas()
    
    # Retornar a função para ser chamada após carregar novos dados
    return atualizar_cores_linhas