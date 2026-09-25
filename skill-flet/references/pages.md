# Páginas — Implementação Completa

## admin_page.py

```python
import flet as ft
from state.app_state import AppState
from components.nav_rail import AppNavRail

@ft.component
def AdminPage():
    state = AppState()

    return ft.Row([
        AppNavRail(page=ft.current_page()),
        ft.VerticalDivider(width=1),
        ft.Column([
            ft.Text("Dashboard HIVERCAR", size=24, weight="bold"),
            ft.Divider(),
            ft.Row([
                _card_resumo("Produtos",  str(len(state.produtos)),  ft.Icons.INVENTORY),
                _card_resumo("Vendas",    str(len(state.vendas)),    ft.Icons.SELL),
            ]),
        ], expand=True),
    ], expand=True)

def _card_resumo(titulo: str, valor: str, icone):
    return ft.Card(
        content=ft.Container(
            ft.Column([
                ft.Icon(icone, size=36),
                ft.Text(titulo, size=14),
                ft.Text(valor,  size=28, weight="bold"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
        ),
        width=150,
    )
```

---

## pdv_page.py

```python
import flet as ft
from state.app_state import AppState, ItemVenda
from components.my_button import MyButton
from components.nav_rail import AppNavRail

@ft.component
def PdvPage():
    state = AppState()

    codigo = ft.TextField(label="Código do produto", prefix_icon=ft.Icons.SEARCH)

    def adicionar(e):
        produto = next((p for p in state.produtos if p.codigo == codigo.value), None)
        if produto:
            state.venda_atual.itens.append(ItemVenda(produto=produto, quantidade=1))
            codigo.value = ""

    def fechar_venda(e):
        state.vendas.append(state.venda_atual)
        state.venda_atual = __import__('state.app_state', fromlist=['Venda']).Venda()

    return ft.Row([
        AppNavRail(page=ft.current_page()),
        ft.VerticalDivider(width=1),
        ft.Column([
            ft.Text("PDV — Ponto de Venda", size=24, weight="bold"),
            ft.Row([codigo, MyButton("Adicionar", icon=ft.Icons.ADD, on_click=adicionar)]),
            ft.Divider(),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Produto")),
                    ft.DataColumn(ft.Text("Qtd")),
                    ft.DataColumn(ft.Text("Subtotal")),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(i.produto.nome)),
                        ft.DataCell(ft.Text(str(i.quantidade))),
                        ft.DataCell(ft.Text(f"R$ {i.subtotal:.2f}")),
                    ])
                    for i in state.venda_atual.itens
                ]
            ),
            ft.Divider(),
            ft.Text(f"Total: R$ {state.venda_atual.total:.2f}", size=20, weight="bold"),
            MyButton("Fechar Venda", icon=ft.Icons.CHECK_CIRCLE, on_click=fechar_venda),
        ], expand=True, scroll=ft.ScrollMode.AUTO),
    ], expand=True)
```

---

## vendas_page.py

```python
import flet as ft
from state.app_state import AppState
from components.nav_rail import AppNavRail

@ft.component
def VendasPage():
    state = AppState()

    return ft.Row([
        AppNavRail(page=ft.current_page()),
        ft.VerticalDivider(width=1),
        ft.Column([
            ft.Text("Histórico de Vendas", size=24, weight="bold"),
            ft.Divider(),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("#")),
                    ft.DataColumn(ft.Text("Itens")),
                    ft.DataColumn(ft.Text("Total")),
                    ft.DataColumn(ft.Text("Status")),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(i + 1))),
                        ft.DataCell(ft.Text(str(len(v.itens)))),
                        ft.DataCell(ft.Text(f"R$ {v.total:.2f}")),
                        ft.DataCell(ft.Text(v.status)),
                    ])
                    for i, v in enumerate(state.vendas)
                ]
            ),
        ], expand=True, scroll=ft.ScrollMode.AUTO),
    ], expand=True)
```

---

## estoque_page.py

```python
import flet as ft
from state.app_state import AppState, Produto
from components.my_button import MyButton
from components.nav_rail import AppNavRail

@ft.component
def EstoquePage():
    state = AppState()

    codigo = ft.TextField(label="Código",  prefix_icon=ft.Icons.QR_CODE)
    nome   = ft.TextField(label="Nome",    prefix_icon=ft.Icons.LABEL)
    preco  = ft.TextField(label="Preço",   prefix_icon=ft.Icons.ATTACH_MONEY)
    qtd    = ft.TextField(label="Estoque", prefix_icon=ft.Icons.NUMBERS)

    def salvar(e):
        state.produtos.append(Produto(
            codigo=codigo.value,
            nome=nome.value,
            preco=float(preco.value or 0),
            estoque=int(qtd.value or 0),
        ))
        for f in [codigo, nome, preco, qtd]:
            f.value = ""

    return ft.Row([
        AppNavRail(page=ft.current_page()),
        ft.VerticalDivider(width=1),
        ft.Column([
            ft.Text("Estoque de Produtos", size=24, weight="bold"),
            ft.Row([codigo, nome, preco, qtd]),
            MyButton("Cadastrar Produto", icon=ft.Icons.SAVE, on_click=salvar),
            ft.Divider(),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Código")),
                    ft.DataColumn(ft.Text("Nome")),
                    ft.DataColumn(ft.Text("Preço")),
                    ft.DataColumn(ft.Text("Estoque")),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(p.codigo)),
                        ft.DataCell(ft.Text(p.nome)),
                        ft.DataCell(ft.Text(f"R$ {p.preco:.2f}")),
                        ft.DataCell(ft.Text(str(p.estoque))),
                    ])
                    for p in state.produtos
                ]
            ),
        ], expand=True, scroll=ft.ScrollMode.AUTO),
    ], expand=True)
```

---

## config_page.py

```python
import flet as ft
from state.config_state import ConfigState
from components.my_button import MyButton
from components.nav_rail import AppNavRail

@ft.component
def ConfigPage():
    state = ConfigState()

    nome     = ft.TextField(label="Nome da Empresa", value=state.nome_empresa,
                             prefix_icon=ft.Icons.BUSINESS)
    cnpj     = ft.TextField(label="CNPJ",            value=state.cnpj,
                             prefix_icon=ft.Icons.BADGE)
    telefone = ft.TextField(label="Telefone",         value=state.telefone,
                             prefix_icon=ft.Icons.PHONE)
    endereco = ft.TextField(label="Endereço",         value=state.endereco,
                             prefix_icon=ft.Icons.LOCATION_ON)

    def salvar(e):
        state.nome_empresa = nome.value
        state.cnpj         = cnpj.value
        state.telefone     = telefone.value
        state.endereco     = endereco.value
        print("[DEBUG] Configurações salvas")

    return ft.Row([
        AppNavRail(page=ft.current_page()),
        ft.VerticalDivider(width=1),
        ft.Column([
            ft.Text("Configurações", size=24, weight="bold"),
            ft.Divider(),
            nome, cnpj, telefone, endereco,
            MyButton("Salvar Configurações", icon=ft.Icons.SAVE, on_click=salvar),
        ], expand=True),
    ], expand=True)
```

---

## financeiro_page.py

> Implementação completa em `references/financeiro.md`

```python
# Importar e montar todos os componentes do financeiro:
# ResumoFinanceiro, FinanceiroForm, TabelaFinanceiro, DreView, FluxoCaixaView
# Ver references/financeiro.md para código completo de cada componente.
```
