---
name: python-sqlite-api
description: >
  Constrói um backend Python completo com SQLite e acesso remoto via API REST.
  Use esta skill SEMPRE que o usuário quiser: criar uma API REST em Python; montar
  um backend com banco de dados SQLite; expor dados locais via HTTP/HTTPS; criar
  CRUD completo com FastAPI + SQLAlchemy; adicionar autenticação JWT ou API Key
  a um servidor Python; criar um servidor com endpoints remotos; gerar estrutura
  de projeto Python para API; containerizar uma API Python com Docker; criar
  rotas GET/POST/PUT/DELETE em Python; montar um backend para aplicativo mobile
  ou web. Ative mesmo que o usuário diga apenas "crie uma API", "quero expor meu
  banco de dados", "preciso de um servidor Python", "crie endpoints REST" ou
  "como acesso meu SQLite de outro computador".
---

# Python + SQLite + API REST — Backend Completo

Skill para gerar backends Python prontos para produção usando **FastAPI**,
**SQLAlchemy** e **SQLite**, com acesso remoto seguro via API REST.

---

## Fluxo de execução obrigatório

Siga estas fases em ordem. Não pule etapas.

1. **Entender o domínio** → descubra as entidades, campos e relacionamentos
2. **Gerar estrutura de projeto** → crie todos os arquivos necessários
3. **Implementar modelos e banco** → SQLAlchemy + SQLite
4. **Implementar rotas CRUD** → FastAPI com validação Pydantic
5. **Adicionar autenticação** → JWT ou API Key (perguntar ao usuário)
6. **Gerar Docker + deploy** → Dockerfile e instrução de execução
7. **Testar e documentar** → mostrar URLs, Swagger, exemplos de curl

---

## Fase 1 — Entender o domínio

Antes de gerar qualquer código, pergunte (ou infira do contexto):

- Quais **entidades/tabelas** o banco precisa ter?
- Quais **campos** cada entidade tem (nome, tipo, obrigatório)?
- Há **relacionamentos** entre entidades (1:N, N:N)?
- Qual tipo de **autenticação** desejada? (JWT, API Key, nenhuma)
- O servidor vai rodar **localmente** ou precisa de **deploy remoto** (VPS, Railway, Fly.io)?
- Precisa de **HTTPS**? (relevante para acesso externo real)

Se o usuário não souber responder, proponha um exemplo concreto e siga em frente.

---

## Fase 2 — Estrutura de projeto gerada

Sempre gere esta estrutura de arquivos:

```
projeto/
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app + routers
│   ├── database.py        # Engine SQLite + Session
│   ├── models.py          # Modelos SQLAlchemy
│   ├── schemas.py         # Schemas Pydantic (request/response)
│   ├── crud.py            # Funções de acesso ao banco
│   ├── auth.py            # Autenticação JWT / API Key
│   └── routers/
│       └── <entidade>.py  # Um arquivo por entidade
├── tests/
│   └── test_<entidade>.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Fase 3 — Modelos e banco

### database.py — padrão obrigatório

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# check_same_thread=False obrigatório para SQLite com FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### models.py — padrão de modelo

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Item(Base):
    __tablename__ = "items"
    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, nullable=False, index=True)
    desc      = Column(String, nullable=True)
    active    = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Regras:**
- Sempre incluir `id` (PK), `created_at`, `updated_at`
- Usar `index=True` em campos usados em filtros
- Relacionamentos com `relationship()` e `ForeignKey`

---

## Fase 4 — Schemas Pydantic

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ItemBase(BaseModel):
    name: str
    desc: Optional[str] = None
    active: bool = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None
    active: Optional[bool] = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # Pydantic v2 (era orm_mode no v1)
```

---

## Fase 5 — CRUD

```python
# crud.py
from sqlalchemy.orm import Session
from app import models, schemas

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item: schemas.ItemUpdate):
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    for field, value in item.model_dump(exclude_unset=True).items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
```

---

## Fase 6 — Rotas FastAPI

```python
# app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db
from app.auth import get_current_user  # remover se não usar auth

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=List[schemas.ItemResponse])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=schemas.ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item

@router.post("/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)

@router.put("/{item_id}", response_model=schemas.ItemResponse)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    updated = crud.update_item(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return updated

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    if not crud.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item não encontrado")
```

---

## Fase 7 — main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import items  # importar todos os routers

Base.metadata.create_all(bind=engine)  # cria tabelas automaticamente

app = FastAPI(
    title="Minha API",
    version="1.0.0",
    description="Backend completo Python + SQLite"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringir em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(items.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## Fase 8 — Autenticação

Leia o arquivo de referência correspondente ao modo desejado:

- **JWT (padrão recomendado):** `references/auth-jwt.md`
- **API Key (mais simples):** `references/auth-apikey.md`
- **Sem autenticação:** omitir `Depends(get_current_user)` nas rotas

Pergunte ao usuário qual prefere antes de gerar o código de auth.

---

## Fase 9 — Docker

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data   # persiste o SQLite fora do container
    environment:
      - DATABASE_URL=sqlite:///./data/app.db
    restart: unless-stopped
```

> **⚠️ Importante:** sempre montar volume para o arquivo `.db` — sem isso o banco some ao reiniciar o container.

---

## Fase 10 — requirements.txt padrão

```
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0   # JWT
passlib[bcrypt]>=1.7.4              # hash de senha
httpx>=0.27.0                       # testes assíncronos
pytest>=8.0.0
```

---

## Fase 11 — Acesso remoto

### Rodando localmente com acesso na rede

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse de outro computador na mesma rede: `http://<IP_DA_MAQUINA>:8000`

### Expondo para a internet (acesso externo)

Opções recomendadas:

| Plataforma | Grátis | Comando |
|------------|--------|---------|
| **Railway** | ✅ (trial) | `railway up` |
| **Fly.io** | ✅ (free tier) | `fly launch` |
| **Render** | ✅ (free tier) | via GitHub |
| **VPS própria** | ❌ | nginx + uvicorn |

Para VPS, fornecer também configuração `nginx` como reverse proxy com HTTPS via Certbot.

### Swagger UI automático

FastAPI gera documentação automática:
- `http://localhost:8000/docs` — Swagger UI interativo
- `http://localhost:8000/redoc` — ReDoc
- `http://localhost:8000/openapi.json` — schema OpenAPI

---

## Checklist final antes de entregar

- [ ] Todos os arquivos da estrutura gerados
- [ ] Modelos com `created_at` / `updated_at`
- [ ] `check_same_thread=False` no engine SQLite
- [ ] CORS configurado no `main.py`
- [ ] Volume Docker para persistir o `.db`
- [ ] `.env.example` com todas as variáveis
- [ ] Pelo menos um teste de exemplo em `tests/`
- [ ] README com instruções de instalação e uso
- [ ] Exemplos de `curl` para cada endpoint

---

## Boas práticas obrigatórias

1. **Nunca** commitar o arquivo `.db` no Git — adicionar ao `.gitignore`
2. **Nunca** expor `SECRET_KEY` hardcoded — usar `.env`
3. **Sempre** usar `Depends(get_db)` — nunca instanciar Session manualmente
4. **Sempre** fechar a session no `finally` (já feito no `get_db`)
5. **Sempre** validar entrada com Pydantic — nunca inserir dados brutos no banco
6. Em produção com múltiplas instâncias: migrar para PostgreSQL (SQLite não suporta escrita concorrente)
