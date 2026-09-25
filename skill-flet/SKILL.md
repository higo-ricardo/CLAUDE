---
name: dev-flet
description: >
  Skill completa para desenvolvimento de aplicações desktop/mobile/web em Python com Flet
  para sistemas empresariais (ERP leve), especialmente no setor de autopeças no Brasil.
  Use esta skill SEMPRE que o usuário quiser: criar um app Flet do zero; adicionar
  módulos/páginas (PDV, Estoque, Financeiro, Vendas, Config); implementar roteamento
  com ft.Router e @ft.component; estado reativo com @ft.observable; formulários,
  modais, DataTable e NavigationRail; módulo financeiro com DRE, fluxo de caixa
  projetado, contas a pagar/receber; responsividade com page.adaptive; execução
  assíncrona. Ative também para palavras como "HIVERCAR", "sistema de autopeças",
  "ERP em Python", "app comercial com Flet", "módulo financeiro Flet".
---

# Skill: dev-flet

Guia completo de arquitetura e padrões para criar aplicações empresariais em Python com
Flet, seguindo boas práticas de modularidade, reatividade e UX profissional.

---

## 1. Arquitetura do Projeto

```
hivercar/
├── main.py               ← Entry point + App Router
├── state/
│   ├── __init__.py
│   ├── app_state.py      ← Estado global (produtos, vendas, etc.)
│   └── financeiro_state.py
├── pages/
│   ├── __init__.py
│   ├── admin_page.py
│   ├── pdv_page.py
│   ├── vendas_page.py
│   ├── estoque_page.py
│   ├── financeiro_page.py
│   └── config_page.py
├── components/
│   ├── __init__.py
│   ├── my_button.py
│   └── nav_rail.py
└── requirements.txt
```

---

## 2. Entry Point — main.py

```python
import flet as ft
from pages.admin_page import AdminPage
from pages.pdv_page import PdvPage
from pages.vendas_page import VendasPage
from pages.estoque_page import EstoquePage
from pages.financeiro_page import FinanceiroPage
from pages.config_page import ConfigPage

@ft.component
def App():
    return ft.Router([
        ft.Route(index=True,          component=AdminPage),
        ft.Route(path="pdv",          component=PdvPage),
        ft.Route(path="vendas",       component=VendasPage),
        ft.Route(path="estoque",      component=EstoquePage),
        ft.Route(path="financeiro",   component=FinanceiroPage),
        ft.Route(path="config",       component=ConfigPage),
    ])

def main(page: ft.Page):
    page.title = "HIVERCAR"
    page.adaptive = True
    page.url_strategy = ft.UrlStrategy.PATH
    page.add(App())

ft.app(target=main)
```

---

## 3. Componentes Globais

### MyButton (components/my_button.py)

```python
import flet as ft

@ft.component
def MyButton(text: str, icon=None, on_click=None, color=ft.Colors.BLUE):
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(bgcolor=color, color=ft.Colors.WHITE),
    )
```

### NavigationRail (components/nav_rail.py)

```python
import flet as ft

DESTINATIONS = [
    ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD,       label="Admin"),
    ft.NavigationRailDestination(icon=ft.Icons.POINT_OF_SALE,   label="PDV"),
    ft.NavigationRailDestination(icon=ft.Icons.SELL,            label="Vendas"),
    ft.NavigationRailDestination(icon=ft.Icons.INVENTORY,       label="Estoque"),
    ft.NavigationRailDestination(icon=ft.Icons.ACCOUNT_BALANCE, label="Financeiro"),
    ft.NavigationRailDestination(icon=ft.Icons.SETTINGS,        label="Config"),
]

ROUTES = ["", "pdv", "vendas", "estoque", "financeiro", "config"]

@ft.component
def AppNavRail(page: ft.Page):
    def on_change(e):
        page.go(f"/{ROUTES[e.control.selected_index]}")

    return ft.NavigationRail(
        destinations=DESTINATIONS,
        on_change=on_change,
        extended=True,
    )
```

---

## 4. Estado Reativo

> Para detalhes completos de todos os estados, ver → `references/state.md`

### Padrão base

```python
from dataclasses import dataclass, field
import flet as ft

@ft.observable
@dataclass
class FinanceiroState:
    lancamentos: list = field(default_factory=list)
```

### Regra de ouro

- **Nunca** crie lógica de negócio fora do estado reativo.
- Cada página instancia seu próprio state ou recebe via injeção.
- Use `@ft.observable` em toda dataclass de estado.

---

## 5. Módulo Financeiro

> Detalhe completo → `references/financeiro.md`

### Estrutura de Dados

```python
from dataclasses import dataclass, field
import flet as ft

@ft.observable
@dataclass
class Lancamento:
    descricao: str
    valor: float
    tipo: str   # "entrada" | "saida"
    data: str

@ft.observable
@dataclass
class FinanceiroState:
    lancamentos: list[Lancamento] = field(default_factory=list)
```

### Componentes obrigatórios

| Componente         | Responsabilidade                        |
|--------------------|-----------------------------------------|
| `ResumoFinanceiro` | Entradas, Saídas, Saldo atual           |
| `FinanceiroForm`   | Formulário de lançamento (com data)     |
| `DreView`          | DRE: Receita, Despesa, Lucro            |
| `FluxoCaixaView`   | Saldo atual + saldo projetado (+10%)    |
| `TabelaFinanceiro` | DataTable com todos os lançamentos      |
| `FinanceiroPage`   | Monta todos acima em ft.Column          |

### Ícones padrão do financeiro

```python
ft.Icons.ARROW_DOWNWARD   # Receita / Entrada
ft.Icons.ARROW_UPWARD     # Despesa / Saída
ft.Icons.TRENDING_UP      # Lucro / Saldo positivo
ft.Icons.ACCOUNT_BALANCE  # Módulo Financeiro (navegação)
ft.Icons.ATTACH_MONEY     # Campo de valor
ft.Icons.DATE_RANGE       # Campo de data
ft.Icons.DESCRIPTION      # Campo de descrição
ft.Icons.SAVE             # Botão salvar
```

---

## 6. Padrões de Formulário

```python
@ft.component
def FinanceiroForm(state: FinanceiroState):
    descricao = ft.TextField(label="Descrição", prefix_icon=ft.Icons.DESCRIPTION)
    valor     = ft.TextField(label="Valor",     prefix_icon=ft.Icons.ATTACH_MONEY)
    data      = ft.TextField(label="Data",      prefix_icon=ft.Icons.DATE_RANGE)
    tipo      = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("entrada"),
            ft.dropdown.Option("saida"),
        ]
    )

    def salvar(e):
        state.lancamentos.append(
            Lancamento(
                descricao=descricao.value,
                valor=float(valor.value or 0),
                tipo=tipo.value,
                data=data.value,
            )
        )

    return ft.Column([descricao, valor, data, tipo,
                      MyButton("Salvar", icon=ft.Icons.SAVE, on_click=salvar)])
```

---

## 7. Modais

```python
def abrir_modal_confirmacao(page: ft.Page, mensagem: str, on_confirm):
    modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmação"),
        content=ft.Text(mensagem),
        actions=[
            ft.TextButton("Confirmar", on_click=lambda e: (on_confirm(), page.pop_dialog())),
            ft.TextButton("Cancelar",  on_click=lambda e: page.pop_dialog()),
        ],
    )
    page.dialog = modal
    page.open_dialog(modal)
```

---

## 8. DataTable padrão

```python
ft.DataTable(
    columns=[
        ft.DataColumn(ft.Text("Descrição")),
        ft.DataColumn(ft.Text("Valor")),
        ft.DataColumn(ft.Text("Tipo")),
        ft.DataColumn(ft.Text("Data")),
    ],
    rows=[
        ft.DataRow(cells=[
            ft.DataCell(ft.Text(l.descricao)),
            ft.DataCell(ft.Text(f"R$ {l.valor:.2f}")),
            ft.DataCell(ft.Text(l.tipo)),
            ft.DataCell(ft.Text(l.data)),
        ])
        for l in state.lancamentos
    ]
)
```

---

## 9. Configurações de Page

```python
page.title          = "HIVERCAR"
page.adaptive       = True                  # responsividade automática
page.url_strategy   = ft.UrlStrategy.PATH   # ou HASH
page.theme_mode     = ft.ThemeMode.LIGHT
```

---

## 10. Checklist de Validação

Antes de entregar qualquer módulo, verifique:

- [ ] Todos os estados usam `@ft.observable` + `@dataclass`
- [ ] Nenhuma lógica de negócio fora do estado reativo
- [ ] Router atualizado ao adicionar nova página
- [ ] NavigationRail atualizado com novo destino + ícone
- [ ] Formulários possuem `prefix_icon` em todos os campos
- [ ] DRE calcula Receita, Despesa e Lucro corretamente
- [ ] FluxoCaixaView mostra saldo atual e projetado
- [ ] Modais usam `ft.AlertDialog` com `page.open_dialog()`
- [ ] Código completo — sem omissões, sem `# ...` ou `# TODO`

---

## Referências

- `references/financeiro.md` → Implementação completa do módulo financeiro
- `references/state.md`      → Todos os estados reativos do sistema
- `references/pages.md`      → Implementação completa de todas as páginas
