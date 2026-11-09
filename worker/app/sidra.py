"""Cliente assíncrono da API SIDRA (IBGE) - tabela 6588 (LSPA)."""
import asyncio

import aiohttp

BASE_URL = "https://apisidra.ibge.gov.br/values"
TABELA_LSPA = 6588

# Variáveis da tabela 6588
VAR_AREA_PLANTADA = "109"
VAR_AREA_COLHIDA = "216"
VAR_PRODUCAO = "35"
VAR_RENDIMENTO = "36"
VARIAVEIS = [VAR_AREA_PLANTADA, VAR_AREA_COLHIDA, VAR_PRODUCAO, VAR_RENDIMENTO]


def _num(valor: str):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None  # SIDRA usa "-", "..", "X" para valores ausentes/sigilosos


async def buscar_variavel(session: aiohttp.ClientSession, uf: str, produto: str,
                          variavel: str, periodos: int = 13, tentativas: int = 3):
    """Retorna lista [(periodo_codigo, periodo_nome, valor, uf_nome, produto_nome)]."""
    url = (f"{BASE_URL}/t/{TABELA_LSPA}/n3/{uf}/v/{variavel}"
           f"/p/last%20{periodos}/c48/{produto}")
    for tentativa in range(1, tentativas + 1):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                dados = await resp.json(content_type=None)
            return [(d["D3C"], d["D3N"], _num(d["V"]), d["D1N"], d["D4N"]) for d in dados[1:]]
        except Exception:
            if tentativa == tentativas:
                raise
            await asyncio.sleep(2 ** tentativa)  # backoff exponencial


async def coletar_tarefa(session: aiohttp.ClientSession, uf: str, produto: str) -> dict:
    """Busca as 4 variáveis EM PARALELO (asyncio.gather) e calcula indicadores."""
    respostas = await asyncio.gather(
        *(buscar_variavel(session, uf, produto, v) for v in VARIAVEIS)
    )
    series = dict(zip(VARIAVEIS, respostas))

    producao = series[VAR_PRODUCAO]
    if not producao:
        raise ValueError("SIDRA não retornou dados para esta combinação")

    atual = producao[-1]
    anterior = producao[0] if len(producao) >= 13 else None  # mesmo mês do ano anterior

    def ultimo(var):
        return series[var][-1][2] if series[var] else None

    plantada, colhida = ultimo(VAR_AREA_PLANTADA), ultimo(VAR_AREA_COLHIDA)
    prod_atual = atual[2]
    prod_ant = anterior[2] if anterior else None

    variacao = None
    if prod_atual is not None and prod_ant:
        variacao = round((prod_atual - prod_ant) / prod_ant * 100, 2)

    perda_area = None
    if plantada and colhida is not None:
        perda_area = round((plantada - colhida) / plantada * 100, 2)

    return {
        "uf_nome": atual[3],
        "produto_nome": atual[4],
        "periodo": atual[1],
        "area_plantada_ha": plantada,
        "area_colhida_ha": colhida,
        "producao_t": prod_atual,
        "rendimento_kg_ha": ultimo(VAR_RENDIMENTO),
        "producao_ano_anterior_t": prod_ant,
        "variacao_producao_pct": variacao,
        "perda_area_pct": perda_area,
    }
