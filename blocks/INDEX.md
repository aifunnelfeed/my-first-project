# ИНДЕКС БЛОКОВ — М.О.С. (Маркетинговая Операционная Система)

## Как использовать

Блоки загружаются **автоматически**. Claude читает `state.md`, определяет текущий стейт и загружает нужные блоки сам. Пользователю достаточно написать **"Продолжаем"**.

Ручная загрузка тоже поддерживается: "Прочитай блок [номер]".

---

## Карта блоков

| # | Файл | Что внутри | Когда нужен |
|---|-------|------------|-------------|
| 01 | `01_system_core.md` | Identity, Philosophy, 7 Laws, RAG Security | **Всегда** — основа системы |
| 02 | `02_state_machine.md` | States, Transitions, Execution Rules | **Всегда** — как работает процесс |
| 03 | `03_evidence_strategy.md` | Evidence Map + Strategy Skeleton | STATE=INPUT → STRATEGY |
| 04 | `04_protocols.md` | Operational Loop, Truth Protocol, Query Protocol | STATE=INPUT, QUERY |
| 05 | `05_research_engine.md` | JTBD, Schwartz Matrix, Unfair Advantage, Curiosity Mining, Corruption Mining, Research Sources, Source Priority, Fact Tagging, Triple Source Rule, Search Templates, Research Subagent Dispatch, Double Filter | STATE=RESEARCH |
| 06 | `06_meaning_maker.md` | UM Engine, Big Idea, Offer Engine | STATE=STRATEGY → EXECUTION |
| 07 | `07_copywriting_kernel.md` | RMBC, Lead, Story, Mechanism, Product Reveal, Close, Fascinations, FAQ, Proof Engine (incl. Proof Research) | STATE=EXECUTION |
| 08 | `08_asset_library.md` | Email, Ads, VSL, Chatbot шаблоны, Subject Lines | STATE=EXECUTION (по формату) |
| 09 | `09_debugging.md` | Critic Mode, Launch Checklist, Strategy Critic | STATE=STRATEGY, DEBUGGING, DELIVERY |
| 10 | `10_xray.md` | Рентген текста — X-ray анализ, 8-мерный скоринг, KB-сравнение | Команда «Рентген» (независимый режим) |

---

## Автозагрузка по стейтам

| Стейт | Блоки | ~Токены |
|-------|-------|---------|
| INPUT | 01 + 03 + 04 | ~12k |
| QUERY | 01 + 04 | ~8k |
| RESEARCH | 01 + 05 | ~10k |
| STRATEGY | 01 + 03 + 06 + 09 | ~13k |
| EXECUTION (landing/VSL) | 02 + 07 | ~14k |
| EXECUTION (email/ads/chatbot) | 02 + 08 | ~10k |
| DEBUGGING | 02 + 09 | ~6k |
| DELIVERY | 02 + 09 | ~6k |
| REVIEW | 02 | ~4k |
| XRAY | 01 + 10 | ~10k |

---

## Типичный workflow по чатам

**Чат 1:** "Новый проект — {описание}" → INPUT + QUERY (блоки загружены автоматически)
**Чат 2:** "Продолжаем" → RESEARCH (блоки загружены автоматически)
**Чат 3:** "Продолжаем" → STRATEGY (блоки загружены автоматически)
**Чат 4–7:** "Продолжаем" → EXECUTION (блоки загружены автоматически)
**Чат 8:** "Продолжаем" → DEBUGGING + DELIVERY (блоки загружены автоматически)
