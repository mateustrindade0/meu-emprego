"""meu_emprego.py
App Tkinter com tela inicial e formulário de cadastro.

Resumo:
- Usa MongoDB (se MEU_EMPREGO_MONGO_URI estiver definido) ou CSV como fallback.
- Formulário com 5+ campos e 3 tipos de widgets.
- Botão de teste de conexão na tela inicial.
"""

import csv
import datetime
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent

# carregar .env se disponível (opcional) a partir da raiz do projeto
try:
	from dotenv import load_dotenv
	load_dotenv(dotenv_path=ROOT_DIR / ".env")
except Exception:
	# python-dotenv não está instalado; as variáveis de ambiente ainda podem ser fornecidas externamente
	pass

try:
	import tkinter as tk
	from tkinter import messagebox
	from tkinter import ttk
except Exception:
	raise RuntimeError("Tkinter não está disponível no ambiente atual.")

try:
	from pymongo import MongoClient
	PYMONGO_AVAILABLE = True
except Exception:
	PYMONGO_AVAILABLE = False

CSV_PATH = Path(os.environ.get("CANDIDATURAS_CSV_PATH", str(ROOT_DIR / "candidaturas.csv")))

# Schema recomendado para MongoDB (apenas documentação / referência)
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
				# usar timeout maior para evitar falhas em redes lentas
				timeout_ms = int(os.environ.get("MEU_EMPREGO_MONGO_TIMEOUT_MS", "10000"))
				self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
				# Forçar uma ação que confirme a conexão
				self.client.server_info()
				self.db = self.client[db_name]
				# Garantir que a coleção existe e criar índices úteis (se possível)
				try:
					coll = self.db[MONGO_SCHEMA["collection"]]
					# criar índice simples na data para acelerar consultas por data
					coll.create_index("data")
				except Exception:
					# se algo falhar na criação de índices, continuamos sem interromper
					pass
				self.use_mongo = True
			except Exception:
				# Falha ao conectar — caímos para CSV
				self.client = None
				self.db = None
				self.use_mongo = False

	def test_connection(self):
		"""Testa a conexão com o MongoDB e retorna um dicionário com o resultado."""
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
		"""Insere documento na coleção `candidaturas` (Mongo) ou append no CSV."""
		if self.use_mongo and self.db is not None:
			coll = self.db[MONGO_SCHEMA["collection"]]
			# Converter data para datetime em caso de string
			if isinstance(doc.get("data"), str):
				try:
					doc["data"] = datetime.datetime.fromisoformat(doc["data"])  # armazena como datetime
				except Exception:
					pass
			res = coll.insert_one(doc)
			return {"ok": True, "id": str(res.inserted_id), "backend": "mongo"}
		else:
			# Assegurar que o CSV existe e tem cabeçalho
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


class MeuEmpregoApp:
	def __init__(self, root: tk.Tk, datastore: DataStore):
		self.root = root
		self.root.title("Meu Emprego – Painel Inicial")
		self.datastore = datastore
		self._build_main()

	def _build_main(self):
		frm = ttk.Frame(self.root, padding=16)
		frm.grid()

		ttk.Label(frm, text="Meu Emprego", font=(None, 18, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 10))

		# Indicador do backend
		backend = "MongoDB" if self.datastore.use_mongo else "CSV (fallback)"
		ttk.Label(frm, text=f"Persistência: {backend}").grid(column=0, row=1, columnspan=2, pady=(0, 8))

		ttk.Button(frm, text="Cadastrar candidatura", command=self.open_cadastro).grid(column=0, row=2, sticky="ew", padx=5, pady=5)
		ttk.Button(frm, text="Visualizar registros", command=self._not_implemented).grid(column=1, row=2, sticky="ew", padx=5, pady=5)
		ttk.Button(frm, text="Análise (gráficos)", command=self._not_implemented).grid(column=0, row=3, columnspan=2, sticky="ew", padx=5, pady=5)
		# Botão de teste: ícone pequeno no canto inferior direito (mais discreto)
		test_btn = ttk.Button(frm, text="🔌", width=3, command=self._on_test_connection)
		test_btn.grid(column=1, row=5, sticky="e", padx=5, pady=(8,0))

		ttk.Label(frm, text="Clique em 'Cadastrar candidatura' para começar.", wraplength=360).grid(column=0, row=4, columnspan=2, pady=(10, 0))

	def _not_implemented(self):
		messagebox.showinfo("Atenção", "Funcionalidade ainda não implementada nesta iteração.")

	def open_cadastro(self):
		CadastroWindow(self.root, self.datastore)

	def _on_test_connection(self):
		res = self.datastore.test_connection()
		if res.get("ok"):
			ver = res.get("server")
			messagebox.showinfo("Conexão", f"Conectado ao MongoDB {ver}")
		else:
			messagebox.showerror("Conexão", f"Falha: {res.get('msg')}")


class CadastroWindow:
	"""Janela de cadastro com pelo menos 5 campos e 3 tipos diferentes de widgets."""

	def __init__(self, master: tk.Tk, datastore: DataStore):
		self.top = tk.Toplevel(master)
		self.top.title("Cadastrar Candidatura")
		self.datastore = datastore
		self._build()

	def _build(self):
		frm = ttk.Frame(self.top, padding=12)
		frm.grid()

		# Campo 1: Empresa (Entry)
		ttk.Label(frm, text="Empresa:").grid(column=0, row=0, sticky="w")
		self.empresa_var = tk.StringVar()
		ttk.Entry(frm, textvariable=self.empresa_var, width=40).grid(column=1, row=0)

		# Campo 2: Cargo (Entry)
		ttk.Label(frm, text="Cargo:").grid(column=0, row=1, sticky="w")
		self.cargo_var = tk.StringVar()
		ttk.Entry(frm, textvariable=self.cargo_var, width=40).grid(column=1, row=1)

		# Campo 3: Data (Entry) — texto simples com placeholder de ISO
		ttk.Label(frm, text="Data (YYYY-MM-DD):").grid(column=0, row=2, sticky="w")
		self.data_var = tk.StringVar(value=datetime.date.today().isoformat())
		ttk.Entry(frm, textvariable=self.data_var, width=20).grid(column=1, row=2, sticky="w")

		# Campo 4: Tipo (Combobox) — exemplo de widget diferente
		ttk.Label(frm, text="Tipo:").grid(column=0, row=3, sticky="w")
		self.tipo_var = tk.StringVar()
		tipos = ["Presencial", "Remoto", "Híbrido"]
		ttk.Combobox(frm, textvariable=self.tipo_var, values=tipos, state="readonly").grid(column=1, row=3, sticky="w")

		# Campo 5: Status (Radiobuttons) — outro tipo de widget
		ttk.Label(frm, text="Status:").grid(column=0, row=4, sticky="nw")
		self.status_var = tk.StringVar(value="Inscrito")
		status_frame = ttk.Frame(frm)
		status_frame.grid(column=1, row=4, sticky="w")
		for s in ["Inscrito", "Entrevista", "Rejeitado", "Contratado"]:
			ttk.Radiobutton(status_frame, text=s, variable=self.status_var, value=s).pack(side="left", padx=2)

		# Campo 6: Observações (Text) — 6º campo opcional, demonstra outro widget
		ttk.Label(frm, text="Observações:").grid(column=0, row=5, sticky="nw")
		self.obs_text = tk.Text(frm, width=40, height=4)
		self.obs_text.grid(column=1, row=5)

		btn_frame = ttk.Frame(frm)
		btn_frame.grid(column=0, row=6, columnspan=2, pady=(8, 0))
		ttk.Button(btn_frame, text="Salvar", command=self.on_submit).pack(side="left", padx=4)
		ttk.Button(btn_frame, text="Fechar", command=self.top.destroy).pack(side="left", padx=4)

	def on_submit(self):
		doc = {
			"empresa": self.empresa_var.get().strip(),
			"cargo": self.cargo_var.get().strip(),
			"data": self.data_var.get().strip(),
			"tipo": self.tipo_var.get().strip(),
			"status": self.status_var.get().strip(),
			"observacoes": self.obs_text.get("1.0", "end").strip(),
		}
		# Validações básicas
		if not doc["empresa"] or not doc["cargo"]:
			messagebox.showwarning("Validação", "Preencha pelo menos Empresa e Cargo.")
			return
		# Validar data simples
		try:
			datetime.date.fromisoformat(doc["data"])  # levanta se inválido
		except Exception:
			messagebox.showwarning("Validação", "Data inválida. Use o formato YYYY-MM-DD.")
			return

		res = self.datastore.insert_candidatura(doc)
		if res.get("ok"):
			messagebox.showinfo("Sucesso", f"Registro salvo ({res.get('backend')}).")
			self.top.destroy()
		else:
			messagebox.showerror("Erro", "Falha ao salvar o registro.")


def main():
	# Tentativa de conectar ao MongoDB se variável de ambiente estiver definida
	mongo_uri = os.environ.get("MEU_EMPREGO_MONGO_URI")
	db_name = os.environ.get("MEU_EMPREGO_DB_NAME", "meu_emprego")
	ds = DataStore(mongo_uri=mongo_uri, db_name=db_name)

	# Aviso proativo: .env/URI presente mas Mongo não está ativo (pymongo ausente ou conexão falhou)
	try:
		# Inicializa uma root temporária apenas para exibir alerta antes da janela principal
		if mongo_uri and not ds.use_mongo:
			# Tentar obter mais contexto
			msg = ""
			if not PYMONGO_AVAILABLE:
				msg = (
					"O app encontrou MEU_EMPREGO_MONGO_URI, mas o driver pymongo não está instalado nesta execução.\n"
					"Ative seu ambiente virtual (venv) ou instale as dependências conforme REQUIREMENTS.md.\n"
					"Por enquanto, será usado o CSV (fallback)."
				)
			else:
				# pymongo existe, mas a conexão pode ter falhado (timeout/URI inválida/rede)
				res = ds.test_connection()
				msg = (
					"Não foi possível conectar ao MongoDB agora. O app vai usar CSV (fallback).\n\n"
					f"Detalhe: {res.get('msg', 'sem detalhes')}"
				)
			# Mostrar um alerta não-bloqueante antes da janela principal
			_root = tk.Tk()
			_root.withdraw()
			messagebox.showwarning("Persistência em CSV", msg)
			_root.destroy()
	except Exception:
		# Qualquer falha nessa notificação não deve impedir o app de abrir
		pass

	root = tk.Tk()
	app = MeuEmpregoApp(root, ds)
	root.mainloop()


if __name__ == "__main__":
	main()

