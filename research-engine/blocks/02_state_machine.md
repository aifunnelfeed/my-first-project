# БЛОК 2: СТЕЙТ-МАШИНА (6 States + Transitions + Dispatch + Pipelines)

## РАЗДЕЛ 1: СТЕЙТ-МАШИНА

### 1.1. ОПРЕДЕЛЕНИЕ СТЕЙТОВ
КОД ДОСТУПА: [RESEARCH_STATES_V1]

```
INPUT → COLLECTION → SYNTHESIS → SIMULATION → VALIDATION → DELIVERY
```

**STATE=INPUT — Что исследуем**
- Приём данных от пользователя: ниша, продукт, ЦА, ссылки, файлы
- HYPOTHESIS-HEAVY detection (протокол в блоке 03)
- Выбор глубины: QUICK / STANDARD / DEEP
- Формирование Research Brief
- Выход: `research_brief.md`
- Автозагрузка: блоки 01 + 03

**STATE=COLLECTION — Сбор сырых данных**
- Волна 1 (параллельно): dispatch A + B + C
- Волна 2 (после Волны 1, параллельно друг другу): dispatch S (нужен выход A) + T (нужен выход B)
- Волна 3 (после Волны 2): dispatch H (Assembler) с входами A+B+C+S+T
- DATA_CONFIDENCE_CHECK после H
- Показ пользователю → фильтрация → одобрение
- Выход: `collection_raw.md` → `collection.md`
- Автозагрузка: блоки 01 + 02 + 04

**STATE=SYNTHESIS — Интерпретация данных**
- Главный агент (НЕ субагенты) выполняет интеллектуальную работу:
  - JTBD Decoder (полная карта работ с приоритизацией)
  - Schwartz Matrix (координаты клиента)
  - Unfair Advantage Mining (поиск УТП)
  - Scene Bank (минимум 12 сцен)
  - Belief Map (карта убеждений ЦА)
  - Decision Journey (путь принятия решения)
  - Objection Tree (иерархия возражений)
- Опционально: dispatch U (Belief Mapper) для сложных ниш (Sophistication 3+)
- Выход: `synthesis.md`
- Автозагрузка: блоки 01 + 02 + 05

**STATE=SIMULATION — Проверка на виртуальных аватарах**
- ПРОПУСКАЕТСЯ при глубине QUICK
- Генерация 5-8 персон (STANDARD) или 8-12 (DEEP) из данных synthesis.md
- Dispatch W (Persona Simulator) для каждой стандартной персоны
- Dispatch V (Adversarial Persona) для 1-2 скептиков (STANDARD) или 2-3 (DEEP)
- 3 теста на каждую персону:
  1. Problem Recognition Test
  2. Mechanism Credibility Test
  3. Offer Attractiveness Test
- Агрегация результатов: консенсус, расхождения, слепые зоны
- Выход: `simulation_report.md`
- Автозагрузка: блоки 01 + 02 + 06

**STATE=VALIDATION — Перекрёстная проверка**
- Cross-validation: COLLECTION data vs SIMULATION results
- Final Confidence Scoring по каждому блоку данных
- Gap Analysis: что не покрыто, что требует подтверждения
- Hypothesis Registry: обновление статусов (CONFIRMED / LIKELY / NEEDS_DATA / DISPROVED)
- Показ пользователю → пользователь дополняет / подтверждает / корректирует
- Выход: обновлённый `collection.md` + `validation_report.md`
- Автозагрузка: блоки 01 + 02 + 07

**STATE=DELIVERY — Упаковка**
- Сборка секционного `research_pack/` (11 файлов)
- Генерация `meta.md` с маппингом для Copycraft
- Опционально: HTML-отчёт
- Git commit
- Выход: `research_pack/` + опционально HTML
- Автозагрузка: блоки 01 + 02 + 08

---

### 1.2. ПРАВИЛА ПЕРЕХОДОВ
КОД ДОСТУПА: [TRANSITION_RULES_V1]

```
INPUT → COLLECTION            (всегда, после формирования research_brief.md)
COLLECTION → SYNTHESIS         (после одобрения collection.md пользователем)
SYNTHESIS → SIMULATION         (если глубина != QUICK)
SYNTHESIS → VALIDATION         (если глубина == QUICK — пропуск SIMULATION)
SIMULATION → VALIDATION        (всегда)
VALIDATION → DELIVERY          (после подтверждения пользователем)
```

**BACKTRACK:** Разрешён из любого стейта в любой предыдущий. При бэктреке:
1. Сбросить все стейты после целевого в state.md
2. Сохранить существующие файлы (не удалять — пометить как outdated)
3. Показать пользователю: "Откат на {стейт}. Данные после этого стейта будут перегенерированы."

---

### 1.3. КЛЮЧЕВЫЕ ПРАВИЛА
КОД ДОСТУПА: [STATE_RULES_V1]

**ATOMICITY RULE:** Один стейт за одно сообщение. Нельзя выполнить COLLECTION и SYNTHESIS в одном ответе.

**STATE DECLARATION:** Каждый ответ начинается с:
```
**STATE: {текущий стейт}**
```

**STATE PERSISTENCE:** После каждого перехода — обновить state.md:
1. Пометить завершённый стейт галочкой [x]
2. Обновить "Текущий стейт"
3. Обновить "Последнее обновление"

**USER APPROVAL GATES:**
- COLLECTION → SYNTHESIS: пользователь должен одобрить collection.md
- VALIDATION → DELIVERY: пользователь должен подтвердить готовность
- Все остальные переходы — автоматические (но state.md обновляется)

---

## РАЗДЕЛ 2: DISPATCH ПРАВИЛА

### 2.1. ОБЩИЕ ПРАВИЛА СУБАГЕНТОВ
КОД ДОСТУПА: [RESEARCH_SUBAGENT_RULES_V1]

**8 правил для ВСЕХ субагентов:**

1. **Нет доступа к blocks/.** Субагенты НЕ читают блоки автоматически — все инструкции передаются в промпте.
2. **Контекст проекта: 3-5 предложений.** Из research_brief.md — только самое важное, НЕ весь файл.
3. **Строгий формат вывода.** Каждый субагент возвращает ответ ТОЧНО по шаблону из своей секции.
4. **Обработка ошибок.** Если инструмент недоступен → `STATUS: TOOL_UNAVAILABLE` + описание + частичные результаты.
5. **Запрет на выдумку.** Запрещено придумывать факты. Нет данных → `НЕ НАЙДЕНО`.
6. **Инструмент запуска.** Claude Code Agent tool (`subagent_type="general-purpose"`). Параллельные dispatch'и когда задачи независимы.
7. **Результаты показываются пользователю ПЕРЕД интеграцией** в файлы проекта.
8. **Язык.** Субагент работает на языке проекта.

---

### 2.2. РЕЕСТР СУБАГЕНТОВ
КОД ДОСТУПА: [RESEARCH_SUBAGENT_REGISTRY_V1]

| ID | Название | Файл промпта | Когда | Зависимости | Что возвращает |
|----|----------|-------------|-------|-------------|----------------|
| A | VOC Mining | `agents/A_voc_mining.md` | COLLECTION Wave 1 | Нет | Теггированные VOC-цитаты + Belief-revealing VOC |
| B | Competitor + Market | `agents/B_competitor_market.md` | COLLECTION Wave 1 | Нет | Таблицы конкурентов + STAT + Pricing Landscape |
| C | Curiosity + Corruption | `agents/C_curiosity_corruption.md` | COLLECTION Wave 1 | Нет | Углы для Big Idea |
| S | Audience Depth | `agents/S_audience_depth.md` | COLLECTION Wave 2 | Выход A | AUDIENCE DEPTH PROFILE (8 секций + Decision Journey Signals) |
| T | Trend & Market Dynamics | `agents/T_trend_dynamics.md` | COLLECTION Wave 2 | Выход B | Тренды, сезонность, рост/падение сегментов |
| H | Research Assembler | `agents/H_research_assembler.md` | COLLECTION Wave 3 | Выходы A+B+C+S+T | collection_raw.md + SUMMARY |
| U | Belief Mapper | `agents/U_belief_mapper.md` | SYNTHESIS (опцион.) | collection.md | Structured Belief Map |
| V | Adversarial Persona | `agents/V_adversarial_persona.md` | SIMULATION | synthesis.md | Vulnerability Map + attack vectors |
| W | Persona Simulator | `agents/W_persona_simulator.md` | SIMULATION | synthesis.md | Per-persona scorecard (3 теста) |

---

### 2.3. DISPATCH ПРАВИЛА ПО СТЕЙТАМ
КОД ДОСТУПА: [RESEARCH_DISPATCH_V1]

**STATE=COLLECTION:**

```
ВОЛНА 1 (параллельно):
  dispatch A (VOC Mining) — brief-context
  dispatch B (Competitor + Market) — brief-context
  dispatch C (Curiosity + Corruption) — brief-context

  ↓ Ожидание завершения A+B+C

ВОЛНА 2 (параллельно друг другу):
  dispatch S (Audience Depth) — выход A + brief-context + HYPOTHESIS-HEAVY флаг
  dispatch T (Trend Dynamics) — выход B + brief-context

  ↓ Ожидание завершения S+T

ВОЛНА 3:
  dispatch H (Research Assembler) — входы A+B+C+S+T

  ↓ H возвращает collection_raw.md

DATA_CONFIDENCE_CHECK_V2 (главный агент, не субагент)
  ↓
Показ пользователю → фильтрация → collection.md
```

**FALLBACK (Agent tool недоступен):**
- A+B+C → серийный ресерч в основном агенте (WebSearch)
- S → сокращённый AUDIENCE_DEPTH in-context (True Fears 2 слоя, Internal Dialogue 5 фраз, Failed Methods 3, Decision Model)
- T → сокращённый TREND ANALYSIS in-context (3 тренда, 1 сезонность)
- H → главный агент собирает collection_raw.md вручную

**STATE=SYNTHESIS:**
- Главный агент выполняет все интерпретации (блок 05)
- Опционально: dispatch U (Belief Mapper) если Sophistication 3+ или пользователь запросил
- Fallback U: главный агент строит Belief Map самостоятельно

**STATE=SIMULATION:**
1. Главный агент генерирует 5-8 персон → показывает пользователю для одобрения
2. Параллельный dispatch: 5-8 субагентов W + 1-2 субагентов V
3. Сборка SIMULATION REPORT
4. Fallback: 3 персоны in-context (1 primary + 1 secondary + 1 skeptic)

**STATE=VALIDATION:**
- Главный агент выполняет cross-validation (блок 07)
- Субагенты не используются

**STATE=DELIVERY:**
- Главный агент собирает research_pack/ (блок 08)
- Субагенты не используются

---

## РАЗДЕЛ 3: ПАЙПЛАЙНЫ

### 3.1. Collection Pipeline
КОД ДОСТУПА: [COLLECTION_PIPELINE_V1]

1. Субагенты A+B+C+S+T возвращают сырые данные → dispatch H
2. H дедуплицирует, кросс-проверяет, форматирует → `collection_raw.md`
3. Главный агент записывает collection_raw.md и показывает пользователю с маркерами надёжности
4. Пользователь решает по каждому факту:
   - ✅ Оставить (одобрено)
   - ❌ Убрать (нерелевантно/неточно)
   - ✏️ Исправить (пользователь корректирует)
   - 📌 Добавить (свои данные — автоматически S1)
5. Одобренные данные → `collection.md` (финальный формат с тегами)
6. DATA_CONFIDENCE_CHECK_V2
7. Git commit: `research({slug}): collection`

**ФОРМАТ collection_raw.md:**
```markdown
# Сырой ресерч: {название проекта}
## Дата: {дата}
## Источник: A (VOC) + B (Market) + C (Curiosity) + S (Audience Depth) + T (Trends)

---
{объединённые результаты — каждый факт с тегами [TYPE|SOURCE|RELIABILITY|RELEVANCE]}
---

## SUMMARY
- Всего фактов: {N}
- ★★★ CONFIRMED: {N}
- ★★ CROSS-CHECKED: {N}
- ★ SINGLE: {N}
- ⚠️ HYPOTHESIS: {N}
- Рекомендация: {что перепроверить / чего не хватает}
```

---

### 3.2. Simulation Pipeline
КОД ДОСТУПА: [SIMULATION_PIPELINE_V1]

1. Главный агент генерирует персоны из synthesis.md → показывает пользователю
2. Пользователь одобряет / корректирует набор персон
3. Параллельный dispatch: W (стандартные персоны) + V (скептики)
4. Сборка SIMULATION REPORT:
   - Per-persona scorecards (3 теста × 5 баллов)
   - Aggregate: % pass rate, consensus objections, consensus strengths
   - Red flags (scores < 2)
   - Vulnerability Map (от adversarial personas)
   - Recommendations
5. Показ пользователю
6. Git commit: `research({slug}): simulation`

---

### 3.3. Обработка тупиков (Deadlock Recovery)

**Субагент вернул TOOL_UNAVAILABLE:**
- Зафиксировать в state.md (колонка "Статус" = TOOL_UNAVAILABLE)
- Использовать fallback (in-context версию)
- Предупредить пользователя: "Субагент {X} не смог использовать WebSearch. Данные неполные."

**DATA_CONFIDENCE_CHECK = LOW (≥ 3 категорий):**
```
⚠️ DATA CONFIDENCE: LOW ({N} из 7 категорий с низкой уверенностью)

Варианты:
A) Дополните данные — скажите, что можете предоставить по: {список LOW}
B) Продолжить с гипотезами — LOW-данные пометятся [HYPOTHESIS] в synthesis.md
C) Запросить данные у эксперта — я сформирую список вопросов
D) Дополнительный ресерч по LOW-категориям (повторный dispatch A/B/C/S/T)
```

**SIMULATION все персоны < 2 баллов по тесту:**
- СТОП — не переходить в VALIDATION
- Показать: "Симуляция выявила критические проблемы: {описание}"
- Предложить: A) Вернуться в SYNTHESIS, B) Скорректировать позиционирование, C) Запросить данные у пользователя
