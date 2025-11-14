# assets/ui_windows.py
"""
Definição das janelas/telas da aplicação “Meu Emprego”.

Classes:
- MainWindow: Tela principal (Painel Inicial)
- CadastroWindow: Tela de cadastro de candidatura
- (Placeholders para VisualizacaoWindow e AnaliseWindow)
"""

# Nota ao implementador de gráficos
# --------------------------------
# A área de gráficos do `MainWindow` foi intencionalmente deixada como
# placeholder para que outro desenvolvedor (responsável pela análise)
# implemente os gráficos. Há um guia técnico em `assets/GRAPH_GUIDE.md`
# que descreve passo-a-passo como:
#  - obter os dados via `DataStore.list_candidaturas()`;
#  - gerar gráficos com matplotlib (barras/pizza/linhas);
#  - embuti-los no Tkinter com `FigureCanvasTkAgg` e gerenciar resize;
#  - atualizar `requirements.txt` e adicionar testes simples.
#
# Dentro do arquivo, procure o bloco que monta `right = ttk.Frame(...)`
# e o `placeholder_text` — substitua esse bloco pelo código de plot
# seguindo o guia quando for implementar.


import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from assets.ui_style import apply_theme
from assets.ui_components import BaseFrame, InfoLabel, ActionButton

# Import DataStore será feito no módulo principal, ou podemos importar opcionalmente aqui
# do meu_emprego import DataStore

class MainWindow:
    """Tela principal – Painel Inicial."""
    def __init__(self, root, datastore):
        self.root = root
        self.datastore = datastore
        self.root.title("Meu Emprego – Painel Inicial")
        try:
            self.root.minsize(420, 300)
        except Exception:
            pass

        # Setup de responsividade — se quiser, pode mover esse bloco para BaseFrame
        self.default_font = None
        self.title_font = None
        try:
            import tkinter.font as tkfont
            self.default_font = tkfont.nametofont("TkDefaultFont")
            self.title_font = tkfont.Font(root=self.root, family=self.default_font.cget("family"),
                                           size=18, weight="bold")
        except Exception:
            pass

        self._build_main()
        # controle de resize (debounce + guardas para evitar loop de realocação)
        self._resize_after = None
        self._last_w = None
        self._last_h = None
        self._last_title_sz = None
        self.root.bind('<Configure>', self._on_root_resize)

    def _build_main(self):
        # Dashboard container
        frm = BaseFrame(self.root, padding=16)
        frm.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=2)

        # Header / título
        if self.title_font:
            ttk.Label(frm, text="Meu Emprego", font=self.title_font).grid(column=0, row=0,
                                                                             sticky="w", pady=(0,6))
        else:
            ttk.Label(frm, text="Meu Emprego", font=(None,18,"bold")).grid(column=0, row=0,
                                                                             sticky="w", pady=(0,6))

        backend = "MongoDB" if self.datastore.use_mongo else "CSV (fallback)"
        InfoLabel(frm, text=f"Persistência: {backend}").grid(column=0, row=1, sticky="w", pady=(0,8))

        # Test connection button (small icon) at top-right
        test_btn = ttk.Button(frm, text="🔌", width=3, command=self._on_test_connection, style="Icon.TButton")
        test_btn.grid(column=1, row=0, rowspan=2, sticky="ne", padx=4, pady=0)

        # Main content: left = cards + actions, right = gráficos (placeholder)
        content = ttk.Frame(frm)
        content.grid(column=0, row=2, columnspan=2, sticky="nsew", pady=(8,0))
        frm.rowconfigure(2, weight=1)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        # Left column: resumo rápido e botões de ação
        left = ttk.Frame(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        left.columnconfigure(0, weight=1)

        # Card: total de candidaturas (se disponível)
        total = 0
        try:
            total = len(self.datastore.list_candidaturas() or [])
        except Exception:
            total = 0
        InfoLabel(left, text=f"Total de candidaturas: {total}").grid(row=0, column=0, sticky="ew", pady=(0,8))

        # Ações principais (mantendo estilos compactos)
        ActionButton(left, text="Cadastrar novas vagas", command=self.open_cadastro, width=14).grid(row=1, column=0, sticky="ew", pady=4)
        ActionButton(left, text="Visualizar registros", command=self.open_visualizacao, width=14).grid(row=2, column=0, sticky="ew", pady=4)

        # Right column: área reservada para gráficos (placeholder)
        right = ttk.Frame(content, borderwidth=1, relief="solid")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        placeholder_text = (
            "Área reservada para gráficos\n\n"
            "(Responsável: Matheus)\n\n"
            "Instruções: usar `DataStore.list_candidaturas()` para obter os dados e\n"
            "embutir gráficos via matplotlib + FigureCanvasTkAgg."
        )
        InfoLabel(right, text=placeholder_text, justify="center", wraplength=420).grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

    def _on_root_resize(self, event=None):
        if self._resize_after:
            try:
                self.root.after_cancel(self._resize_after)
            except Exception:
                pass
        self._resize_after = self.root.after(120, lambda: self._apply_responsive(event))

    def _apply_responsive(self, event=None):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if not w or not h:
            return
        # guarda para evitar recalcular em mudanças muito pequenas
        if self._last_w is not None and self._last_h is not None:
            if abs(w - self._last_w) < 24 and abs(h - self._last_h) < 24:
                return
        self._last_w, self._last_h = w, h

        # Escala somente o título (não alteramos TkDefaultFont em runtime para evitar loops)
        if self.title_font:
            new_title_size = max(12, int(18 * max(0.6, min(2.0, w / 480))))
            if new_title_size != self._last_title_sz:
                try:
                    self.title_font.configure(size=new_title_size)
                    self._last_title_sz = new_title_size
                except Exception:
                    pass

    def _on_test_connection(self):
        res = self.datastore.test_connection()
        if res.get("ok"):
            ver = res.get("server")
            messagebox.showinfo("Conexão", f"Conectado ao MongoDB {ver}")
        else:
            messagebox.showerror("Conexão", f"Falha: {res.get('msg')}")

    def open_cadastro(self):
        CadastroWindow(self.root, self.datastore)

    def open_visualizacao(self):
        VisualizacaoWindow(self.root, self.datastore)

    def open_analise(self):
        # futura implementação
        messagebox.showinfo("Em desenvolvimento", "Tela de Análise ainda não implementada.")

class CadastroWindow:
    """Janela de cadastro com pelo menos 5 campos e 3 tipos diferentes de widgets."""
    def __init__(self, master, datastore):
        self.top = tk.Toplevel(master)
        self.top.title("Cadastrar Candidatura")
        try:
            self.top.minsize(520, 380)
        except Exception:
            pass

        try:
            import tkinter.font as tkfont
            self.top_default_font = tkfont.nametofont("TkDefaultFont")
        except Exception:
            self.top_default_font = None
        self._top_resize_after = None
        self.top.bind('<Configure>', self._on_top_resize)
        self.datastore = datastore
        self._build()

    def _build(self):
        frm = BaseFrame(self.top, padding=12)
        frm.grid(sticky="nsew")
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(5, weight=1)

        ttk.Label(frm, text="Empresa:").grid(column=0, row=0, sticky="w")
        self.empresa_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.empresa_var, width=40).grid(column=1, row=0, sticky="ew")

        ttk.Label(frm, text="Cargo:").grid(column=0, row=1, sticky="w")
        self.cargo_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.cargo_var, width=40).grid(column=1, row=1, sticky="ew")

        ttk.Label(frm, text="Data (YYYY-MM-DD):").grid(column=0, row=2, sticky="w")
        self.data_var = tk.StringVar(value=datetime.date.today().isoformat())
        ttk.Entry(frm, textvariable=self.data_var, width=20).grid(column=1, row=2, sticky="w")

        ttk.Label(frm, text="Tipo:").grid(column=0, row=3, sticky="w")
        self.tipo_var = tk.StringVar()
        tipos = ["Presencial", "Remoto", "Híbrido"]
        ttk.Combobox(frm, textvariable=self.tipo_var, values=tipos, state="readonly").grid(column=1, row=3, sticky="ew")

        ttk.Label(frm, text="Status:").grid(column=0, row=4, sticky="nw")
        self.status_var = tk.StringVar(value="Inscrito")
        status_frame = ttk.Frame(frm)
        status_frame.grid(column=1, row=4, sticky="w")
        for s in ["Inscrito", "Entrevista", "Rejeitado", "Contratado"]:
            ttk.Radiobutton(status_frame, text=s, variable=self.status_var, value=s).pack(side="left", padx=2)

        ttk.Label(frm, text="Observações:").grid(column=0, row=5, sticky="nw")
        self.obs_text = tk.Text(frm, width=40, height=4)
        self.obs_text.grid(column=1, row=5, sticky="nsew")

        self.btn_frame = ttk.Frame(frm)
        self.btn_frame.grid(column=0, row=6, columnspan=2, pady=(8,0), sticky="e")

        ttk.Button(self.btn_frame, text="Salvar", command=self.on_submit).pack(side="left", padx=4)
        ttk.Button(self.btn_frame, text="Fechar", command=self.top.destroy).pack(side="left", padx=4)

    def _on_top_resize(self, event=None):
        if self._top_resize_after:
            try:
                self.top.after_cancel(self._top_resize_after)
            except Exception:
                pass
        self._top_resize_after = self.top.after(120, lambda: self._apply_responsive_top(event))

    def _apply_responsive_top(self, event=None):
        # Janela de cadastro: não alteramos fontes/wraplength em tempo real
        # para evitar ciclos de redimensionamento. Mantemos apenas a
        # responsividade de grid definida no _build().
        return

    def on_submit(self):
        doc = {
            "empresa": self.empresa_var.get().strip(),
            "cargo": self.cargo_var.get().strip(),
            "data": self.data_var.get().strip(),
            "tipo": self.tipo_var.get().strip(),
            "status": self.status_var.get().strip(),
            "observacoes": self.obs_text.get("1.0", "end").strip(),
        }
        if not doc["empresa"] or not doc["cargo"]:
            messagebox.showwarning("Validação", "Preencha pelo menos Empresa e Cargo.")
            return
        try:
            datetime.date.fromisoformat(doc["data"])
        except Exception:
            messagebox.showwarning("Validação", "Data inválida. Use o formato YYYY-MM-DD.")
            return

        res = self.datastore.insert_candidatura(doc)
        if res.get("ok"):
            messagebox.showinfo("Sucesso", f"Registro salvo ({res.get('backend')}).")
            self.top.destroy()
        else:
            messagebox.showerror("Erro", "Falha ao salvar o registro.")


class VisualizacaoWindow:
    """Janela de visualização de registros salvos (MongoDB ou CSV)."""
    def __init__(self, master, datastore):
        self.top = tk.Toplevel(master)
        self.top.title("Visualizar Candidaturas")
        try:
            self.top.minsize(700, 420)
        except Exception:
            pass

        self.datastore = datastore

        container = BaseFrame(self.top, padding=12)
        container.grid(sticky="nsew")
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        # Header
        backend = "MongoDB" if self.datastore.use_mongo else "CSV (fallback)"
        InfoLabel(container, text=f"Fonte de dados: {backend}").grid(row=0, column=0, sticky="w", pady=(0,8))

        # Tabela
        cols = ("empresa", "cargo", "data", "tipo", "status", "observacoes")
        self.tree = ttk.Treeview(container, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
        self.tree.column("empresa", width=160, anchor="w")
        self.tree.column("cargo", width=140, anchor="w")
        self.tree.column("data", width=110, anchor="center")
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("observacoes", width=260, anchor="w")

        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")

        # Ações
        btns = ttk.Frame(container)
        btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8,0))
        ttk.Button(btns, text="Atualizar", command=self._load_data).pack(side="left", padx=4)
        ttk.Button(btns, text="Fechar", command=self.top.destroy).pack(side="left", padx=4)

        self._load_data()

    def _load_data(self):
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            records = []
            # Preferir listar via DataStore, caso exista método; caso contrário, tentar caminhos diretos
            if hasattr(self.datastore, "list_candidaturas"):
                records = self.datastore.list_candidaturas()
            else:
                # Fallback leve: tentar pelo Mongo ou CSV mínimo
                if getattr(self.datastore, "use_mongo", False) and getattr(self.datastore, "db", None) is not None:
                    coll = self.datastore.db.get_collection("candidaturas")
                    records = list(coll.find())
                else:
                    import csv
                    from pathlib import Path
                    import os
                    csv_path = Path(os.environ.get("CANDIDATURAS_CSV_PATH", "candidaturas.csv"))
                    if csv_path.exists():
                        with csv_path.open(newline="", encoding="utf-8") as f:
                            reader = csv.DictReader(f)
                            records = list(reader)

            for r in records:
                empresa = r.get("empresa", "")
                cargo = r.get("cargo", "")
                data = r.get("data", "")
                # normalizar data caso venha datetime
                try:
                    if hasattr(data, "isoformat"):
                        data = data.date().isoformat() if hasattr(data, "date") else data.isoformat()
                except Exception:
                    pass
                tipo = r.get("tipo", "")
                status = r.get("status", "")
                obs = r.get("observacoes", r.get("obs", ""))
                self.tree.insert("", "end", values=(empresa, cargo, data, tipo, status, obs))
        except Exception as e:
            messagebox.showerror("Erro ao carregar", f"Não foi possível carregar os dados.\n{e}")
