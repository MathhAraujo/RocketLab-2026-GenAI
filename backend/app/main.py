from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from app.routers import auth, produtos


def custom_key_builder(
    func,
    namespace: str = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
) -> str:
    args_str = ",".join(f"{k}={v}" for k, v in kwargs.items() if k not in ("db", "current_user"))
    return f"{FastAPICache.get_prefix()}:{namespace}:{func.__module__}:{func.__name__}:{args_str}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache", key_builder=custom_key_builder)
    yield


app = FastAPI(
    title="Sistema de Compras Online",
    description="API para gerenciamento de pedidos, produtos, consumidores e vendedores.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(produtos.router, prefix="/api")


@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    description="Verifica o status da API e se está rodando corretamente.",
)
def health():
    return {"status": "ok", "message": "API rodando com sucesso!"}
