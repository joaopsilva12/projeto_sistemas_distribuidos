# Roteiro palavra por palavra: Demonstração e Conclusão

**Apresentador:** João Paulo · **Slides:** 10 (Demonstração ao vivo) e 11 (Conclusão) · **Tempo:** cerca de 2 min 30 s

Legenda:
- 🗣️ **FALA:** o que dizer, palavra por palavra
- 🖱️ **AÇÃO:** o que fazer no computador

---

## Preparação (antes de a apresentação começar)

Faça isto **antes** de o grupo começar a apresentar, não durante:

1. Abra o **Docker Desktop** e espere aparecer "Engine running".
2. Abra um terminal **na pasta do projeto** e rode:
   ```bash
   docker compose up -d
   ```
3. Confira que voltaram 3 workers, para começar a demonstração do zero:
   ```bash
   docker compose up -d --scale worker=3
   ```
4. Abra o navegador em **http://127.0.0.1:8000**.
5. **Rode um job de teste** (marque Soja e Café arábica e clique em "Distribuir tarefas"). Se a internet ou o IBGE falharem na hora, você já terá resultados na tela para mostrar.
6. Deixe **duas janelas prontas**: o terminal e o navegador. Aumente a fonte do terminal (Ctrl + roda do mouse) para a turma conseguir ler.
7. No painel, deixe marcadas **apenas Soja e Café arábica**. São 54 tarefas, que terminam rápido o suficiente para caber no tempo.

---

## Slide 10: Demonstração ao vivo (≈ 2 min)

### Passo 1: Abertura e nós do cluster (≈ 20 s)

🗣️ **FALA:**
> "Obrigado. Agora eu vou mostrar o AgroDist funcionando de verdade. Tudo o que os meus colegas explicaram até aqui está rodando agora, nesta máquina, dentro do Docker."

🖱️ **AÇÃO:** vá para o terminal e digite:
```bash
docker compose ps
```

🗣️ **FALA** (apontando para a lista na tela):
> "Aqui estão os nós do nosso sistema distribuído. Este é o **agrodist-manager**, o nosso nó coordenador. Estes três são os **workers**, os nós de processamento. E aqui embaixo estão o **Redis**, que é a nossa fila de tarefas, e o **PostgreSQL**, onde ficam os resultados. São seis contêineres conversando entre si por uma rede do Docker."

### Passo 2: Painel e disparo do job (≈ 40 s)

🖱️ **AÇÃO:** vá para o navegador, no painel em http://127.0.0.1:8000.

🗣️ **FALA:**
> "Este é o painel do Manager. Aqui no quadro **Cluster** dá para ver os três workers ativos. Cada um avisa a cada três segundos que está vivo: é o heartbeat que foi explicado antes."

🖱️ **AÇÃO:** mostre as culturas marcadas (Soja e Café arábica) e clique em **"Distribuir tarefas"**.

🗣️ **FALA:**
> "Eu escolhi soja e café arábica. Quando eu clico em distribuir, o Manager divide esse pedido em tarefas: uma para cada cultura em cada um dos 27 estados. São **54 tarefas**, que foram agora para a fila."

### Passo 3: Mostrar a distribuição acontecendo (≈ 30 s)

🖱️ **AÇÃO:** role a página até **"Progresso do job"** e **"Tarefas por worker"**.

🗣️ **FALA** (enquanto a barra avança):
> "Reparem na barra de progresso subindo, e aqui embaixo, em **Tarefas por worker**: os três workers estão dividindo o trabalho sozinhos. Ninguém diz para qual worker vai cada tarefa. Quem está livre pega a próxima da fila. Cada worker ainda processa oito tarefas ao mesmo tempo com programação assíncrona, e cada tarefa faz quatro consultas simultâneas à API do IBGE."

🖱️ **AÇÃO:** role até **"Resultados por estado"**.

🗣️ **FALA:**
> "E aqui estão os dados reais do IBGE, do Levantamento Sistemático da Produção Agrícola: produção, rendimento por hectare e a variação em relação ao ano anterior, de cada estado. Nesta última coluna dá para ver **qual worker processou cada linha**."

### Passo 4: Escalar o cluster (≈ 30 s)

🖱️ **AÇÃO:** volte ao terminal e digite:
```bash
docker compose up -d --scale worker=6
```

🗣️ **FALA** (enquanto o comando roda):
> "Agora imagine que a demanda aumentou. Em um sistema distribuído, a gente não precisa de um computador mais forte: basta colocar mais nós. Com um único comando, eu estou subindo de três para **seis workers**, sem mudar uma linha de código."

🖱️ **AÇÃO:** volte ao navegador e mostre o quadro **Cluster**. Em poucos segundos aparecem 6 workers.

🗣️ **FALA:**
> "E pronto: os novos workers já apareceram no painel e já estão prontos para pegar tarefas da fila. Isso é escalabilidade horizontal."

> **Se sobrar tempo (opcional):** clique de novo em "Distribuir tarefas" para mostrar os 6 workers dividindo o trabalho. Se o tempo estiver curto, pule e vá para a conclusão.

---

## Slide 11: Conclusão (≈ 30 s)

🖱️ **AÇÃO:** volte para os slides e avance para o slide **Conclusão**.

🗣️ **FALA:**
> "Para concluir: o AgroDist mostra na prática uma arquitetura **Manager e Workers**, escalável com Docker, que usa uma fila para distribuir o trabalho e processamento assíncrono dentro de cada nó.
>
> Do lado do agronegócio, transformamos os dados oficiais de safra do IBGE em indicadores de produção e de eficiência no uso da terra, que se ligam diretamente aos temas de ESG.
>
> Como próximos passos, queremos rodar os workers em várias máquinas com o Docker Swarm, reprocessar automaticamente as tarefas que falharem e analisar séries históricas.
>
> O código e o passo a passo para rodar estão no nosso repositório no GitHub. Esse foi o AgroDist. Muito obrigado, e estamos abertos a perguntas."

---

## Plano B: se algo der errado

| Problema | O que fazer | O que dizer |
|---|---|---|
| O job não avança (internet ou IBGE lento) | Mostre os resultados do **job de teste** que você rodou antes | "A API do IBGE está lenta agora, mas aqui está um processamento que fizemos minutos atrás, com o mesmo fluxo." |
| `localhost` não abre | Use **http://127.0.0.1:8000** | (não precisa comentar) |
| Escalar demora | Siga falando; os workers aparecem em alguns segundos | "Os contêineres estão subindo; em instantes eles aparecem no painel." |
| Docker não abre | Mostre os slides 4 e 9 (topologia e resultados) | "Vou mostrar pelo diagrama e pelos resultados do nosso teste." |

---

## Respostas rápidas se perguntarem durante a demonstração

- **"Por que os workers têm números diferentes de tarefas?"** "Porque quem termina antes pega a próxima tarefa da fila. O balanceamento é automático."
- **"O que acontece se eu derrubar um worker?"** "Os outros continuam pegando tarefas da fila." Para mostrar ao vivo:
  ```bash
  docker stop agrodist-worker-1
  ```
- **"De onde vêm os dados?"** "Da API SIDRA do IBGE, tabela 6588, do LSPA, que é a estimativa oficial de safra, atualizada todo mês."
