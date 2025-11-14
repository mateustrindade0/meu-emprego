# Guia para implementação dos gráficos (Dashboard)

Este documento destina-se ao desenvolvedor encarregado de implementar a área de
análise/gráficos no dashboard da aplicação `Meu Emprego`.

Objetivo
--------
- Fornecer instruções claras e um snippet de exemplo para embutir gráficos
  Matplotlib dentro do `MainWindow` usando `FigureCanvasTkAgg`.
- Orientar sobre pré-requisitos, manipulação de dados e boas práticas de
  responsividade.

Dependências
------------
- Adicionar `matplotlib` nas dependências do projeto (ex.: `requirements.txt`):

```text
matplotlib>=3.0
```

- Instalar no ambiente:

```bash
.venv/bin/python -m pip install matplotlib
```

Fluxo de dados
--------------
- Use o método `DataStore.list_candidaturas()` fornecido em `meu_emprego.py`.
  Ele retorna uma lista de dicionários com campos: `empresa`, `cargo`, `data`,
  `tipo`, `status`, `observacoes`.
- Normalize e agrupe os dados para o tipo de gráfico desejado. Ex.: contar por
  `status` para um gráfico de barras.

Exemplo de snippet (barras) — como incorporar no `MainWindow`
-----------------------------------------------------------
Insira esse tipo de código no lugar do placeholder do painel direito.

```python
# imports necessários dentro do módulo que monta a UI
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import collections

# função de utilidade dentro da classe MainWindow
def _build_status_chart(self, parent_frame):
    # 1) coletar dados
    records = self.datastore.list_candidaturas()
    if not records:
        # mostrar mensagem ou retornar
        return None

    # 2) agrupar por status
    counts = collections.Counter(r.get('status','') or 'Indefinido' for r in records)
    labels = list(counts.keys())
    values = [counts[l] for l in labels]

    # 3) criar figura matplotlib
    fig = Figure(figsize=(4,3), dpi=100)
    ax = fig.add_subplot(111)
    ax.bar(labels, values, color=['#2b7cff','#1a60d6','#f7c6c6','#a5d6a7'])
    ax.set_title('Candidaturas por status')
    ax.set_ylabel('Quantidade')
    fig.tight_layout()

    # 4) embutir no Tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.grid(row=0, column=0, sticky='nsew')

    # 5) retornar o canvas para controle (remover/atualizar posteriormente)
    return canvas
```

Boas práticas e dicas
---------------------
- Sempre chame `canvas.get_tk_widget().grid_forget()` antes de inserir um novo gráfico
  se for re-renderizar o painel para evitar sobreposição.
- Em callbacks de resize, evite redesenhar o gráfico constantemente — use um
  debounce (after cancel/after) para redesenhar apenas após o usuário terminar
  de redimensionar.
- Trate dados ausentes (status vazio, datas inválidas). Use rótulos `Indefinido`
  ou similar para manter consistência.
- Para desempenho, você pode manter a última `Figure` e atualizar seus dados
  (limpar e redesenhar) em vez de criar novas figuras sempre.

Testes manuais
--------------
- Inserir manualmente alguns registros (ou usar o script de teste no `README`) e
  abrir a aplicação; pressionar "Atualizar" (se implementado) para validar o
  gráfico.

Checklist para a integração
---------------------------
- [ ] Adicionar `matplotlib` em `requirements.txt`.
- [ ] Implementar a função de construção do gráfico no `MainWindow`.
- [ ] Fornecer um botão "Atualizar gráfico" e/ou recarregar automaticamente ao
      abrir o dashboard.
- [ ] Garantir que o gráfico redimensiona sem criar loops de redimensionamento.
- [ ] Adicionar um pequeno trecho no README apontando onde o desenvolvedor
      encontrará este guia: `assets/GRAPH_GUIDE.md`.

Contato / Observações
---------------------
Se tiver dúvidas sobre o formato dos dados ou sobre como acessar o `DataStore`,
consulte `meu_emprego.py` (classe `DataStore`).

Bom trabalho — implemente os gráficos usando esse guia e abra um PR apontando
para as alterações no dashboard.
