# Autenticação por API Key para FastAPI

Ideal para integração entre serviços (machine-to-machine) onde não há login humano.

## auth.py (modo API Key)

```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

API_KEY        = os.getenv("API_KEY", "troque-em-producao")
API_KEY_NAME   = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key inválida ou ausente"
        )
    return api_key
```

## Como proteger uma rota

```python
from app.auth import get_api_key

@router.get("/items/", dependencies=[Depends(get_api_key)])
def list_items(db: Session = Depends(get_db)):
    return crud.get_items(db)
```

## .env.example

```
API_KEY=minha-chave-secreta-aqui
DATABASE_URL=sqlite:///./app.db
```

## Uso com curl

```bash
curl http://localhost:8000/items/ \
  -H "X-API-Key: minha-chave-secreta-aqui"
```

## Múltiplas chaves (banco de dados)

Para cenários com várias integrações, armazene as chaves no banco:

```python
class APIKey(Base):
    __tablename__ = "api_keys"
    id         = Column(Integer, primary_key=True)
    key        = Column(String, unique=True, index=True)
    name       = Column(String)           # nome do cliente/serviço
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

def get_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    key = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active == True).first()
    if not key:
        raise HTTPException(status_code=403, detail="API Key inválida")
    return key
```
