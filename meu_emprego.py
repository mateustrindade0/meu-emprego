# meu_emprego.py
"""
App Tkinter com tela inicial e formulário de cadastro.

Resumo:
- Usa MongoDB (se MEU_EMPREGO_MONGO_URI estiver definido) ou CSV como fallback.
- Formulário com 5+ campos e 3 tipos de widgets.
- Botão de teste de conexão na tela inicial.
"""

# EXPLICAÇÃO SIMPLES (para não-técnicos)
# -------------------------------------
# Este programa gerencia candidaturas (vagas/inscrições). Em linguagem simples:
# - Ele abre janelas para você digitar ou ver candidaturas.
# - Tenta salvar os dados em um banco na nuvem (MongoDB). Se não conseguir,
#   salva em um arquivo local chamado `candidaturas.csv`.
# - As telas principais são: Dashboard (resumo), Cadastro (formulário) e
#   Visualização (tabela). A parte dos gráficos no dashboard foi deixada como
#   placeholder para outro desenvolvedor implementar (veja `assets/GRAPH_GUIDE.md`).
#

import csv
import datetime
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=ROOT_DIR / ".env")
except Exception:
    pass

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:
    raise RuntimeError("Tkinter não está disponível no ambiente atual.")

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except Exception:
    PYMONGO_AVAILABLE = False

CSV_PATH = Path(os.environ.get("CANDIDATURAS_CSV_PATH", str(ROOT_DIR / "candidaturas.csv")))

MONGO_SCHEMA = {
    "collection": "candidaturas",
    "fields": {
        "empresa": {"type": "string", "required": True},
        "cargo": {"type": "string", "required": True},
        "data": {"type": "date", "required": True, "format": "YYYY-MM-DD"},
        "tipo": {"type": "string", "required": True, "enum": ["Presencial", "Remoto", "Híbrido"]},
        "status": {"type": "string", "required": True, "enum": ["Inscrito", "Entrevista", "Rejeitado", "Contratado"]},
        "observacoes": {"type": "string", "required": False}
    }
}

class DataStore:
    """Classe simples que encapsula persistência: MongoDB (se disponível) ou CSV."""
    def __init__(self, mongo_uri: str = None, db_name: str = "meu_emprego"):
        self.client = None
        self.db = None
        self.use_mongo = False
        if PYMONGO_AVAILABLE and mongo_uri:
            try:
                timeout_ms = int(os.environ.get("MEU_EMPREGO_MONGO_TIMEOUT_MS", "10000"))
                self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
                self.client.server_info()
                self.db = self.client[db_name]
                try:
                    coll = self.db[MONGO_SCHEMA["collection"]]
                    coll.create_index("data")
                except Exception:
                    pass
                self.use_mongo = True
            except Exception:
                self.client = None
                self.db = None
                self.use_mongo = False

    def test_connection(self):
        if not PYMONGO_AVAILABLE:
            return {"ok": False, "backend": "none", "msg": "pymongo não está instalado"}
        if not self.client:
            return {"ok": False, "backend": "none", "msg": "Nenhuma URI de Mongo fornecida ou cliente não inicializado"}
        try:
            info = self.client.server_info()
            return {"ok": True, "backend": "mongo", "msg": "Conectado ao MongoDB", "server": info.get("version")}
        except Exception as e:
            return {"ok": False, "backend": "mongo", "msg": f"Erro conectando: {e}"}

    def insert_candidatura(self, doc: dict):
        if self.use_mongo and self.db is not None:
            coll = self.db[MONGO_SCHEMA["collection"]]
            if isinstance(doc.get("data"), str):
                try:
                    doc["data"] = datetime.datetime.fromisoformat(doc["data"])
                except Exception:
                    pass
            res = coll.insert_one(doc)
            return {"ok": True, "id": str(res.inserted_id), "backend": "mongo"}
        else:
            created = not CSV_PATH.exists()
            with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if created:
                    writer.writerow(["empresa", "cargo", "data", "tipo", "status", "observacoes"])
                writer.writerow([
                    doc.get("empresa", ""),
                    doc.get("cargo", ""),
                    doc.get("data", ""),
                    doc.get("tipo", ""),
                    doc.get("status", ""),
                    doc.get("observacoes", ""),
                ])
            return {"ok": True, "backend": "csv"}

    def list_candidaturas(self, limit: int | None = None, order_by_date_desc: bool = True):
        """Retorna uma lista de candidaturas como dicionários prontos para exibição.

        Campos: empresa, cargo, data (YYYY-MM-DD), tipo, status, observacoes
        """
        items = []
        try:
            if self.use_mongo and self.db is not None:
                coll = self.db[MONGO_SCHEMA["collection"]]
                cursor = coll.find()
                if order_by_date_desc:
                    try:
                        cursor = cursor.sort("data", -1)
                    except Exception:
                        pass
                if limit:
                    cursor = cursor.limit(limit)
                for d in cursor:
                    data_val = d.get("data")
                    try:
                        if hasattr(data_val, "date"):
                            data_val = data_val.date().isoformat()
                        elif hasattr(data_val, "isoformat"):
                            data_val = data_val.isoformat()
                    except Exception:
                        data_val = str(data_val) if data_val is not None else ""
                    items.append({
                        "empresa": d.get("empresa", ""),
                        "cargo": d.get("cargo", ""),
                        "data": data_val or "",
                        "tipo": d.get("tipo", ""),
                        "status": d.get("status", ""),
                        "observacoes": d.get("observacoes", ""),
                    })
            else:
                # CSV
                if CSV_PATH.exists():
                    with CSV_PATH.open(newline="", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for d in reader:
                            items.append({
                                "empresa": d.get("empresa", ""),
                                "cargo": d.get("cargo", ""),
                                "data": d.get("data", ""),
                                "tipo": d.get("tipo", ""),
                                "status": d.get("status", ""),
                                "observacoes": d.get("observacoes", d.get("obs", "")),
                            })
                    # ordenação simples por data se possível
                    try:
                        items.sort(key=lambda x: x.get("data") or "", reverse=bool(order_by_date_desc))
                    except Exception:
                        pass
                if limit:
                    items = items[:limit]
        except Exception:
            # Em caso de erro silencioso, retorna lista acumulada até então
            pass
        return items

def main():
    mongo_uri = os.environ.get("MEU_EMPREGO_MONGO_URI")
    db_name = os.environ.get("MEU_EMPREGO_DB_NAME", "meu_emprego")
    ds = DataStore(mongo_uri=mongo_uri, db_name=db_name)

    try:
        if mongo_uri and not ds.use_mongo:
            msg = ""
            if not PYMONGO_AVAILABLE:
                msg = (
                    "O app encontrou MEU_EMPREGO_MONGO_URI, mas o driver pymongo não está instalado nesta execução.\n"
                    "Ative seu ambiente virtual ou instale as dependências conforme REQUIREMENTS.md.\n"
                    "Por enquanto, será usado o CSV (fallback)."
                )
            else:
                res = ds.test_connection()
                msg = (
                    "Não foi possível conectar ao MongoDB agora. O app vai usar CSV (fallback).\n\n"
                    f"Detalhe: {res.get('msg', 'sem detalhes')}"
                )
            root_temp = tk.Tk()
            root_temp.withdraw()
            messagebox.showwarning("Persistência em CSV", msg)
            root_temp.destroy()
    except Exception:
        pass

    import tkinter as tk  # garantir import local
    from assets.ui_style import apply_theme
    from assets.ui_windows import MainWindow

    root = tk.Tk()
    apply_theme(root)

    try:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        if sw >= 1920:
            w, h = int(sw * 0.7), int(sh * 0.7)
        elif sw >= 1366:
            w, h = int(sw * 0.65), int(sh * 0.65)
        elif sw >= 800:
            w, h = int(sw * 0.9), int(sh * 0.85)
        else:
            w, h = int(sw * 0.95), int(sh * 0.9)
        w = max(420, min(1400, w))
        h = max(300, min(1000, h))
        x = (sw - w) // 2
        y = (sh - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")
        try:
            scaling = max(0.8, min(2.0, sw / 1366))
            root.tk.call('tk', 'scaling', scaling)
        except Exception:
            pass
    except Exception:
        pass

    app = MainWindow(root, ds)
    root.mainloop()

if __name__ == "__main__":
    main()
