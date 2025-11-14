"""assets/ui_style.py
Centralized UI styling for Meu Emprego.

This module exposes a single function `apply_theme(root)` which applies a
clean ttk theme, configures base colors, fonts and useful style names.

Note: the application currently doesn't import this file automatically —
this file is provided as a single place to centralize styling. To use it,
call `from assets.ui_style import apply_theme; apply_theme(root)` from your
application startup code.
"""
from tkinter import ttk

try:
    # optional import; tkinter may not be present in headless test environments
    import tkinter as tk
    from tkinter import font as tkfont
except Exception:
    tk = None
    tkfont = None

# Simple color palette (adjust as needed)
PRIMARY = "#2b7cff"
PRIMARY_DARK = "#1a60d6"
BG = "#f7f9fc"
SURFACE = "#ffffff"
TEXT = "#222222"
MUTED = "#6b7280"


def apply_theme(root):
    """Apply a modest theme and style overrides to the given Tk root.

    Returns a dict with useful style objects (style, default_font, title_font).
    """
    if tk is None or tkfont is None:
        return {}

    style = ttk.Style(root)

    # try use a modern-ish theme if available
    for theme_name in ("clam", "alt", "default"):
        try:
            style.theme_use(theme_name)
            break
        except Exception:
            pass

    # base fonts
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=10)
    title_font = tkfont.Font(root=root, family=default_font.cget("family"), size=16, weight="bold")

    # configure general colors
    try:
        style.configure('.', background=BG, foreground=TEXT)
        style.configure('TFrame', background=BG)
        style.configure('TLabel', background=BG, foreground=TEXT)
        style.configure('TEntry', padding=6)

        # Buttons: padrão mais compacto e 'arredondado' visual (simulado com relief flat/borderwidth)
        style.configure('TButton', padding=6, relief='flat', background=PRIMARY, foreground='white', borderwidth=0)
        style.map('TButton',
                  foreground=[('disabled', MUTED), ('active', 'white')],
                  background=[('active', PRIMARY_DARK)])

        # Estilo 'arredondado' (visual) usado para botões de ação. True rounded corners require images
        # ou temas externos; aqui simulamos com borderwidth reduzido e fundo consistente.
        style.configure('Rounded.TButton', padding=6, relief='flat', background=PRIMARY, foreground='white', borderwidth=0)
        style.map('Rounded.TButton',
                  foreground=[('disabled', MUTED), ('active', 'white')],
                  background=[('active', PRIMARY_DARK)])

        # Small icon-style button used for connection test (compact)
        style.configure('Icon.TButton', padding=2, relief='flat', background=BG, foreground=TEXT, borderwidth=0)
        style.map('Icon.TButton', background=[('active', BG)])

        # Combobox
        style.configure('TCombobox', padding=4)

    except Exception:
        # ignore style configuration failures on unusual platforms
        pass

    return {
        'style': style,
        'default_font': default_font,
        'title_font': title_font,
        'colors': {
            'primary': PRIMARY,
            'primary_dark': PRIMARY_DARK,
            'bg': BG,
            'surface': SURFACE,
            'text': TEXT,
            'muted': MUTED,
        }
    }
