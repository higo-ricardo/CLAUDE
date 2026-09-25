# Módulo Financeiro — Implementação Completa

## financeiro_state.py

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

---

## ResumoFinanceiro

```python
@ft.component
def ResumoFinanceiro(state: FinanceiroState):
    entradas = sum(l.valor for l in state.lancamentos if l.tipo == "entrada")
    saidas   = sum(l.valor for l in state.lancamentos if l.tipo == "saida")
    saldo    = entradas - saidas

    return ft.Column([
        ft.Row([ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.GREEN),
                ft.Text(f"Entradas: R$ {entradas:.2f}")]),
        ft.Row([ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.RED),
                ft.Text(f"Saídas: R$ {saidas:.2f}")]),
        ft.Row([ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.BLUE),
                ft.Text(f"Saldo: R$ {saldo:.2f}", weight="bold")]),
    ])
```

---

## DreView

```python
@ft.component
def DreView(state: FinanceiroState):
    receita = sum(l.valor for l in state.lancamentos if l.tipo == "entrada")
    despesa = sum(l.valor for l in state.lancamentos if l.tipo == "saida")
    lucro   = receita - despesa

    return ft.Column([
        ft.Text("DRE — Demonstrativo de Resultado", size=18, weight="bold"),
        ft.Divider(),
        ft.Row([ft.Icon(ft.Icons.ARROW_DOWNWARD, color=ft.Colors.GREEN),
                ft.Text(f"Receita Bruta: R$ {receita:.2f}")]),
        ft.Row([ft.Icon(ft.Icons.ARROW_UPWARD, color=ft.Colors.RED),
                ft.Text(f"(-) Despesas: R$ {despesa:.2f}")]),
        ft.Divider(),
        ft.Row([ft.Icon(ft.Icons.TRENDING_UP,
                        color=ft.Colors.GREEN if lucro >= 0 else ft.Colors.RED),
                ft.Text(f"Lucro Líquido: R$ {lucro:.2f}", weight="bold",
                        color=ft.Colors.GREEN if lucro >= 0 else ft.Colors.RED)]),
    ])
```

---

## FluxoCaixaView

```python
@ft.component
def FluxoCaixaView(state: FinanceiroState):
    saldo_atual = sum(
        l.valor if l.tipo == "entrada" else -l.valor
        for l in state.lancamentos
    )
    saldo_projetado = saldo_atual * 1.1  # projeção +10%

    return ft.Column([
        ft.Text("Fluxo de Caixa Projetado", size=18, weight="bold"),
        ft.Divider(),
        ft.Text(f"Saldo Atual:     R$ {saldo_atual:.2f}"),
        ft.Text(f"Saldo Projetado: R$ {saldo_projetado:.2f}",
                weight="bold", color=ft.Colors.BLUE),
        ft.Text("(Projeção baseada em crescimento de 10%)",
                size=11, color=ft.Colors.GREY),
    ])
```

---

## FinanceiroForm

```python
from components.my_button import MyButton

@ft.component
def FinanceiroForm(state: FinanceiroState):
    descricao = ft.TextField(label="Descrição",    prefix_icon=ft.Icons.DESCRIPTION)
    valor     = ft.TextField(label="Valor (R$)",   prefix_icon=ft.Icons.ATTACH_MONEY)
    data      = ft.TextField(label="Data",         prefix_icon=ft.Icons.DATE_RANGE)
    tipo      = ft.Dropdown(
        label="Tipo",
        options=[
            ft.dropdown.Option("entrada"),
            ft.dropdown.Option("saida"),
        ]
    )

    def salvar(e):
        if not descricao.value or not valor.value or not tipo.value:
            return  # validação básica
        state.lancamentos.append(
            Lancamento(
                descricao=descricao.value,
                valor=float(valor.value or 0),
                tipo=tipo.value,
                data=data.value or "—",
            )
        )
        descricao.value = ""
        valor.value = ""
        data.value = ""
        print("[DEBUG] Lançamento financeiro adicionado")

    return ft.Column([
        ft.Text("Novo Lançamento", size=16, weight="bold"),
        descricao, valor, data, tipo,
        MyButton("Salvar Lançamento", icon=ft.Icons.SAVE, on_click=salvar),
    ])
```

---

## TabelaFinanceiro

```python
@ft.component
def TabelaFinanceiro(state: FinanceiroState):
    return ft.DataTable(
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
                ft.DataCell(ft.Text(l.tipo,
                    color=ft.Colors.GREEN if l.tipo == "entrada" else ft.Colors.RED)),
                ft.DataCell(ft.Text(l.data)),
            ])
            for l in state.lancamentos
        ]
    )
```

---

## FinanceiroPage — Completa

```python
from state.financeiro_state import FinanceiroState
from components.nav_rail import AppNavRail

@ft.component
def FinanceiroPage():
    state = FinanceiroState()

    return ft.Row([
        AppNavRail(page=ft.current_page()),
        ft.VerticalDivider(width=1),
        ft.Column([
            ft.Text("Financeiro", size=24, weight="bold"),
            ft.Divider(),
            ResumoFinanceiro(state),
            ft.Divider(),
            FinanceiroForm(state),
            ft.Divider(),
            TabelaFinanceiro(state),
            ft.Divider(),
            DreView(state),
            ft.Divider(),
            FluxoCaixaView(state),
        ], scroll=ft.ScrollMode.AUTO, expand=True),
    ], expand=True)
```

---

## Modal de Exclusão

```python
def abrir_modal_excluir_lancamento(page: ft.Page, state: FinanceiroState, idx: int):
    def confirmar(e):
        state.lancamentos.pop(idx)
        page.pop_dialog()

    modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir lançamento"),
        content=ft.Text("Deseja remover este lançamento financeiro?"),
        actions=[
            ft.TextButton("Excluir",  on_click=confirmar),
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
        ],
    )
    page.dialog = modal
    page.open_dialog(modal)
```
