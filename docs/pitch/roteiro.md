# Roteiro do Pitch (máx. 10 min)

**Equipe:** Alan, Angelo, João Paulo, João Victor, Lucas e Vitor.

Slides: [`AgroDist_Pitch.pptx`](AgroDist_Pitch.pptx). Roteiro palavra por palavra da demonstração e conclusão: [`roteiro_demonstracao.md`](roteiro_demonstracao.md). As falas também estão nas anotações de cada slide.

## Antes de começar
- Docker Desktop aberto e cluster no ar: `docker compose up -d`
- Navegador aberto em http://127.0.0.1:8000
- Terminal aberto na pasta do projeto

## Tempo por slide

| # | Slide | Tempo | Acumulado |
|---|---|---|---|
| 1 | Capa | 0:30 | 0:30 |
| 2 | Contexto Agro | 1:00 | 1:30 |
| 3 | O que o AgroDist faz | 1:00 | 2:30 |
| 4 | Topologia no Docker | 1:30 | 4:00 |
| 5 | Por que Manager/Worker | 1:00 | 5:00 |
| 6 | Comunicação entre os nós | 1:00 | 6:00 |
| 7 | Paralelismo em 3 níveis | 1:00 | 7:00 |
| 8 | Tecnologias | 0:30 | 7:30 |
| 9 | Resultados | 0:30 | 8:00 |
| 10 | Demonstração ao vivo | 1:30 | 9:30 |
| 11 | Conclusão | 0:30 | 10:00 |

## Falas principais

**1. Capa.** "O AgroDist é um ecossistema distribuído que coleta e processa em paralelo as estimativas oficiais de safra do IBGE para todos os estados."

**2. Contexto.** O LSPA é a estimativa oficial de safra, revisada todo mês. Cada combinação de cultura e estado é uma consulta independente, o que torna o problema naturalmente paralelizável. Relação com ESG: o rendimento por hectare mostra eficiência no uso da terra, e a diferença entre área plantada e colhida aponta perdas por clima.

**3. Solução.** Quatro passos: pedido, particionamento, distribuição e consolidação. Um job com 4 culturas vira 108 tarefas independentes.

**4. Topologia.** Seis contêineres em uma rede bridge. O Manager é o coordenador e o único ponto de entrada. Os Workers são réplicas do mesmo serviço. O Redis faz a fila e o PostgreSQL guarda os resultados.

**5. Justificativas.** Desacoplamento, escala horizontal sem mudar código, balanceamento automático pela fila (quem está livre pega a próxima tarefa) e tolerância a falhas.

**6. Comunicação.** Seguir o caminho de uma tarefa pela tabela. Manager e Workers não conversam diretamente: trocam mensagens pela fila. O heartbeat informa quais workers estão vivos.

**7. Paralelismo.** Nível 1: vários contêineres. Nível 2: 8 corrotinas asyncio em cada worker. Nível 3: as 4 variáveis de cada tarefa buscadas ao mesmo tempo. Contar o aprendizado: o IBGE derrubava conexões com 96 requisições simultâneas, então limitamos a 4 conexões por worker com um semáforo, e o tempo por tarefa caiu de 30–50 s para cerca de 10 s.

**8. Tecnologias.** Passar rápido; destacar que a pilha é assíncrona de ponta a ponta.

**9. Resultados.** 108 tarefas, nenhum erro, cerca de 73 s, carga dividida entre os workers só pela fila.

**10. Demonstração.**
1. `docker compose ps`: mostrar o Manager e os Workers.
2. No painel, distribuir 4 culturas; mostrar a fila esvaziando e a coluna "Worker" nos resultados.
3. `docker compose up -d --scale worker=6` e criar um novo job; os novos workers aparecem no painel.
4. `docker stop agrodist-worker-1`; o job continua.

**11. Conclusão.** Retomar os três pontos e abrir para perguntas.

## Perguntas prováveis
- **Por que Redis e não RabbitMQ?** Mais simples de operar e suficiente para uma fila de trabalho; o padrão seria o mesmo com RabbitMQ.
- **E se um worker cair no meio de uma tarefa?** As outras tarefas continuam sendo processadas pelos demais. A tarefa em andamento se perde; uma melhoria futura é usar uma fila de confirmação (BLMOVE com reprocessamento).
- **Por que asyncio e não threads?** O trabalho é dominado por espera de rede (I/O), e corrotinas lidam com muitas conexões com custo menor que threads.
- **Isso roda em várias máquinas?** Sim, com Docker Swarm, usando o mesmo arquivo Compose; os workers só precisam alcançar o Redis e o Postgres.
