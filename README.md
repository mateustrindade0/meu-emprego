# Meu Emprego – Sistema de Cadastro de Candidaturas

Aplicação desktop simples em Python/Tkinter para registrar candidaturas (empresa, cargo, data, tipo, status, observações).

Principais pontos:
- Persistência principal: MongoDB (se configurado via `.env`).
- Fallback: arquivo CSV `candidaturas.csv` quando o Mongo não estiver disponível.

## Como rodar (resumido)

Recomendo sempre usar o ambiente virtual (`.venv`) que está no projeto. Existem duas formas claras de executar — opção 1 é a recomendada.

### Opção 1 — Recomendado: ativar o venv e rodar (modo interativo)

1. Criar (se necessário) e ativar o venv, instalar dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

2. Verificar `.env` (preencher `MEU_EMPREGO_MONGO_URI` se for usar Atlas):

```bash
cat .env
# procure a linha MEU_EMPREGO_MONGO_URI
```

3. Rodar a aplicação GUI:

```bash
python meu_emprego.py
```

Na tela inicial clique em "Testar conexão" para confirmar que a aplicação está usando MongoDB antes de salvar registros.

### Opção 2 — Alternativa (sem ativar o venv): usar o binário do venv diretamente

Se preferir não ativar o venv, use o binário que já existe em `.venv/bin/python` (útil quando `activate` não está presente):

```bash
.venv/bin/python -m pip install --upgrade pip setuptools wheel
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python meu_emprego.py
```

### Teste rápido (sem abrir GUI)

Roda um snippet que carrega o `.env`, testa a conexão e informa se o app usará Mongo ou CSV:

```bash
.venv/bin/python - <<'PY'
from dotenv import load_dotenv
import os
from meu_emprego import DataStore
load_dotenv(dotenv_path='.env')
ds = DataStore(mongo_uri=os.environ.get('MEU_EMPREGO_MONGO_URI'), db_name=os.environ.get('MEU_EMPREGO_DB_NAME','meu_emprego'))
print('use_mongo:', ds.use_mongo)
print('test_connection:', ds.test_connection())
PY
```

Se `use_mongo: True` e `test_connection()` retornar ok, a GUI gravará no MongoDB.

## Verificando no MongoDB Compass

- Abra o Compass e conecte ao mesmo cluster/URI usado em `.env`.
- Procure o database `MEU_EMPREGO_DB_NAME` (por padrão `meu_emprego`) e a collection `candidaturas`.
- Registros inseridos pela aplicação devem aparecer aí.

## Observações rápidas

- Mensagem sobre `/home/.../.deno/envexport` vem do seu arquivo de configuração do shell e não afeta o app; remova a linha que tenta dar `source` se quiser parar de ver a mensagem.
- Se a aplicação estiver salvando em CSV, normalmente é porque o Python que foi usado para executar não tinha `pymongo` instalado ou a conexão ao Mongo falhou. Use o binário do `.venv` mostrado acima para garantir consistência.

Se quiser, posso adicionar um script `run.sh` que automatize os passos de verificação e só abra a GUI quando a conexão estiver OK — quer que eu o adicione?
