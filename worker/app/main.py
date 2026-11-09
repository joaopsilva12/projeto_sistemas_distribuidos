"""Worker: consome tarefas da fila Redis e processa de forma assíncrona.

Paralelismo interno em dois níveis:
  1. N corrotinas consumidoras rodando ao mesmo tempo (WORKER_CONCURRENCY);
  2. dentro de cada tarefa, as 4 variáveis são buscadas no SIDRA em paralelo.
"""
import asyncio
import json
import logging
import os
import socket
import time

import aiohttp
import asyncpg
import redis.asyncio as aioredis

from sidra import coletar_tarefa

FILA = "fila:tarefas"
WORKER_ID = os.getenv("WORKER_ID") or socket.gethostname()
CONCORRENCIA = int(os.getenv("WORKER_CONCURRENCY", "8"))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(level=logging.INFO,
                    format=f"%(asctime)s [worker {WORKER_ID}] %(message)s")
log = logging.getLogger("worker")


async def heartbeat(r):
    """Anuncia ao Manager que este worker está vivo (chave expira em 10 s)."""
    while True:
        await r.set(f"worker:{WORKER_ID}", json.dumps(
            {"id": WORKER_ID, "concorrencia": CONCORRENCIA, "visto": time.time()}), ex=10)
        await asyncio.sleep(3)


async def salvar(pool, tarefa, dados, tempo_ms, status, erro=None):
    dados = dados or {}
    await pool.execute(
        """INSERT INTO resultados (job_id, uf_codigo, uf_nome, produto_codigo, produto_nome,
               periodo, area_plantada_ha, area_colhida_ha, producao_t, rendimento_kg_ha,
               producao_ano_anterior_t, variacao_producao_pct, perda_area_pct,
               worker_id, tempo_ms, status, erro)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17)""",
        tarefa["job_id"], tarefa["uf"], dados.get("uf_nome") or tarefa.get("uf_nome"),
        tarefa["produto"], dados.get("produto_nome") or tarefa.get("produto_nome"),
        dados.get("periodo"), dados.get("area_plantada_ha"), dados.get("area_colhida_ha"),
        dados.get("producao_t"), dados.get("rendimento_kg_ha"),
        dados.get("producao_ano_anterior_t"), dados.get("variacao_producao_pct"),
        dados.get("perda_area_pct"), WORKER_ID, tempo_ms, status, erro)
    await pool.execute("UPDATE jobs SET concluidas = concluidas + 1 WHERE id = $1",
                       tarefa["job_id"])


async def consumidor(n, r, pool, http):
    while True:
        item = await r.blpop(FILA, timeout=5)
        if not item:
            continue
        tarefa = json.loads(item[1])
        inicio = time.perf_counter()
        try:
            dados = await coletar_tarefa(http, tarefa["uf"], tarefa["produto"])
            status, erro = "ok", None
        except Exception as e:
            dados, status, erro = None, "erro", str(e)[:300]
        ms = int((time.perf_counter() - inicio) * 1000)
        await salvar(pool, tarefa, dados, ms, status, erro)
        await r.hincrby("stats:workers", WORKER_ID, 1)
        log.info("slot %d | UF %s produto %s -> %s em %d ms",
                 n, tarefa["uf"], tarefa["produto"], status, ms)


async def main():
    r = aioredis.from_url(REDIS_URL, decode_responses=True)
    for _ in range(30):  # aguarda o banco subir
        try:
            pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=CONCORRENCIA)
            break
        except Exception:
            await asyncio.sleep(2)
    else:
        raise RuntimeError("Banco indisponível")

    conector = aiohttp.TCPConnector(limit=CONCORRENCIA * 4)
    async with aiohttp.ClientSession(connector=conector) as http:
        log.info("pronto com %d consumidores assíncronos", CONCORRENCIA)
        await asyncio.gather(heartbeat(r),
                             *(consumidor(i, r, pool, http) for i in range(CONCORRENCIA)))


if __name__ == "__main__":
    asyncio.run(main())
