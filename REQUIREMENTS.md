Requisitos e instruções de instalação — Meu Emprego

Este arquivo descreve as dependências e passos recomendados para preparar o ambiente e rodar a aplicação `meu_emprego.py`.

1) Requisitos do sistema (Linux - Debian/Ubuntu/Mint)
- Python 3.8+ (recomendado 3.10+)
- python3-pip (se não tiver, instale: `sudo apt install python3-pip`)
- python3-venv (para criar ambientes virtuais: `sudo apt install python3-venv`)
- pacote do Tkinter para GUI (se não tiver):
  - Debian/Ubuntu/Mint: `sudo apt install python3-tk`

2) Recomendações: usar virtualenv (isolamento)
No diretório do projeto rode:

```bash
# cria venv
python3 -m venv .venv
# ativa (Linux/macOS)
source .venv/bin/activate
# atualiza pip
python -m pip install --upgrade pip setuptools wheel
```

Se ocorrer erro com `python` dentro do venv, use o executável do venv explicitamente:
```
.venv/bin/python -m pip install --upgrade pip setuptools wheel
```

3) Instalar dependências Python (arquivo `requirements.txt`)
Com o venv ativado executo:

```bash
pip install -r requirements.txt
```

Isso instala:
- python-dotenv: carrega variáveis do `.env` para `os.environ`.
- pymongo: driver do MongoDB para Python.
- dnspython: necessário para suportar URIs `mongodb+srv` (usado pelo Atlas).

Observação: se preferir instalar apenas o necessário:
```bash
pip install "pymongo" python-dotenv dnspython
```

4) Dependência opcional (gráficos)
- Matplotlib é usada apenas para a tela de análise (ainda não implementada nesta iteração).
- Para instalar: `pip install matplotlib`

5) Verificações rápidas
Após instalar, confirme:

```bash
python -c "import pymongo, dotenv; print('pymongo', pymongo.__version__); print('dotenv ok')"
```

6) Configurar `.env`
- Copie `.env.example` para `.env` e preencha `MEU_EMPREGO_MONGO_URI` com a connection string do Atlas.
- Exemplo (não commit):
```
MEU_EMPREGO_MONGO_URI="mongodb+srv://usuario:senha@clusterdev.bsjig.mongodb.net/?appName=ClusterDev"
MEU_EMPREGO_DB_NAME="meu_emprego"
CANDIDATURAS_CSV_PATH="candidaturas.csv"
```

7) Rodar a aplicação
Com o venv ativado:

```bash
python3 meu_emprego.py
```

Dica: se preferir não ativar o venv, use o binário direto:
```
.venv/bin/python meu_emprego.py
```

8) Problemas comuns
- `pip: command not found`: instale `python3-pip` ou use `python3 -m pip`.
- `ModuleNotFoundError: No module named 'pymongo'`: provavelmente está instalando no sistema Python diferente. Garanta que está usando o venv correto ou use `.venv/bin/python -m pip install pymongo`.
- `Tkinter não está disponível`: instale `python3-tk` pelo gerenciador de pacotes do sistema.

9) Notas finais
- Não versionar `.env` (arquivo já listado em `.gitignore`).
- Para deploy/prod use mecanismos secretos do ambiente (Docker secrets, CI/CD variables) em vez de `.env`.



Sequência curta (copie/cole cada bloco na ordem, dentro da pasta do projeto)

1.Verificar o Python do venv e o pip

.venv/bin/python --version
.venv/bin/python -m pip --version.

2.Garantir dependências (faça isso só se não tiver feito antes ou após recriar o venv)

.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -r requirements.txt.

3.Conferir rapidamente o .env (ver se a URI está definida)
grep -E '^MEU_EMPREGO_MONGO_URI' .env || echo "MEU_EMPREGO_MONGO_URI not set in .env"
# opcional: ver primeiras linhas
sed -n '1,40p' .env.

4.Teste rápido de conexão (não abre GUI) — mostra se vai usar Mongo ou CSV

.venv/bin/python - <<'PY'
from dotenv import load_dotenv
import os
from meu_emprego import DataStore
load_dotenv(dotenv_path='.env')
mongo_uri = os.environ.get('MEU_EMPREGO_MONGO_URI')
ds = DataStore(mongo_uri=mongo_uri, db_name=os.environ.get('MEU_EMPREGO_DB_NAME','meu_emprego'))
print('use_mongo:', ds.use_mongo)
print('test_connection:', ds.test_connection())
PY .

Se use_mongo: True e test_connection() retornar ok, você está pronto para salvar no DB.
Se use_mongo: False, confira output (pymongo ausente ou erro de conexão); verifique passo 2/3.
Rodar a GUI (use o mesmo Python do venv)

5. Rodar a GUI (use o mesmo Python do venv)

.venv/bin/python meu_emprego.py.





CASO QUEIRA INSERIR UM REGISTRO DE TESTE SEM ABRIR A GUI USE ISSO.


.venv/bin/python - <<'PY'
from dotenv import load_dotenv
import os
from meu_emprego import DataStore
load_dotenv(dotenv_path='.env')
ds = DataStore(mongo_uri=os.environ.get('MEU_EMPREGO_MONGO_URI'), db_name=os.environ.get('MEU_EMPREGO_DB_NAME','meu_emprego'))
print('use_mongo:', ds.use_mongo)
if ds.use_mongo:
    print(ds.insert_candidatura({
        "empresa":"TesteAutomático",
        "cargo":"Dev Teste",
        "data":"2025-11-13",
        "tipo":"Remoto",
        "status":"Inscrito",
        "observacoes":"inserção automática para teste"
    }))
else:
    print('Fallback CSV')
PY


ou python - <<'PY'
from dotenv import load_dotenv
import os
from meu_emprego import DataStore
load_dotenv(dotenv_path='.env')
ds = DataStore(mongo_uri=os.environ.get('MEU_EMPREGO_MONGO_URI'),
               db_name=os.environ.get('MEU_EMPREGO_DB_NAME','meu_emprego'))
print('use_mongo:', ds.use_mongo)
print('test_connection:', ds.test_connection())
if ds.use_mongo:
    print(ds.insert_candidatura({"empresa":"TesteOps1","cargo":"Dev","data":"2025-11-13","tipo":"Remoto","status":"Inscrito","observacoes":"teste opcao1"}))
else:
    print('Fallback CSV')
PY

# rodar GUI (com venv ativado)
python meu_emprego.py