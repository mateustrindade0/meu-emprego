# assets/ui_components.py
"""
Componentes reutilizáveis de UI para o app “Meu Emprego”.

Aqui definimos classes e funções que abstraem widgets ou frames comuns para facilitar
as futuras telas.
"""

import tkinter as tk
from tkinter import ttk

class BaseFrame(ttk.Frame):
    """Frame base com padding e configuração padrão."""
    def __init__(self, master=None, padding=12, **kwargs):
        super().__init__(master, padding=padding, **kwargs)
        self.columnconfigure(0, weight=1)

def InfoLabel(master, text, **kwargs):
    """Cria um label com estilo de informação comum."""
    lbl = ttk.Label(master, text=text, **kwargs)
    return lbl

def ActionButton(master, text, command, width: int | None = 14, style: str = 'Rounded.TButton', **kwargs):
    """Botão de ação estilizado.

    Parâmetros adicionais:
    - width: largura em caracteres (padrão 18, pode ser menor)
    - style: nome do estilo ttk a usar (padrão 'Rounded.TButton')
    """
    params = dict(text=text, command=command, style=style, **kwargs)
    if width is not None:
        params['width'] = width
    btn = ttk.Button(master, **params)
    return btn
