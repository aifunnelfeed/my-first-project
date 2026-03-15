# БЛОК 11: ОРКЕСТРАТОР СУБАГЕНТОВ (Agent Orchestration + Dispatch)

## РАЗДЕЛ 7: ОРКЕСТРАТОР СУБАГЕНТОВ (AGENT ORCHESTRATOR)

### 7.1. ОБЩИЕ ПРАВИЛА СУБАГЕНТОВ
КОД ДОСТУПА: [SUBAGENT_RULES_V1]

**8 правил для ВСЕХ субагентов:**

1. **Нет доступа к blocks/.** Субагенты НЕ читают блоки автоматически — все инструкции передаются в промпте.
2. **Контекст проекта: 3-5 предложений.** Из brief.md/strategy.md — только самое важное, НЕ весь файл.
3. **Строгий формат вывода.** Каждый субагент возвращает ответ ТОЧНО по шаблону из своей секции. Отклонение от формата = невалидный результат.
4. **Обработка ошибок.** Если инструмент (WebSearch/MCP) недоступен → субагент возвращает `STATUS: TOOL_UNAVAILABLE` + описание того, что не смог сделать + частичные результаты (если есть).
5. **Запрет на выдумку.** Запрещено придумывать факты, цифры, цитаты, источники. Если данные не найдены → `НЕ НАЙДЕНО`.
6. **Инструмент запуска.** Claude Code Agent tool (`subagent_type="general-purpose"`). Субагенты запускаются параллельно, когда задачи независимы.
7. **Результаты показываются пользователю ПЕРЕД интеграцией** в файлы проекта (правило из CLAUDE.md). Молчаливая вставка запрещена.
8. **Язык.** Субагент работает на языке проекта (обычно RU для русскоязычных проектов, EN для англоязычных запросов).

---

### 7.2. РЕЕСТР СУБАГЕНТОВ
КОД ДОСТУПА: [SUBAGENT_REGISTRY_V1]

| ID | Название | Файл промпта | Когда запускается | Что возвращает |
|----|----------|-------------|-------------------|----------------|
| A  | VOC Mining | `agents/A_voc_mining.md` | STATE=RESEARCH | Теггированные VOC-цитаты |
| B  | Competitor + Market | `agents/B_competitor_market.md` | STATE=RESEARCH | Таблицы конкурентов + STAT |
| C  | Curiosity + Corruption | `agents/C_curiosity_corruption.md` | STATE=RESEARCH | Углы для Big Idea |
| D  | Proof Research | `agents/D_proof_research.md` | EXECUTION (PROOF_MINING gap) | Исследования + Insider Knowledge |
| E  | Research-Mini | `agents/E_research_mini.md` | EXECUTION (data gap) | Точечные данные |
| F  | Block Critic | `agents/F_block_critic.md` | DEBUGGING (после каждого блока COPY) | CRITIC REPORT (PASS/FAIL + corrections) |
| G  | Launch Critic | `agents/G_launch_critic.md` | DELIVERY (после сборки) | LAUNCH REPORT (PASS/FAIL + corrections) |
| H  | Research Assembler | `agents/H_research_assembler.md` | STATE=RESEARCH (после A+B+C) | Готовый research_raw.md + SUMMARY |
| I  | KB-Scout | `agents/I_kb_scout.md` | EXECUTION (PHASE C, перед блоком COPY) | Top-3 формулы + Top-2 примера |
| J  | Alternatives Scout | `agents/J_alternatives_scout.md` | STRATEGY (авто, фон) / команда "Альтернативы" | ALTERNATIVES REPORT |
| P  | Reader Simulation | `agents/P_reader_simulation.md` | DELIVERY (после Launch Critic) | READER MONOLOGUE (BUY/LEAVE/MAYBE) |
| Q  | Fresh Eyes Review | `agents/Q_fresh_eyes.md` | STATE=REVIEW (первый шаг) | FRESH EYES REPORT (12 критериев, /10) |
| R  | Mini Fresh Eyes | `agents/R_mini_fresh_eyes.md` | EXECUTION (3 точки) | MINI FRESH EYES (5 критериев, OK/⚠️) |

**Загрузка промптов:** при dispatch субагента прочитай его файл из `blocks/agents/` и используй промпт-шаблон из файла.

---

### 7.3. ПРАВИЛА ДИСПАТЧА
КОД ДОСТУПА: [DISPATCH_RULES_V1]

**STATE=RESEARCH (полный ресерч):**
- Если WebSearch доступен → dispatch A + B + C параллельно
- Пока субагенты работают → главный агент выполняет JTBD_DECODER + SCHWARTZ_MATRIX
- По возвращении A+B+C → dispatch H (Research Assembler) с выходами A+B+C
- H возвращает готовый research_raw.md → DOUBLE FILTER (секция 7.4)
- Если нужен PROOF_RESEARCH → dispatch D (обычно позже, внутри EXECUTION)

**STATE=EXECUTION (PHASE C):**
- Data gap типа B (нужен WebSearch) → dispatch E (Research-Mini)
- PROOF_MINING шаг 5 (пробелы Scientific/Historical/Authority) → dispatch D (Proof Research)

**ПРОТОКОЛ DISPATCH D (Proof Research) — пошагово:**
1. Основной агент выполняет PROOF_MINING шаги 1-4 (инвентаризация, поиск формул, аудитория, эксперт)
2. Шаг 5 (Gap-анализ) → определяет пробелы. Если пробелы типа Scientific/Historical/Authority:
3. **Основной агент формирует контекст** для D: UMR-заявления, требующие подкрепления (из шага 5)
4. **Dispatch D** (субагент) с контекстом → D работает параллельно
5. **Основной агент НЕ ждёт D** — продолжает писать блок с имеющимся proof. На месте недостающих элементов ставит `[ВСТАВИТЬ: ...]` плейсхолдеры
6. **Когда D вернётся** — показать результаты пользователю → заменить плейсхолдеры найденными proof-элементами → перезаписать блок
7. **Если D не нашёл** — плейсхолдеры остаются, разрешаются в PLACEHOLDER RESOLUTION

**STATE=EXECUTION (PHASE C — KB-SCOUT):**
- Перед каждым блоком COPY (кроме Proof) → dispatch I (KB-Scout) ПАРАЛЛЕЛЬНО с подготовкой контекста блока
- ИСКЛЮЧЕНИЕ: block_type = Proof → НЕ dispatch I (Proof использует собственный PROOF_MINING_V1)
- По возвращении I → показать KB-SCOUT REPORT пользователю → основной агент объединяет свои находки + REPORT скаута → пишет блок
- Fallback: основной агент работает через KNOWLEDGE GATE самостоятельно

**STATE=EXECUTION — MINI FRESH EYES (автоматический, 3 точки):**

Субагент R запускается автоматически в 3 точках EXECUTION. Не требует команды пользователя.

- **Точка 1 — после Headline + Lead (Part 1 + Part 2):**
  - Триггер: блок Lead утверждён (PASS от Block Critic F)
  - Dispatch R с текстом: headline + lead part 1 + lead part 2
  - Фокус: первое впечатление, сюжетная логика, тон

- **Точка 2 — после Story + Mechanism:**
  - Триггер: блок Mechanism утверждён (PASS от Block Critic F)
  - Dispatch R с текстом: headline + lead + story + mechanism (все утверждённые блоки)
  - Фокус: противоречия между блоками, повторы образов, переходы

- **Точка 3 — после сборки draft.md (до DELIVERY):**
  - Триггер: все блоки утверждены, draft.md собран
  - Dispatch R с текстом: весь draft.md
  - Фокус: полный скан — повторы, тон, противоречия, связность

**Обработка результата R:**
- Все 5 критериев = OK → продолжаем без остановки, показать пользователю краткую строку: "Mini Fresh Eyes #{N}: OK"
- Есть ⚠️ → показать пользователю MINI FRESH EYES REPORT → спросить: "Исправить сейчас или продолжить?"
  - Исправить → правки → НЕ перезапускать R (не блокировать бесконечно)
  - Продолжить → замечания сохраняются, учитываются при Launch Critic
- Fallback (Agent tool недоступен): пропустить (R — advisory, не blocking)

**STATE=DEBUGGING (после каждого блока COPY) — ОБЯЗАТЕЛЬНО:**
- Dispatch F (Block Critic) с текстом блока + контекст проекта
- Получить CRITIC REPORT → показать пользователю
- PASS → "Принять блок?"
- FAIL → показать CORRECTIONS → "Применить исправления?"

**STATE=DELIVERY (перед FINAL SELF-CHECK):**

<!-- TODO: ADVERSARIAL ARENA — вставить здесь (Задача 2) -->
<!-- TODO: DIAGNOSTICS (Emotion Map ∥ Bias Audit) — вставить здесь (Задача 3) -->

**Шаг 1 — LAUNCH CRITIC (обязательно):**
- После сборки final.md → dispatch G (Launch Critic)
- PASS → переход к Шагу 2
- FAIL → показать LAUNCH REPORT → исправить → перезапустить G

**Шаг 2 — AUDIENCE SIMULATION (обязательно):**
- После PASS Launch Critic → запустить [AUDIENCE_SIMULATION_V1] (см. `agents/P_reader_simulation.md`)
- Генерация персон → показать пользователю → параллельный dispatch 5-8 субагентов P → SIMULATION REPORT
- PASS → FINAL SELF-CHECK
- NEEDS_FIX → рекомендации, решение пользователя
- CRITICAL_FIX → обязательные правки → повторная симуляция (макс. 2 итерации)

**STATE=STRATEGY (Alternatives Scout — ФОНОВЫЙ):**
- После генерации PHASE A (стратегия v1) → dispatch J В ФОНЕ (run_in_background=true)
- J работает ПАРАЛЛЕЛЬНО с KB GATE и PHASE B — НЕ блокирует основной поток
- Контекст для J: brief-context (3-5 предложений) + research-context (JTBD, DRE/DES, VOC топ-5, UMP/UMR из стратегии v1) + strategy v1 (секции A-K)
- По возвращении J: главный агент сохраняет ALTERNATIVES REPORT в alternatives.md, показывает пользователю КРАТКУЮ СВОДКУ
- Fallback (Agent tool недоступен): пропустить автодиспатч

**STATE=REVIEW (Fresh Eyes — первый шаг):**
- При входе в REVIEW → dispatch Q (Fresh Eyes Review) ПЕРЕД точечными правками
- Контекст для Q: ТОЛЬКО текст final.md. Без strategy.md, без blocks/, без системных протоколов
- Q возвращает FRESH EYES REPORT → показать пользователю
- Пользователь решает, какие замечания Q принять для точечных правок
- Fallback (Agent tool недоступен): главный агент выполняет сокращённый Fresh Eyes in-context (5 критериев)

**РУЧНОЙ ДИСПАТЧ — команда "Альтернативы" / "Alternatives" (любой стейт):**
- Пользователь вводит "Альтернативы" → dispatch J
- Контекст адаптируется по текущему стейту:

  | Стейт | Что передать J |
  |-------|---------------|
  | INPUT/QUERY | brief-context only |
  | RESEARCH | brief-context + research (сырой или финальный) |
  | STRATEGY | brief + research + strategy (v1 и/или v2) |
  | EXECUTION | brief + research + strategy + текущий draft.md + текущий block_type |
  | DEBUGGING | brief + research + strategy + текущий блок + CRITIC REPORT (FAIL corrections) |
  | DELIVERY/REVIEW | brief + research + strategy + final.md |

- Ручной вызов = НЕ фоновый. Результат показывается пользователю сразу

**FALLBACK (всегда):**
Если Agent tool недоступен → выполнять проверки in-context (блок 09):
- F → 34 вопроса CRITIC_MODE_V1 (секция 6.1)
- G → 30 вопросов LAUNCH_CHECKLIST_V1 (секция 6.2)
- H → главный агент собирает research_raw.md вручную
- A-E → серийный ресерч в основном агенте
- I → основной агент выполняет KNOWLEDGE GATE самостоятельно
- J → главный агент генерирует альтернативы in-context (сокращённый набор)
- P → 3 персоны in-context (PRIMARY-BURNED + PRIMARY-другая модель + SECONDARY)
- Q → сокращённый Fresh Eyes in-context (5 критериев)
- R → пропустить (advisory)

---

### 7.4. ПАЙПЛАЙН ОБРАБОТКИ РЕЗУЛЬТАТОВ
КОД ДОСТУПА: [RESULT_PIPELINE_V1]

#### A) Research Pipeline (субагенты A, B, C)

**ЦЕЛЬ:** Субагенты собирают сырые данные → пользователь фильтрует → только одобренное идёт в работу.

**ПАЙПЛАЙН:**
1. Субагенты A+B+C возвращают сырые данные → dispatch H (Research Assembler) с выходами A+B+C
2. H дедуплицирует, кросс-проверяет (Triple Source Rule), форматирует → возвращает готовый `research_raw.md`
3. Главный агент записывает `research_raw.md` и показывает пользователю с маркерами надёжности
4. Пользователь просматривает и решает по каждому факту:
   - ✅ Оставить (одобрено)
   - ❌ Убрать (нерелевантно/неточно)
   - ✏️ Исправить (пользователь корректирует факт)
   - 📌 Добавить (пользователь добавляет свои данные — автоматически S1)
5. Одобренные данные → `research.md` (финальный формат с тегами)
6. Git commit: `research({slug}): {краткое описание}`

**ФОРМАТ research_raw.md:**
```markdown
# Сырой ресерч: {название проекта}
## Дата: {дата}
## Источник: субагент A (VOC) + субагент B (Market) + субагент C (Curiosity/Corruption)

---
{объединённые результаты всех субагентов — каждый факт с тегами [TYPE|SOURCE|RELIABILITY|RELEVANCE]}
---

## SUMMARY (главный агент)
- Всего фактов: {N}
- ★★★ CONFIRMED: {N}
- ★★ CROSS-CHECKED: {N}
- ★ SINGLE: {N}
- ⚠️ HYPOTHESIS: {N}
- Рекомендация: {что стоит перепроверить / чего не хватает}
```

**ФОРМАТ research.md (после одобрения):**
Тот же формат, что используется сейчас (JTBD Map, Schwartz Matrix, Unfair Advantage, Curiosity Mining, Corruption Mining, VOC, Market Data, Competitors, Evidence Map), НО с добавлением тегов `[TYPE|SOURCE|RELIABILITY|RELEVANCE]` к каждому факту/цитате.

**ПРАВИЛО РАЗДЕЛЕНИЯ ОТВЕТСТВЕННОСТИ:**
- **Субагенты** собирают СЫРЫЕ данные (VOC, цифры, факты)
- **Главный агент** ИНТЕРПРЕТИРУЕТ (JTBD_DECODER, SCHWARTZ_MATRIX, UNFAIR_ADVANTAGE_MINER заполняет сам на основе brief.md + одобренных данных)
- **Пользователь** ФИЛЬТРУЕТ (одобряет/отклоняет/корректирует)

**КРОСС-ПРОВЕРКА МЕЖДУ СУБАГЕНТАМИ:**
Выполняется субагентом H (Research Assembler): дедупликация + Triple Source Rule между субагентами. Если Agent tool для H недоступен — главный агент выполняет кросс-проверку вручную.

---

#### B) Proof/Mini Pipeline (субагенты D, E)

**ПАЙПЛАЙН:**
1. Субагент возвращает результат
2. Главный агент показывает пользователю
3. Пользователь одобряет/отклоняет/корректирует
4. Одобренные данные интегрируются в текущий блок

Без промежуточного файла — результаты интегрируются inline.

---

#### C) Critic Pipeline (субагенты F, G)

**ПАЙПЛАЙН:**
1. Субагент возвращает CRITIC REPORT (F) или LAUNCH REPORT (G)
2. Главный агент валидирует: все ли вопросы отвечены, формат корректен
3. Главный агент показывает пользователю:
   - **PASS:** "Блок {name} прошёл проверку ({score}/{applicable} — {percent}%). Принять блок? (да / правки / следующий блок)"
   - **FAIL:** "Блок {name} не прошёл проверку ({score}/{applicable} — {percent}%). Исправления: {список из CORRECTIONS}. Применить исправления? (да / вручную / override)"
4. Действия пользователя:
   - **"Да" / "Принять"** (PASS) → пометить блок как APPROVED в state.md, перейти к следующему
   - **"Применить исправления"** (FAIL) → главный агент переписывает блок по CORRECTIONS → повторный dispatch F
   - **"Вручную"** (FAIL) → пользователь описывает свои правки → главный агент применяет → повторный dispatch F
   - **"Override"** (FAIL) → принять как есть (пользователь берёт ответственность, зафиксировать в state.md: "OVERRIDE by user")
5. **Deadlock (3 FAIL на один блок):** Срабатывает существующий протокол из CLAUDE.md:
   - СТОП — не пытайся исправить снова
   - Покажи: "Блок {название} не прошёл проверку 3 раза. Причины: {список}"
   - Варианты: A) Вернуться к STRATEGY, B) Упростить блок, C) Пропустить, D) Принять как есть
6. **Обновление state.md:** После каждого FAIL → обновить секцию "Счётчик попыток"

---

#### D) KB-Scout Pipeline (субагент I)

**ЦЕЛЬ:** Усилить KNOWLEDGE GATE дополнительным материалом из KB. Скаут НЕ заменяет поиск основного агента — он приносит дополнительные формулы и примеры.

**ПАЙПЛАЙН:**
1. Начало PHASE C → dispatch I параллельно с подготовкой контекста блока
2. I выполняет `search_knowledge()` → фильтрует → возвращает KB-SCOUT REPORT
3. Основной агент показывает пользователю REPORT вместе со своими находками
4. Основной агент объединяет оба источника → пишет блок COPY
5. Результаты I НЕ записываются в файл — используются inline

---

#### E) Alternatives Pipeline (субагент J)

**ЦЕЛЬ:** Собрать альтернативные креативные направления. Кумулятивное накопление идей в alternatives.md.

**ПАЙПЛАЙН (авто-режим, STATE=STRATEGY):**
1. После PHASE A → dispatch J в фоне (run_in_background=true)
2. J генерирует ALTERNATIVES REPORT → возвращает главному агенту
3. Главный агент сохраняет в `projects/{name}/alternatives.md` (кумулятивно)
4. Показывает пользователю КРАТКУЮ СВОДКУ после завершения STRATEGY
5. Git commit: `alt({slug}): {краткое описание}`

**ПАЙПЛАЙН (ручной режим, любой стейт):**
1. Пользователь: "Альтернативы" → dispatch J (НЕ в фоне)
2. J генерирует → показывает ПОЛНЫЙ REPORT пользователю
3. Добавляет в alternatives.md (кумулятивно, с разделителем `---` и датой/стейтом)
4. Git commit (если сохранено): `alt({slug}): manual — {краткое описание}`

**ПРАВИЛО КУМУЛЯТИВНОСТИ:**
- alternatives.md НЕ перезаписывается, а дополняется
- Каждый запуск J добавляет новую секцию с заголовком `## Сессия: {дата} | Стейт: {STATE} | Режим: {AUTO/MANUAL}`

**ПРАВИЛО ИНТЕГРАЦИИ:**
- Если пользователь выбрал альтернативу → пометить в alternatives.md: `USED IN: {block_type} ({дата})`

---

#### F) Simulation Pipeline (субагент P)

**ЦЕЛЬ:** Протестировать текст на виртуальных читателях. Полный протокол — в `agents/P_reader_simulation.md` (секция 7.16).

**ПАЙПЛАЙН:**
1. Главный агент генерирует 5-8 персон → показывает пользователю
2. Dispatch 5-8 субагентов P ПАРАЛЛЕЛЬНО
3. Сборка SIMULATION REPORT (формат — в `agents/P_reader_simulation.md`)
4. По вердикту: PASS → FINAL SELF-CHECK / NEEDS_FIX → решение пользователя / CRITICAL_FIX → обязательные правки
5. Лимит итераций: макс. 2

---

#### G) Review Pipeline (субагент Q)

**ПАЙПЛАЙН:**
1. Dispatch Q с текстом final.md → FRESH EYES REPORT
2. Показать пользователю → спросить какие замечания принять
3. Принятые → точечные правки в REVIEW
4. Q запускается ОДИН раз за REVIEW

---

#### H) Mini Fresh Eyes Pipeline (субагент R)

**ПАЙПЛАЙН:**
1. Автоматический dispatch в 3 точках EXECUTION
2. Все OK → одна строка: "Mini Fresh Eyes #{N}: ✓ OK"
3. Есть ⚠️ → показать REPORT → спросить: "Исправить или продолжить?"
4. R = ADVISORY, не блокирует процесс
