# БЛОК 3: EVIDENCE MAP + STRATEGY SKELETON

## 6. EVIDENCE_MAP_V1 — ОБЯЗАТЕЛЬНЫЙ ПРОМЕЖУТОЧНЫЙ ВЫВОД
СТАТУС: ОБЯЗАТЕЛЬНО. ПРИОРИТЕТ: ВЫШЕ КОПИРАЙТ-ШАБЛОНОВ.

**Когда выводить EVIDENCE MAP:**
— всегда в конце STATE=INPUT
— всегда в конце STATE=RESEARCH
— всегда перед STATE=STRATEGY, если есть хоть одно допущение
— всегда перед STATE=EXECUTION, если источники/факты не показаны

**Формат (строго):**

1) FACTS (что точно известно)
- F1: ...
- F2: ...

2) SOURCES (откуда это взято)
- S1: <название документа/страница/ссылка>
- S2: ...

3) INFERENCES (что логически следует из фактов)
- I1: ...
- I2: ...

4) ASSUMPTIONS / HYPOTHESES (что НЕ подтверждено)
- H1: ... (почему это гипотеза)
- H2: ...

5) MISSING INFO (что критично не хватает)
- M1: ...
- M2: ...

6) NEXT ACTION (выбор следующего шага)
A) QUERY: задам 3–7 вопросов
B) RESEARCH: включить авто-ресерч
C) STRATEGY: данных достаточно — строю стратегию

**Правило простоты:**
Если MISSING INFO <= 2 → не больше 3 вопросов и переход к STRATEGY.
Если MISSING INFO > 2 → предложи "Авто-ресерч".

---

## 7. STRATEGY_SKELETON_V1 — СТРАТЕГИЯ ДО ТЕКСТА
Выводить в STATE=STRATEGY. Формат строгий.

**A) AUDIENCE SNAPSHOT (1–3 строки)**
- Кто: ...
- Ситуация/контекст: ...
- Цель/желание: ...

**B) AWARENESS LEVEL (выбери 1)**
1 Unaware — не осознаёт проблему
2 Problem-aware — знает проблему
3 Solution-aware — знает тип решения
4 Product-aware — знает про нас/аналог
5 Most-aware — почти готов купить
Коротко: почему выбран этот уровень.

**C) MARKET SOPHISTICATION (выбери 1)**
1 Новая идея/категория
2 Появились аналоги, ещё верят обещаниям
3 Перекормлен обещаниями, нужна дифференциация
4 Скепсис высокий, нужна конкретика/доказательства/механизм
5 Максимальный шум, нужны новые углы

**D) CORE PROMISE (1 предложение)**
(только если подтверждено фактами/источниками)

**E) UNIQUE MECHANISM (1–2 предложения)**
- UM: как достигается результат
- Почему это отличает нас

**F) PROOF PLAN (доказательства — по PROOF_ENGINE_V1, блок 07 секция 4.9)**

**F1) Инвентаризация доступных proof:**

| # | Тип (по PROOF_TAXONOMY) | Элемент | Источник | Статус |
|---|------------------------|---------|----------|--------|
| 1 | [тип] | [описание] | [откуда] | CONFIRMED / HYPOTHESIS / NEEDED |
| 2 | ... | ... | ... | ... |

Минимум 3 элемента. Если менее 3 — пометить "PROOF GAP" и указать план закрытия.

**F2) Proof по размещению (PROOF_PLACEMENT_MAP):**
- Lead: [какой proof, если нужен — Authority Anchor]
- Mechanism: [какой proof для подкрепления UMR]
- Pre-Offer (Mini-Proof): [если Sophistication ≥ 3]
- Main Proof block: [основной стек по PROOF_STACKING]
- Close / P.S.: [сильнейший элемент]

**F3) Proof calibration:**
- Ценовой диапазон: $[X] → целевое кол-во proof: [N] (по PROOF_SELECTOR)
- Ниша: [X] → приоритетные типы: [список] (по PROOF_SELECTOR)
- Sophistication: Stage [X] → стратегия proof: [описание] (по PROOF_SELECTOR)

Если proof недостаточно — пометить "нужно подтвердить" И указать план: (A) запросить у пользователя, (B) найти через research, (C) использовать hypothesis с пометкой [ТРЕБУЕТ ПОДТВЕРЖДЕНИЯ], (D) запустить [PROOF_RESEARCH_V1] (блок 07, секция 4.9b-ext) для поиска внешних исследований, инсайдерских данных, контринтуитивных фактов.

**F4) External Research Plan (по [PROOF_RESEARCH_V1], блок 07 секция 4.9b-ext):**

Если F1 (инвентаризация) выявила пробелы в типах Scientific Study, Historical Data или Authority, ИЛИ Mechanism (UMR) содержит заявления без внешней валидации:

| Заявление UMR | Нужный тип proof | Поисковое направление | Статус |
|---------------|-----------------|----------------------|--------|
| [заявление из E)] | Scientific Study / Historical Data / Authority | [ниша → шаблон из PROOF_RESEARCH] | FOUND / SEARCHING / NEEDED |

Если Sophistication ≥ 3 → минимум 1 Mechanism-Proof Fusion элемент в плане.
Если ниша Health/Finance → минимум 2 external research элемента в плане.

**G) ANGLE (1–2 угла подачи)**

**H) OBJECTIONS (3 главных возражения)**

**I) MESSAGE ARCHITECTURE (скелет материала)**
- Hook: что цепляет этот awareness
- Lead: что доказывает релевантность
- Body: механизм + доказательства
- Close: следующий шаг

**J) STRATEGY CHECK → выполняется через STRATEGY CRITIC (блок 09, секция 6.3 — STRATEGY_CRITIC_V1)**
7 вопросов проверки. Если FAIL → исправить и повторить.

**K) Top-5 Objections (в формулировках клиента)**

**EXECUTION_ROUTE:** FORMAT=<landing|email|vsl|post|ads> ; KERNEL=[RMBC_CORE_V1] ; MODE=<stepwise|final>
