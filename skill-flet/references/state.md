# Estados Reativos — Implementação Completa

## Regras Gerais

- Todo estado usa `@ft.observable` + `@dataclass`
- Toda lista usa `field(default_factory=list)`
- Nunca crie lógica de negócio fora do estado reativo
- Estados são instanciados dentro da página ou injetados via props

---

## app_state.py — Estado Global

```python
from dataclasses import dataclass, field
import flet as ft

@ft.observable
@dataclass
class Produto:
    codigo: str
    nome: str
    preco: float
    estoque: int

@ft.observable
@dataclass
class ItemVenda:
    produto: Produto
    quantidade: int

    @property
    def subtotal(self) -> float:
        return self.produto.preco * self.quantidade

@ft.observable
@dataclass
class Venda:
    itens: list[ItemVenda] = field(default_factory=list)
    status: str = "aberta"  # "aberta" | "fechada" | "cancelada"

    @property
    def total(self) -> float:
        return sum(i.subtotal for i in self.itens)

@ft.observable
@dataclass
class AppState:
    produtos: list[Produto] = field(default_factory=list)
    vendas:   list[Venda]   = field(default_factory=list)
    venda_atual: Venda      = field(default_factory=Venda)
```

---

## financeiro_state.py — Estado Financeiro

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

    @property
    def entradas(self) -> float:
        return sum(l.valor for l in self.lancamentos if l.tipo == "entrada")

    @property
    def saidas(self) -> float:
        return sum(l.valor for l in self.lancamentos if l.tipo == "saida")

    @property
    def saldo(self) -> float:
        return self.entradas - self.saidas

    @property
    def saldo_projetado(self) -> float:
        return self.saldo * 1.1
```

---

## estoque_state.py

```python
from dataclasses import dataclass, field
import flet as ft

@ft.observable
@dataclass
class MovimentoEstoque:
    produto_codigo: str
    quantidade: int
    tipo: str   # "entrada" | "saida"
    data: str

@ft.observable
@dataclass
class EstoqueState:
    movimentos: list[MovimentoEstoque] = field(default_factory=list)
```

---

## config_state.py

```python
from dataclasses import dataclass
import flet as ft

@ft.observable
@dataclass
class ConfigState:
    nome_empresa: str = "HIVERCAR"
    cnpj: str = ""
    telefone: str = ""
    endereco: str = ""
    tema: str = "light"   # "light" | "dark"
```
