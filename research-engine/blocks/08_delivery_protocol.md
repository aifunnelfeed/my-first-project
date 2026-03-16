# БЛОК 8: ПРОТОКОЛ ДОСТАВКИ (Delivery Protocol)

## НАЗНАЧЕНИЕ

Сборка финального research_pack/ (11 файлов) из данных всех предыдущих стейтов. Опциональная генерация HTML-отчёта. Подготовка к передаче в Copycraft.

**ВХОД:** synthesis.md + collection.md + simulation_report.md + validation_report.md
**ВЫХОД:** research_pack/ (11 файлов) + опционально HTML-отчёт
**ЗАГРУЗКА:** STATE=DELIVERY → блоки 01 + 02 + 08

---

## РАЗДЕЛ 1: ПАЙПЛАЙН СБОРКИ

### 1.1. ASSEMBLY PIPELINE
КОД ДОСТУПА: [RESEARCH_PACK_ASSEMBLY_V1]

**ПОТОК ДАННЫХ:**

```
collection.md ──────────┐
                        ├──→ [Группа A] audience.md, market.md
synthesis.md ───────────┤
                        ├──→ [Группа B] jtbd.md, belief_map.md, objection_tree.md
                        ├──→ [Группа C] mechanism_inputs.md, scene_bank.md, evidence_map.md
                        │
simulation_report.md ───┤
                        ├──→ [Группа D] simulation_report.md (копия)
validation_report.md ───┤
                        ├──→ hypothesis_registry.md
                        │
все файлы ──────────────└──→ meta.md (последний — нужны данные из всех)
```

**ПОРЯДОК СБОРКИ:**

| Шаг | Группа | Файлы | Источник |
|-----|--------|-------|----------|
| 1 | B | jtbd.md, belief_map.md, objection_tree.md | synthesis.md |
| 2 | C | mechanism_inputs.md, scene_bank.md, evidence_map.md | synthesis.md |
| 3 | A | audience.md, market.md | collection.md + synthesis.md |
| 4 | D | simulation_report.md, hypothesis_registry.md | simulation_report.md + validation_report.md |
| 5 | — | meta.md | все предыдущие |

**ПРАВИЛА СБОРКИ:**
1. Группы B и C можно собирать параллельно (независимы).
2. Группа A требует данные из collection.md И synthesis.md (Decision Journey).
3. meta.md собирается ПОСЛЕДНИМ — содержит ссылки на все файлы.
4. Каждый файл — самодостаточный. Читатель не должен открывать другие файлы для понимания.
5. Теги источников ([VOC], [RESEARCH], [SIM], [HYPOTHESIS]) сохраняются в финальных файлах.

---

## РАЗДЕЛ 2: СПЕЦИФИКАЦИИ ФАЙЛОВ

### 2.1. FILE SPECIFICATIONS
КОД ДОСТУПА: [RESEARCH_PACK_SPECS_V1]

#### 1. meta.md

```markdown
# Research Pack: {название проекта}

## Мета-данные
- **Дата сборки:** {дата}
- **Глубина:** {QUICK / STANDARD / DEEP}
- **Общая уверенность:** {HIGH / MED / LOW}
- **Гипотезы:** {confirmed}/{total} ({rejected} отклонено, {open} открыто)
- **Персоны (simulation):** {N} ({PASS rate}%) | или "Simulation skipped (QUICK)"

## Состав пакета
| # | Файл | Статус | Ключевое |
|---|------|--------|----------|
| 1 | jtbd.md | ✅ | Primary Job: {формулировка} |
| 2 | audience.md | ✅ | {N} секций, Decision Model: {тип} |
| 3 | belief_map.md | ✅ | {N} current → {M} to break → {K} to build |
| 4 | objection_tree.md | ✅ | {N} возражений, P1: {топ-возражение} |
| 5 | market.md | ✅ | {N} конкурентов, Soph: {уровень} |
| 6 | mechanism_inputs.md | ✅ | Mode: {Hidden/Teased/Revealed} |
| 7 | scene_bank.md | ✅ | {N} сцен, {M} категорий |
| 8 | evidence_map.md | ✅ | {N} facts, {M} missing |
| 9 | hypothesis_registry.md | ✅ | {N} confirmed, {M} open |
| 10 | simulation_report.md | ✅/⏭️ | PASS rate: {N}% | или "skipped" |

## Copycraft Mapping
{таблица из РАЗДЕЛ 4}

## Известные ограничения
- {LOW-категории из Confidence Scorecard}
- {OPEN гипотезы — кратко}
- {DATA GAPs — кратко}
```

**Минимум:** Все поля заполнены. Критичный файл.

---

#### 2. jtbd.md
**Источник:** synthesis.md → Job Map (секция 2.1)
**Содержит:** Primary Job (формулировка), Secondary Jobs (таблица), 4 Forces Summary, Job Prioritization, Problem Archetype
**Минимум:** Primary Job + 4 Forces

#### 3. audience.md
**Источник:** collection.md (Audience Depth S) + synthesis.md (Decision Journey)
**Содержит:** True Fears (4 слоя), Dream Dictionary, Shock Events, Failed Methods, Internal Dialogue, Decision Model, RAS Triggers, Anti-Segment, Decision Journey (6 этапов)
**Минимум:** ≥5 секций из 9 заполнены. True Fears + Internal Dialogue + Decision Model обязательны.

#### 4. belief_map.md
**Источник:** synthesis.md → Belief Map (секция 3.1) или выход субагента U
**Содержит:** Current Beliefs, Beliefs to Break, Beliefs to Build, Belief Tension Map. При DEEP: + Clusters, Counter-Evidence Sensitivity, Belief-to-Copy Mapping
**Минимум:** ≥5 current beliefs + ≥3 beliefs to build

#### 5. objection_tree.md
**Источник:** synthesis.md → Objection Tree (секция 3.3)
**Содержит:** 5 категорий (цена/доверие/время/релевантность/риск), иерархические возражения, Priority Matrix (P1/P2/P3), контр-стратегии
**Минимум:** ≥5 возражений, ≥3 категории

#### 6. market.md
**Источник:** collection.md (Competitor Analysis B + Trends T)
**Содержит:** Competitor Table, Pricing Landscape, Competitor Positioning Matrix, Системные слабости. Тренды рынка, Сезонность, Растущие/Падающие сегменты, Регуляторный ландшафт, Timing Windows
**Минимум:** ≥3 конкурента + pricing + ≥1 тренд

#### 7. mechanism_inputs.md
**Источник:** synthesis.md → Mechanism Inputs (секция 4.2)
**Содержит:** Unfair Advantage (3 слоя), Candidate Mechanism Name, Copycat Test, Curiosity Angles, Corruption Vectors, Mechanism Mode Recommendation
**Минимум:** Unfair Advantage (≥2 слоя) + Mode Recommendation

#### 8. scene_bank.md
**Источник:** synthesis.md → Scene Bank Expansion (секция 4.1)
**Содержит:** Категоризированные сцены (PAIN/DESIRE/TRIGGER/CONTRAST/IDENTITY) с рекомендованным блоком текста
**Минимум:** 8 (QUICK), 12 (STANDARD), 15 (DEEP)

#### 9. evidence_map.md
**Источник:** synthesis.md → Evidence Map (секция 4.3)
**Содержит:** Facts (с тегами), Inferences, Assumptions, Missing
**Минимум:** ≥10 FACTS

#### 10. hypothesis_registry.md
**Источник:** validation_report.md → Hypothesis Registry
**Содержит:** Все гипотезы с финальными статусами (CONFIRMED/REJECTED/REVISED/OPEN), доказательства, действия
**Минимум:** Реестр существует (может быть пустым если гипотез не было)

#### 11. simulation_report.md
**Источник:** Копия simulation_report.md из STATE=SIMULATION
**Содержит:** Scorecard, Vulnerability Map, Detailed Persona Reports, Recommendations
**Минимум:** Файл существует. Для QUICK: содержит одну строку "Simulation skipped (QUICK depth)."

---

## РАЗДЕЛ 3: ЧЕКЛИСТ КАЧЕСТВА

### 3.1. DELIVERY QUALITY GATE
КОД ДОСТУПА: [DELIVERY_QUALITY_GATE_V1]

**ЧЕКЛИСТ (перед показом пользователю):**

| # | Файл | Критичность | Проверка | Статус |
|---|------|------------|----------|--------|
| 1 | meta.md | 🔴 CRITICAL | Все поля + маппинг | {PASS/FAIL} |
| 2 | jtbd.md | 🔴 CRITICAL | Primary Job + 4 Forces | {PASS/FAIL} |
| 3 | audience.md | 🔴 CRITICAL | ≥5 секций, обязательные заполнены | {PASS/FAIL} |
| 4 | belief_map.md | 🔴 CRITICAL | ≥5 current + ≥3 to build | {PASS/FAIL} |
| 5 | objection_tree.md | 🔴 CRITICAL | ≥5 возражений, ≥3 категории | {PASS/FAIL} |
| 6 | market.md | 🟡 NON-CRITICAL | ≥3 конкурента + pricing | {PASS/FAIL} |
| 7 | mechanism_inputs.md | 🟡 NON-CRITICAL | Unfair Advantage ≥2 слоя | {PASS/FAIL} |
| 8 | scene_bank.md | 🟡 NON-CRITICAL | ≥минимум по глубине | {PASS/FAIL} |
| 9 | evidence_map.md | 🟡 NON-CRITICAL | ≥10 FACTS | {PASS/FAIL} |
| 10 | hypothesis_registry.md | 🟢 MINOR | Существует | {PASS/FAIL} |
| 11 | simulation_report.md | 🟢 MINOR | Существует | {PASS/FAIL} |

**БЛОКИРУЮЩЕЕ ПРАВИЛО:** Если ЛЮБОЙ 🔴 CRITICAL файл = FAIL → DELIVERY невозможен. Показать пользователю что не так и предложить:
- A) Дополнить данные
- B) Backtrack
- C) Принять с пробелами (пользователь подтверждает)

**CROSS-FILE CONSISTENCY CHECK (5 проверок):**

| # | Что проверяем | Файлы | Что ищем |
|---|-------------|-------|---------|
| 1 | Primary Job в jtbd ↔ Target в audience | jtbd.md ↔ audience.md | Одна и та же аудитория? |
| 2 | Beliefs to Break ↔ Objections P1 | belief_map.md ↔ objection_tree.md | Belief порождает objection? |
| 3 | Mechanism Mode ↔ Sophistication | mechanism_inputs.md ↔ jtbd.md | Mode соответствует Soph? |
| 4 | Scene Bank scenes ↔ Audience Fears | scene_bank.md ↔ audience.md | Сцены отражают страхи? |
| 5 | Evidence MISSING ↔ Hypothesis OPEN | evidence_map.md ↔ hypothesis_registry.md | Пробелы покрыты гипотезами? |

Если найдено противоречие → WARNING (не блокирует, но показать пользователю).

---

## РАЗДЕЛ 4: ПЕРЕДАЧА В COPYCRAFT

### 4.1. COPYCRAFT HANDOFF
КОД ДОСТУПА: [COPYCRAFT_HANDOFF_V1]

**МАППИНГ (какой блок текста загружает какие файлы):**

| Блок текста Copycraft | Файлы research_pack/ | Что извлекать |
|----------------------|---------------------|--------------|
| **Headline** | jtbd.md + belief_map.md + audience.md | Primary Job, RAS Triggers, Beliefs to Break (топ) |
| **Lead** | scene_bank.md + audience.md + evidence_map.md | PAIN/TRIGGER сцены, True Fears, Internal Dialogue, якорные факты |
| **Story** | mechanism_inputs.md + scene_bank.md | Unfair Advantage (Слой 1 — история), IDENTITY сцены |
| **Mechanism** | mechanism_inputs.md + market.md | Unfair Advantage (Слой 2), Curiosity Angles, Mechanism Mode, конкуренты (слабости) |
| **Proof** | evidence_map.md + market.md + simulation_report.md | FACTS (CORE), Competitor data, Vulnerability Map (что усилить) |
| **Offer** | objection_tree.md + audience.md + market.md | P1/P2 objections + контр-стратегии, Decision Model, Pricing Landscape |
| **Close** | audience.md + scene_bank.md + belief_map.md | Dream Dictionary, DESIRE сцены, Beliefs to Build |
| **FAQ** | objection_tree.md + audience.md | P2/P3 objections, Decision Model (вопросы по типу) |

**3 РЕЖИМА HANDOFF:**

| Режим | Описание | Записывается в meta.md |
|-------|---------|----------------------|
| **Standalone** | Research pack — самостоятельный продукт. Не передаётся в Copycraft. | `format: standalone` |
| **Integration** | Research pack передаётся в Copycraft как INPUT. Copycraft загружает файлы поблочно. | `format: copycraft-integration` |
| **Both** | Оба варианта. Pack = продукт + INPUT для Copycraft. | `format: both` |

**ПРАВИЛО:** Режим определяется в STATE=INPUT (поле "Формат" в state.md). Если не указан — спросить пользователя при DELIVERY.

---

## РАЗДЕЛ 5: HTML-ОТЧЁТ (опционально)

### 5.1. HTML REPORT
КОД ДОСТУПА: [RESEARCH_HTML_REPORT_V1]

**ТРИГГЕР:** После сборки research_pack/ спросить: **"Собрать HTML-отчёт для GitHub Pages?"**

**КОМАНДА:**
```bash
python scripts/build_research_report.py {project_slug} --input research_pack/ --title "{название проекта}"
```

**ВЫХОД:** `docs/{project}/research.html`

**СЕКЦИИ HTML-ОТЧЁТА:**

| # | Секция | Источник | Визуализация |
|---|--------|----------|-------------|
| 1 | Executive Summary | meta.md | Карточка проекта + уверенность |
| 2 | Целевая аудитория | audience.md | True Fears + Decision Model + RAS |
| 3 | Job Map | jtbd.md | 4 Forces diagram |
| 4 | Карта убеждений | belief_map.md | Current → Break → Build (стрелки) |
| 5 | Возражения | objection_tree.md | Priority Matrix (цветовая шкала) |
| 6 | Рынок | market.md | Competitor table + тренды |
| 7 | Механизм | mechanism_inputs.md | Unfair Advantage + Curiosity |
| 8 | Симуляция | simulation_report.md | Scorecard + Vulnerability Map |

**Шаблон:** `templates/research_report.html` (Jinja2 + встроенный CSS, тёмная тема)
**Скрипт:** `scripts/build_research_report.py`

**ПРИМЕЧАНИЕ:** Скрипт и шаблон создаются отдельно (не в этом блоке). При отсутствии — пропустить HTML и сообщить пользователю.

---

## РАЗДЕЛ 6: GIT И ПРАВИЛА

### 6.1. GIT
КОД ДОСТУПА: [DELIVERY_GIT_V1]

**Формат коммита:**
```
research({проект}): pack — {N} sections, confidence {HIGH/MED/LOW}
```

**Примеры:**
```
research(nutriciologia): pack — 11 sections, confidence HIGH
research(nutriciologia): pack — 10 sections, confidence MED (simulation skipped)
```

**HTML-отчёт (отдельный коммит):**
```
research({проект}): HTML report — {N} sections
```

### 6.2. PACK SUMMARY (показать пользователю перед коммитом)

```markdown
📦 RESEARCH PACK READY

Проект: {название}
Глубина: {QUICK / STANDARD / DEEP}
Уверенность: {HIGH / MED / LOW}

Файлы: {N}/11
- 🔴 Critical: {все PASS? ✅ : список FAIL}
- 🟡 Important: {статус}
- 🟢 Minor: {статус}

Гипотезы: {confirmed}/{total}
Simulation: {PASS rate}% | или "skipped"

Готово к {standalone / Copycraft integration / both}
```

### 6.3. ПРАВИЛА

1. **Никогда не доставлять без одобрения.** Показать pack summary → ждать "да".
2. **Каждый файл самодостаточен.** Читатель понимает файл без контекста других файлов.
3. **Теги сохраняются.** [VOC], [RESEARCH], [SIM], [HYPOTHESIS] — в финальных файлах.
4. **meta.md — entry point.** Copycraft начинает с meta.md, затем загружает нужные файлы по маппингу.
5. **Не удалять промежуточные файлы.** collection.md, synthesis.md, simulation_report.md, validation_report.md остаются в папке проекта.
6. **State.md update.** После DELIVERY: обновить пройденные стейты, записать дату, зафиксировать финальную уверенность.
