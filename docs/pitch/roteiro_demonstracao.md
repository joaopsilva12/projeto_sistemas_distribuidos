# Roteiro: Demonstração e Conclusão (João Paulo)

**Tempo:** cerca de 2 min

## Antes de começar
- Docker Desktop aberto.
- Terminal na pasta do projeto, com o sistema no ar:
  ```bash
  docker compose up -d
  ```
- Navegador em **http://127.0.0.1:8000**, com **Soja** e **Café arábica** marcados.

---

## 1. Mostrar os nós
**Faça:** no terminal, rode `docker compose ps`.

**Diga:**
> "Este é o sistema rodando no Docker. Aqui está o **Manager**, que coordena, os **três Workers**, que processam, o **Redis**, que é a fila, e o **PostgreSQL**, que guarda os resultados."

## 2. Disparar o processamento
**Faça:** no navegador, clique em **Distribuir tarefas**.

**Diga:**
> "Pedi soja e café. O Manager dividiu isso em **54 tarefas**, uma por cultura em cada estado, e colocou na fila."

## 3. Mostrar a distribuição
**Faça:** role até **Tarefas por worker** e depois até **Resultados por estado**.

**Diga:**
> "Os três workers estão dividindo as tarefas sozinhos: quem está livre pega a próxima. E aqui estão os dados reais do IBGE, de cada estado, com o worker que processou cada linha."

## 4. Escalar
**Faça:** no terminal, rode `docker compose up -d --scale worker=6`. Depois mostre o quadro **Cluster** no navegador.

**Diga:**
> "Com um único comando, subi de três para **seis workers**. Eles já aparecem no painel, sem mudar nenhuma linha de código."

---

## 5. Conclusão
**Faça:** volte aos slides, no slide **Conclusão**.

**Diga:**
> "Resumindo: o AgroDist é um sistema distribuído com Manager e Workers, que usa uma fila e processamento em paralelo para analisar os dados de safra do IBGE. Como próximo passo, queremos rodar em várias máquinas. Obrigado, estamos abertos a perguntas."

---

## Se der errado
- **O job não avança:** mostre um job que você rodou antes e diga "a API do IBGE está lenta agora; este é um processamento de minutos atrás".
- **A página não abre:** use **http://127.0.0.1:8000**.
