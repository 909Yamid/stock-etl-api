from fastapi import APIRouter

router = APIRouter()

# Servidor vivo y respondiendo
@router.get("/health")
def verificar_estado():
    return {"status": "ok"}