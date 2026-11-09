CREATE TABLE IF NOT EXISTS jobs (
    id          UUID PRIMARY KEY,
    criado_em   TIMESTAMP NOT NULL DEFAULT NOW(),
    produtos    TEXT NOT NULL,
    total       INT  NOT NULL,
    concluidas  INT  NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS resultados (
    id              SERIAL PRIMARY KEY,
    job_id          UUID REFERENCES jobs(id) ON DELETE CASCADE,
    uf_codigo       TEXT NOT NULL,
    uf_nome         TEXT,
    produto_codigo  TEXT NOT NULL,
    produto_nome    TEXT,
    periodo         TEXT,
    area_plantada_ha   NUMERIC,
    area_colhida_ha    NUMERIC,
    producao_t         NUMERIC,
    rendimento_kg_ha   NUMERIC,
    producao_ano_anterior_t NUMERIC,
    variacao_producao_pct   NUMERIC,
    perda_area_pct          NUMERIC,
    worker_id       TEXT NOT NULL,
    tempo_ms        INT,
    status          TEXT NOT NULL,
    erro            TEXT,
    processado_em   TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_resultados_job ON resultados(job_id);
