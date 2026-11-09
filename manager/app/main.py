"""Manager (coordenador): recebe jobs, divide em tarefas e distribui aos Workers via Redis."""
import json
import os
import uuid
from contextlib import asynccontextmanager

import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

FILA = "fila:tarefas"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL")

UFS = {
    "11": "Rondônia", "12": "Acre", "13": "Amazonas", "14": "Roraima", "15": "Pará",
    "16": "Amapá", "17": "Tocantins", "21": "Maranhão", "22": "Piauí", "23": "Ceará",
    "24": "Rio Grande do Norte", "25": "Paraíba", "26": "Pernambuco", "27": "Alagoas",
    "28": "Sergipe", "29": "Bahia", "31": "Minas Gerais", "32": "Espírito Santo",
    "33": "Rio de Janeiro", "35": "São Paulo", "41": "Paraná", "42": "Santa Catarina",
    "43": "Rio Grande do Sul", "50": "Mato Grosso do Sul", "51": "Mato Grosso",
    "52": "Goiás", "53": "Distrito Federal",
}

PRODUTOS = {
    "39443": "Soja", "39441": "Milho (1ª safra)", "39442": "Milho (2ª safra)",
    "40527": "Café total", "39456": "Cana-de-açúcar", "39432": "Arroz",
    "39429": "Algodão herbáceo", "39445": "Trigo", "39436": "Feijão (1ª safra)",
    "39467": "Mandioca", "39463": "Laranja",
}

estado = {}


@asynccontextmanager
async def lifespan(app):
    estado["redis"] = aioredis.from_url(REDIS_URL, decode_responses=True)
    estado["db"] = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    yield
    await estado["db"].close()


app = FastAPI(title="AgroDist - Manager", lifespan=lifespan)


class NovoJob(BaseModel):
    produtos: list[str] = ["39443", "39441", "39442", "40527"]
    ufs: list[str] | None = None  # None = todas as UFs


@app.get("/")
async def dashboard():
    return FileResponse("static/index.html")


@app.get("/api/catalogo")
async def catalogo():
    return {"produtos": PRODUTOS, "ufs": UFS}


@app.post("/api/jobs")
async def criar_job(job: NovoJob):
    ufs = job.ufs or list(UFS)
    invalidos = [p for p in job.produtos if p not in PRODUTOS]
    if invalidos or not job.produtos:
        raise HTTPException(400, f"Produtos inválidos: {invalidos}")

    job_id = str(uuid.uuid4())
    # Particionamento: 1 tarefa = 1 produto x 1 UF
    tarefas = [{"job_id": job_id, "uf": uf, "uf_nome": UFS.get(uf),
                "produto": p, "produto_nome": PRODUTOS[p]}
               for p in job.produtos for uf in ufs]

    await estado["db"].execute(
        "INSERT INTO jobs (id, produtos, total) VALUES ($1, $2, $3)",
        job_id, ",".join(job.produtos), len(tarefas))
    await estado["redis"].rpush(FILA, *(json.dumps(t) for t in tarefas))
    return {"job_id": job_id, "tarefas": len(tarefas)}


@app.get("/api/jobs")
async def listar_jobs():
    rows = await estado["db"].fetch("SELECT * FROM jobs ORDER BY criado_em DESC LIMIT 20")
    return [dict(r) for r in rows]


@app.get("/api/jobs/{job_id}")
async def detalhar_job(job_id: uuid.UUID):
    job = await estado["db"].fetchrow("SELECT * FROM jobs WHERE id = $1", job_id)
    if not job:
        raise HTTPException(404, "Job não encontrado")
    resultados = await estado["db"].fetch(
        "SELECT * FROM resultados WHERE job_id = $1 ORDER BY producao_t DESC NULLS LAST", job_id)
    por_worker = await estado["db"].fetch(
        """SELECT worker_id, COUNT(*) AS tarefas, AVG(tempo_ms)::INT AS tempo_medio_ms
           FROM resultados WHERE job_id = $1 GROUP BY worker_id ORDER BY worker_id""", job_id)
    ranking = await estado["db"].fetch(
        """SELECT produto_nome, SUM(producao_t) AS producao_total_t,
                  AVG(rendimento_kg_ha)::INT AS rendimento_medio
           FROM resultados WHERE job_id = $1 AND status = 'ok'
           GROUP BY produto_nome ORDER BY producao_total_t DESC NULLS LAST""", job_id)
    return {"job": dict(job), "por_worker": [dict(r) for r in por_worker],
            "ranking_produtos": [dict(r) for r in ranking],
            "resultados": [dict(r) for r in resultados]}


@app.get("/api/cluster")
async def cluster():
    """Workers ativos (heartbeat) e tamanho da fila."""
    r = estado["redis"]
    workers = [json.loads(await r.get(k)) async for k in r.scan_iter("worker:*")]
    return {"fila_pendente": await r.llen(FILA),
            "workers_ativos": sorted(workers, key=lambda w: w["id"]),
            "total_por_worker": await r.hgetall("stats:workers")}
