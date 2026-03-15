### 7.10. ПРОМПТ-ШАБЛОН G: LAUNCH CRITIC (Субагент проверки перед запуском)
КОД ДОСТУПА: [SUBAGENT_G_LAUNCH_V1]

**ТРИГГЕР:** STATE=DELIVERY — после сборки final.md, перед FINAL SELF-CHECK.

**КАК ФОРМИРОВАТЬ КОНТЕКСТ (инструкция для главного агента):**
1. Из strategy.md: Awareness, Sophistication, Core Promise, UMP, UMR
2. Из brief.md: продукт, ЦА, ниша, ценовой диапазон
3. Текст: весь final.md (полный собранный текст)

**ПРОМПТ-ШАБЛОН:**

```
ЗАДАЧА: Проверь полный собранный текст (final.md) по 30 критериям Launch Checklist. ВСЕ 30 должны быть ДА для прохождения. Для каждого НЕТ — опиши проблему и предложи исправление.

КОНТЕКСТ ПРОЕКТА:
- Продукт: {1-2 предложения из brief.md}
- ЦА: {1 предложение}
- Ниша: {ниша}
- Ценовой диапазон: {цена}
- Awareness: {уровень}
- Sophistication: {стадия}
- Core Promise: {из strategy.md}
- UMP: {1 предложение}
- UMR: {название + 1 предложение}
- Value Equation (D2): {Dream Outcome, Likelihood, Time Delay, Effort}
- Speed to Value (D3): {Quick Win + Full Result}
- Guarantee Strategy (F5): {тип + формулировка}
- Mechanism Mode (I2): {Hidden / Teased / Revealed}
- Core Emotion (N): {номер + название}
- Формат: {landing/email/vsl/ads/chatbot}

ПОЛНЫЙ ТЕКСТ ДЛЯ ПРОВЕРКИ:
---
{весь final.md}
---

==============================
28 КРИТЕРИЕВ LAUNCH CHECKLIST
==============================

1. **ЦА через JTBD:** ЦА чётко определена через JTBD (не через соцдем)?
2. **Schwartz Level:** Уровень Шварца выбран правильно — лид соответствует?
3. **UMP Argumentation:** UMP раскрыт через аргументацию [UMP_ARGUMENTATION_V1]? Есть цепочка «убеждение → противоречие → аргументы → self-discovery → раскрытие»? UMP снимает вину с клиента? Если UMP декларирован без цепочки — FAIL.
4. **UMR:** UMR имеет название и 3-шаговое объяснение (что → как → почему работает)?
5. **Big Idea:** Big Idea пробивает рекламную слепоту (не "ещё один курс/метод")?
6. **Offer-Pain Match:** Оффер бьёт в текущую боль, за решение которой ЦА платит СЕЙЧАС?
7. **Value Stack:** Value Stack превышает цену в 3-5 раз (сумма элементов vs цена)?
8. **Guarantee:** Гарантия покрывает главный риск клиента (страх, который мешает купить)?
9. **Urgency:** Есть 2+ триггера срочности (дедлайн, лимит, повышение цены)?
10. **Language:** Текст звучит как разговор двух людей (не как буклет или пресс-релиз)?
11. **FAQ:** Есть ли блок FAQ (обязательно для landing/VSL)?
12. **Pain Depth:** Все 4 слоя DRE проработаны: Поверхность → Цена → Эмоция → Идентичность?
13. **Pain Budget:** Pain Budget выполнен — секция боли >= секции механизма по объёму?
14. **Story Stakes:** История прошла Stakes Checklist на 4+ из 6?
15. **Trust Account:** Trust Balance >= 3 на каждый блок? Нет Trust Killers?
16. **Proof Diversity:** Минимум 3 разных типа proof в тексте (из 10 типов таксономии)?
17. **Proof Placement:** Доказательства размещены ДО первого запроса денег (CTA #1)?
18. **Proof Specificity:** Каждый proof-элемент содержит конкретное имя/число/дату?
19. **Mechanism-Research:** Если Sophistication >= 3 или ниша Health/Finance — есть минимум 1 внешнее исследование, подкрепляющее UMR?
20. **Authority Weaving:** Credentials эксперта появляются в тексте минимум в 2 точках? Нет «резюме-стиля»? Если эксперта нет → Н/П.
21. **Zero Placeholders:** Содержит ли final.md неразрешённые плейсхолдеры `[ВСТАВИТЬ:...]`? Если ДА — FAIL. Исключение: PLACEHOLDER_OVERRIDE → WARNING.
22. **Pain Density:** Каждый абзац pain section вносит новый ракурс? Micro-relief при 5+ абзацах?
23. **Push:Pull Balance:** Push (боль/DRE) ≠ 0 И Pull (желание/DES) ≠ 0? Один = 0 → FAIL.
24. **Arrangement Coherence:** ARRANGEMENT_MODS из BRIEF выполнены? Если не указаны → Н/П.
25. **Mechanism Mode Coherence (Hormozi):** I2 из strategy.md соответствует реализации? Если не заполнен → WARNING.
26. **"Who NOT for" (Hormozi):** Секция «для кого НЕ подходит» (3-5 пунктов)? Позиция: после CTA #3 или перед P.S.?
27. **Speed to Value (Hormozi):** Quick Win + Full Result с конкретным сроком? Если D3 не заполнен → WARNING.
28. **Audience Simulation Coverage:** Если симуляция проводилась — Primary удержаны, 4 decision models обслужены? Если не проводилась → Н/П.
29. **Core Emotion Arc:** Core Emotion проходит через дугу Lead → Pain → Story → Mechanism → Close? Переключение на несвязанную эмоцию = FAIL. Если N не выбрана → FAIL.
30. **Cross-Block Repetition Scan:** Полный скан по R1-R6. Любой R1/R2/R3/R6 = FAIL. R4/R5: 1 = WARNING, 2+ = FAIL.

==============================
READER PERSPECTIVE (ADVISORY — не влияют на PASS/FAIL)
==============================

31. **Reader Experience:** Прочитай весь текст как обычный человек. Есть ли моменты «ну опять», «не верю», «хватит уже»? Цитаты.
32. **Image Repetition:** Визуальные сцены/фразы/метафоры 3+ раз? Это НЕ про дословные повторы — про повтор КАРТИНКИ.
33. **Tone Shifts:** Резкие переключения с разговорного на рекламный? Конкретные переходы.

==============================
ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ
==============================

**A) Cross-Block Consistency:**
- Core Promise в Lead = то, что Offer доставляет?
- UMP в Lead = тот же UMP в Mechanism?
- UMR одинаково описан во всех упоминаниях?
- Имена, числа, даты не противоречат друг другу?

**B) Flow между блоками:**
- Переход Lead → Story плавный?
- Переход Story → Mechanism логичный?
- Переход Mechanism → Offer естественный?
- P.S. содержит самый сильный аргумент?

==============================
ФОРМАТ ВЫВОДА (строго)
==============================

## LAUNCH REPORT: {project_name}

### VERDICT: PASS / FAIL ({кол-во ДА}/29)

### DETAILED CHECK
| # | Критерий | Результат | Комментарий |
|---|---------|-----------|-------------|
| 1 | ЦА через JTBD | ✓ / ✗ | {комментарий} |
| ... | ... | ... | ... |

### CROSS-BLOCK CONSISTENCY
| Проверка | Результат | Деталь |
|---------|-----------|--------|
| Promise Lead = Offer | ✓ / ✗ | {что совпадает/не совпадает} |
| UMP consistency | ✓ / ✗ | {детали} |
| UMR consistency | ✓ / ✗ | {детали} |
| Data consistency | ✓ / ✗ | {детали} |

### FLOW CHECK
| Переход | Оценка | Комментарий |
|---------|--------|-------------|
| Lead → Story | Smooth / Jarring | {детали} |
| Story → Mechanism | Smooth / Jarring | {детали} |
| Mechanism → Offer | Smooth / Jarring | {детали} |
| P.S. strength | Strong / Weak | {что в P.S.} |

### READER PERSPECTIVE (ADVISORY)

**Q31 — Reader Experience:**
{свободный текст}

**Q32 — Image Repetition:**
{список повторяющихся образов}

**Q33 — Tone Shifts:**
{список мест переключения тона}

### CORRECTIONS (для каждого ✗)
**Q{N} — {критерий}**
Проблема: {конкретно}
→ Исправление: {что сделать}

### STRENGTHS (3-5 пунктов)
- {сильные стороны текста в целом}

### PLACEHOLDER STATUS
- Неразрешённых плейсхолдеров: {N}
- PLACEHOLDER_OVERRIDE: {YES/NO}

### SUMMARY
{2-3 предложения}

ПРАВИЛА:
- Все 29 = ДА для PASS. Даже 1 НЕТ = FAIL. Q20 без эксперта → Н/П. Q21 с OVERRIDE → WARNING. Q24 без MODs → Н/П. Q25 без I2 → WARNING. Q27 без D3 → WARNING. Q28 без симуляции → Н/П.
- Cross-Block Consistency и Flow Check — дополнительные (не влияют на PASS/FAIL).
- Цитируй конкретные фрагменты текста.
- STRENGTHS обязательны.
```
