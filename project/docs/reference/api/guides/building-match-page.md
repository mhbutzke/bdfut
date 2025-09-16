# Guia — Construindo uma Match Page com Sportmonks

## Objetivo
Exibir partida com timeline, estatísticas por período, escalações e árbitros.

## Endpoints/Includes
- `fixtures/{id}?include=participants;events;statistics;lineups;referees;venue;periods;scores`
- Dicionários: `types`, `states` (pré-carregados)

## Fluxo de dados (ETL)
1) Janela ampla mantém `fixtures` atualizados (metadados + participants)
2) Ao detectar mudança (pós-jogo), detalhar com `events;statistics;lineups;referees`
3) Persistir em tabelas normalizadas; recalcular MVs (períodos/90min)

## Renderização (Frontend)
- Header: equipes, placar, horário, estado
- Timeline: mapear `events` via `types` e ordenar por `minute`
- Estatísticas: por período (1T/2T/prorrogação) e total
- Lineups: formações, posições, substituições
- Árbitros: principal e assistentes com perfil básico

## Boas práticas
- Carregar incrementalmente (skeletons + progressive rendering)
- Tratar indisponibilidade de stats/lineups com placeholders
- Mostrar timestamp da última atualização
