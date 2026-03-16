# Research Engine — Индекс блоков

## Блоки

| # | Файл | Название | ~Токенов |
|---|------|----------|----------|
| 01 | 01_system_core.md | Идентификация + Философия + 5 Законов | ~3k |
| 02 | 02_state_machine.md | Стейт-машина (6 стейтов) + Переходы + Dispatch | ~8k |
| 03 | 03_intake_protocol.md | Query Protocol + HYPOTHESIS-HEAVY + Research Brief | ~4k |
| 04 | 04_collection_engine.md | Протоколы сбора данных + Субагенты + DATA_CONFIDENCE | ~12k |
| 05 | 05_synthesis_engine.md | JTBD + Schwartz + Belief Map + Decision Journey + Objection Tree | ~10k |
| 06 | 06_simulation_engine.md | Персоны + 3 теста + Adversarial Personas | ~6k |
| 07 | 07_validation_protocol.md | Cross-validation + Confidence Scoring + Hypothesis Registry | ~5k |
| 08 | 08_delivery_protocol.md | Сборка research_pack/ + HTML-отчёт | ~8k |

## Агенты

| ID | Файл | Название | Стейт |
|----|------|----------|-------|
| A | agents/A_voc_mining.md | VOC Mining | COLLECTION (Wave 1) |
| B | agents/B_competitor_market.md | Competitor + Market | COLLECTION (Wave 1) |
| C | agents/C_curiosity_corruption.md | Curiosity + Corruption | COLLECTION (Wave 1) |
| S | agents/S_audience_depth.md | Audience Depth | COLLECTION (Wave 2) |
| T | agents/T_trend_dynamics.md | Trend & Market Dynamics | COLLECTION (Wave 2) |
| H | agents/H_research_assembler.md | Research Assembler | COLLECTION (Wave 3) |
| U | agents/U_belief_mapper.md | Belief Mapper | SYNTHESIS (опционально) |
| V | agents/V_adversarial_persona.md | Adversarial Persona | SIMULATION |
| W | agents/W_persona_simulator.md | Persona Simulator | SIMULATION |

## Автозагрузка по стейту

| Стейт | Блоки | ~Токенов |
|-------|-------|----------|
| INPUT | 01 + 03 | ~7k |
| COLLECTION | 01 + 02 + 04 | ~23k |
| SYNTHESIS | 01 + 02 + 05 | ~21k |
| SIMULATION | 01 + 02 + 06 | ~17k |
| VALIDATION | 01 + 02 + 07 | ~16k |
| DELIVERY | 01 + 02 + 08 | ~19k |

Агенты загружаются по dispatch — только нужный файл в момент вызова.
