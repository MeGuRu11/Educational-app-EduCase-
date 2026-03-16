# ПРОМПТ ДЛЯ AI-АГЕНТА: EduCase — Реализация UI Dashboard (Студент + Преподаватель)

## Задача

Реализовать страницы **StudentDashboard (S-1)**, **MyResults (S-5)**, **TeacherDashboard (T-1)**,
**Analytics (T-6)** и **Groups (T-7)** в виде PySide6-виджетов строго по визуальному референсу
`docs/educase_ui_mockup.html`. Все цвета, отступы, радиусы и логика компонентов берутся
**только из этого файла** — он является единственным источником истины по дизайну.

**Корень проекта:** `C:\Users\user\Desktop\Program\Educational-app-EduCase-\educase\`
**Референс:** `docs/educase_ui_mockup.html` — открой и изучи перед тем, как писать код.
**Архитектура:** `docs/PROJECT_DESIGN_v2.1.md` — все экраны описаны в §8.

---

## Дизайн-токены (взяты из :root в референсе — использовать везде)

```python
# ui/styles/dashboard_theme.py
# Единый источник всех констант дизайна для Dashboard-экранов

COLORS = {
    # Акцент
    "accent":        "#0078D4",
    "accent_hover":  "#006CBD",
    "accent_light":  "#4DA3E8",
    "accent_dark":   "#005A9E",
    # Семантика
    "success":       "#107C10",
    "success_bg":    "#DFF6DD",
    "warning":       "#9D5D00",
    "warning_bg":    "#FFF4CE",
    "error":         "#C42B1C",
    "error_bg":      "#FDE7E9",
    # Фоны
    "bg":            "#F0F2F5",   # основной фон страниц
    "card":          "#FFFFFF",   # фон карточек
    "sidebar":       "#0D1B2E",   # фон сайдбара
    # Текст
    "t1":            "#1A1A2E",   # основной текст
    "t2":            "#5A6478",   # вторичный
    "t3":            "#9BA3B4",   # третичный / метки
    # Тени (передавать как stylesheet box-shadow или рисовать через QGraphicsDropShadow)
    "shadow_sm":     "0 1px 3px rgba(0,0,0,.06)",
    "shadow_md":     "0 4px 16px rgba(0,0,0,.08)",
    "shadow_lg":     "0 12px 40px rgba(0,0,0,.12)",
    # Граница
    "border":        "rgba(0,0,0,0.07)",
}

RADIUS = {
    "card":    12,   # --r: 12px
    "control": 8,
    "pill":    100,
    "badge":   6,
}

SIDEBAR_WIDTH = 240   # px
TOPBAR_HEIGHT = 60    # px
FONT = "Segoe UI Variable"
```

---

## Архитектура файлов

Создать следующие файлы (если не существуют):

```
educase/
├── ui/
│   ├── styles/
│   │   └── dashboard_theme.py        ← токены выше
│   ├── components/
│   │   ├── stat_card.py              ← StatCard (универсальная)
│   │   ├── case_card.py              ← CaseCard (для S-1, S-2)
│   │   ├── continue_banner.py        ← ContinueBanner (S-1)
│   │   ├── ring_progress.py          ← RingProgress (круговой график, S-1)
│   │   ├── score_chart.py            ← ScoreChart (линейный matplotlib, S-1/S-5)
│   │   ├── activity_feed.py          ← ActivityFeed (T-1)
│   │   ├── group_card.py             ← GroupCard (T-1, T-7)
│   │   ├── heatmap_widget.py         ← HeatmapWidget (T-6)
│   │   └── weak_tasks_list.py        ← WeakTasksList (T-6)
│   └── windows/
│       ├── student_dashboard.py      ← S-1 StudentDashboard
│       ├── student_results.py        ← S-5 MyResults
│       ├── teacher_dashboard.py      ← T-1 TeacherDashboard
│       ├── teacher_analytics.py      ← T-6 Analytics
│       └── teacher_groups.py         ← T-7 Groups
```

---

## КОМПОНЕНТЫ — детальные спецификации

### 1. StatCard (`ui/components/stat_card.py`)

HTML-референс: `.stat-card` в educase_ui_mockup.html

```
Размер:     auto-width, height ~90px
Фон:        #FFFFFF
Радиус:     12px
Граница:    1px solid rgba(0,0,0,0.07)
Тень:       QGraphicsDropShadowEffect(blurRadius=8, offset=(0,2), color=rgba(0,0,0,30))
Верхняя полоска: 3px, цвет задаётся при создании (accent_color параметр)

Внутри (горизонтально):
  [Иконка 44×44px, радиус 10px, фон icon_bg]  [Текст блок]

Текст блок (вертикально):
  label: 12px, font-weight 600, color #5A6478, UPPERCASE, letter-spacing 0.6px
  value: 28px, font-weight 800, color #1A1A2E, letter-spacing -1px
  delta: 12px, font-weight 700 (цвет: up=#107C10, down=#C42B1C, neutral=#9BA3B4)

Hover: translateY(-2px) анимация через QPropertyAnimation на geometry/pos, 180ms OutCubic
```

```python
class StatCard(QFrame):
    def __init__(self, label: str, value: str, delta: str = "",
                 delta_type: str = "neutral",   # "up" | "down" | "neutral"
                 icon_svg: str = "",             # SVG-строка иконки
                 accent_color: str = "#0078D4",
                 icon_bg: str = "#EFF6FC",
                 parent=None):
        ...
```

---

### 2. ContinueBanner (`ui/components/continue_banner.py`)

HTML-референс: `.continue-banner`

```
Фон:        linear-gradient(120deg, #0052a3 0%, #0078D4 60%, #4DA3E8 100%)
Радиус:     12px
Padding:    20px 24px
Тень:       0 8px 24px rgba(0,120,212,.35)
Декор:      два полупрозрачных круга справа (рисовать через paintEvent)

Внутри (горизонтально):
  [Иконка 52×52, rgba(255,255,255,.15), радиус 14px]
  [Информационный блок, flex:1]
  [Кнопка "Продолжить"]

Информационный блок:
  label:    11px, opacity .65, UPPERCASE, letter-spacing .8px  → "ПРОДОЛЖИТЬ"
  title:    17px, font-weight 800, цвет #fff
  subtitle: 12px, opacity .65
  progress: полоска 4px, фон rgba(255,255,255,.2), заполнение rgba(255,255,255,.85)
  pct_text: 11px, font-weight 700, opacity .7

Кнопка:     фон #fff, цвет #0078D4, padding 11px 22px, радиус 8px, font-weight 800
            hover: scale(1.03), 150ms
```

```python
class ContinueBanner(QFrame):
    continue_clicked = Signal()

    def __init__(self, case_title: str, module_info: str,
                 progress_pct: int, score_info: str, parent=None):
        ...
```

---

### 3. RingProgress (`ui/components/ring_progress.py`)

HTML-референс: `.ring-card` (тёмная карточка с кольцевым графиком)

```
Фон карточки: linear-gradient(135deg, #0D1B2E, #0a2040)
Радиус:       12px
Граница:      1px solid rgba(255,255,255,0.06)

Кольцо 140×140px — рисовать через QPainter.drawArc():
  Толщина:    14px
  Фон дуги:  rgba(255,255,255, 0.08)
  Дуга:      цвет зависит от процента:
             ≥75% → #4ee87a (зелёный)
             ≥60% → #F59E0B (жёлтый)
             <60% → #C42B1C (красный)
  Анимация заполнения: 0→target за 1200ms, QPropertyAnimation, OutQuart

Центр кольца:
  value:  28px, font-weight 800, цвет как у дуги
  label: "БАЛЛ", 10px, opacity .45, UPPERCASE

Справа от кольца (info-блок, цвет #fff):
  grade_pill:   фон rgba(255,255,255,.08), padding 6px 14px, радиус 100px
                "● Оценка 5" (точка — цвет как дуга)
  title:        18px, font-weight 800
  subtitle:     12px, opacity .45
  modules:      список ModuleRow (name + progressbar 4px + pct%)
```

```python
class RingProgress(QFrame):
    def __init__(self, score_pct: int, case_title: str,
                 subtitle: str, modules: list[tuple[str, int]], parent=None):
        # modules: [(name, pct), ...]
        ...
```

---

### 4. ScoreChart (`ui/components/score_chart.py`)

HTML-референс: chart `scoreChart` / `progressChart` (Chart.js line chart)
Qt-реализация: **matplotlib FigureCanvasQTAgg** (уже в requirements.txt)

```
Тип:        Line chart
Цвет линии: #0078D4, ширина 2.5px
Точки:      radius 5, заливка цветом (зелёный ≥75%, жёлтый ≥60%, красный <60%)
Заливка:    gradient под линией rgba(0,120,212, 0.18→0)
Пороговая линия: rgba(196,43,28,.4), dash [5,4], без точек  → "60% порог"
Оси:        Y: 40–100%, подписи "N%"
            X: даты
Фон:        #FFFFFF (или прозрачный)
Шрифт:      Segoe UI Variable, 11px, цвет #9BA3B4
Сетка Y:    rgba(0,0,0,.05), без сетки X
```

```python
class ScoreChart(FigureCanvasQTAgg):
    def __init__(self, dates: list[str], scores: list[int],
                 show_threshold: bool = True, parent=None):
        ...

    def update_data(self, dates: list[str], scores: list[int]) -> None:
        ...
```

---

### 5. HeatmapWidget (`ui/components/heatmap_widget.py`)

HTML-референс: `#heatmapWrap` + buildHeatmap() JS-функция

```
Отрисовка: QWidget с кастомным paintEvent (НЕ matplotlib — производительнее)

Ячейка:   22×16px, border-radius 3px
Цвет:     интерполяция RGB:
          0%  → rgb(196, 43, 28)   # error red
          50% → rgb(245, 158, 11)  # warning amber
          100%→ rgb(16, 124, 16)   # success green
          Формула: r = 196*(1-t) + 16*t, g = 43*(1-t) + 124*t, b = 28*(1-t) + 16*t

Заголовок: номера заданий (1..N), 9px, color #9BA3B4, выровнены по ячейкам
Строки:    [label 90px fixed] [ячейки с gap 3px]
Label:     10px, font-weight 600, color #9BA3B4, ellipsis overflow

Tooltip:   QToolTip при hover на ячейке: "Студент · Задание N · XX%"

Легенда:  горизонтальный gradient bar внизу: error → warning → success
          подписи "0%" слева, "100%" справа, 11px, color #9BA3B4
```

```python
class HeatmapWidget(QWidget):
    def __init__(self, students: list[str], task_count: int,
                 data: list[list[float]],   # data[student_idx][task_idx] = 0.0..1.0
                 parent=None):
        ...
```

---

### 6. ActivityFeed (`ui/components/activity_feed.py`)

HTML-референс: `.activity-feed` + `.activity-item`

```
Список событий без разделителей (только 1px border-bottom rgba(0,0,0,.04))

Каждый элемент (горизонтально, padding 11px 0):
  [dot 8×8px, border-radius 50%]  [text, flex:1]  [time, 11px, #9BA3B4]

Dot цвета:
  green  → #107C10  (завершил успешно)
  orange → #F59E0B  (завершил с низким баллом)
  blue   → #0078D4  (начал)

Text: 12px, line-height 1.4
  bold часть:  font-weight 700  (имя студента)
  score badge: inline pill, padding 1px 7px, border-radius 100px
               good: bg=#DFF6DD, color=#0B5E0B
               bad:  bg=#FDE7E9, color=#C42B1C
```

```python
class ActivityFeed(QScrollArea):
    def __init__(self, events: list[dict], parent=None):
        # event: {"name": str, "action": str, "score": int|None,
        #         "time": str, "type": "success"|"fail"|"start"}
        ...

    def prepend_event(self, event: dict) -> None:
        """Добавляет новое событие сверху (из bus.attempt_finished)."""
        ...
```

---

### 7. GroupCard (`ui/components/group_card.py`)

HTML-референс: `.group-card`

```
Фон: #FFFFFF, радиус 12px, border 1px solid rgba(0,0,0,0.07)
Hover: translateY(-2px), shadow_md, 180ms

Структура:
  [header: emoji-иконка 40px + название + подпись]
  [stats row: N студентов | N кейсов | ср.балл%]
    разделители: 1px vertical линии rgba(0,0,0,0.07)
  [tags: список кейсов как pill-tags]
  [footer: кнопки "Открыть" (accent) + "Аналитика" (ghost)]
```

---

## ЭКРАНЫ — детальные спецификации

### S-1: StudentDashboard (`ui/windows/student_dashboard.py`)

**Источник данных:** `container.analytics_service`, `container.attempt_service`, `container.case_service`

```
MainLayout: QVBoxLayout с QScrollArea

┌─ TopBar (60px, bg #FFFFFF, border-bottom) ──────────────────────────────┐
│  "Добро пожаловать, {user.full_name}"  [spacer]  [поиск]  [дата]        │
└──────────────────────────────────────────────────────────────────────────┘

┌─ Content (ScrollArea, padding 24px 28px, bg #F0F2F5) ───────────────────┐
│                                                                          │
│  StatRow (3 карточки, grid 1fr 1fr 1fr, gap 16px):                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐         │
│  │ Доступно кейсов  │ │   Выполнено      │ │  Средний балл    │         │
│  │ accent=#0078D4   │ │ accent=#107C10   │ │ accent=#4DA3E8   │         │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘         │
│                                                                          │
│  [ContinueBanner] — показывать только если есть активная попытка        │
│   скрыть если attempt_service.get_active(user.id) is None               │
│                                                                          │
│  Grid (1fr 1.6fr, gap 20px):                                            │
│  ┌─────────────────────┐  ┌────────────────────────────────────────┐    │
│  │  RingProgress       │  │  ScoreChart                            │    │
│  │  (последний кейс)   │  │  "Динамика баллов" + фильтр 30дн/3мес │    │
│  └─────────────────────┘  └────────────────────────────────────────┘    │
│                                                                          │
│  Grid (1fr 1fr, gap 20px):                                              │
│  ┌────────────────────────────┐  ┌───────────────────────────────┐      │
│  │  Таблица последних         │  │  Достижения (4 разблок +      │      │
│  │  результатов (5 строк)     │  │  2 locked) + круговая диагр.  │      │
│  │  Кейс|Балл|Оценка|Дата    │  │  по дисциплинам               │      │
│  └────────────────────────────┘  └───────────────────────────────┘      │
│                                                                          │
│  SectionLabel "Рекомендованные кейсы"                                   │
│  CasesGrid (3 колонки): CaseCard × N (из case_service.get_recommended)  │
└──────────────────────────────────────────────────────────────────────────┘
```

**Данные из сервисов:**
```python
# в __init__ после super().__init__():
self._user = app.current_user
stats = container.analytics_service.get_student_stats(self._user.id)
# stats.available_count, stats.completed_count, stats.avg_score

active = container.attempt_service.get_active(self._user.id)
# если not None → показать ContinueBanner

last_result = container.analytics_service.get_last_result(self._user.id)
# → RingProgress

history = container.analytics_service.get_score_history(self._user.id, days=30)
# → ScoreChart(dates=history.dates, scores=history.scores)

recent = container.analytics_service.get_recent_results(self._user.id, limit=5)
# → таблица результатов

recommended = container.case_service.get_recommended(self._user.id, limit=3)
# → CaseCard × 3
```

---

### S-5: MyResults (`ui/windows/student_results.py`)

```
┌─ FilterRow (gap 10px) ──────────────────────────────────────────────────┐
│  [DateRangePicker] [DropDown дисциплина]                                 │
└──────────────────────────────────────────────────────────────────────────┘

StatRow (4 карточки): Попытки | Ср.балл | Ср.время | Лучший результат

Card "График успеваемости":
  ScoreChart высота 220px
  Цветные точки: ≥75%=зелёный, ≥60%=жёлтый, <60%=красный
  Пунктирная линия "Порог зачёта 60%"

Card "История попыток":
  Таблица: Кейс | Дисциплина | Дата | Время | Балл | Оценка | [Детали]
  Клик "Детали" → bus.navigate_to("case_result", {attempt_id, readonly=True})
  Сортировка по дате по убыванию
  Пагинация если > 20 строк
```

---

### T-1: TeacherDashboard (`ui/windows/teacher_dashboard.py`)

```
StatRow (4 карточки): Мои кейсы | Студентов | Попыток сегодня | Ср.балл группы

Grid (1.6fr 1fr, gap 20px):
  ┌─ BarChart "Активность за 7 дней" ───┐  ┌─ ActivityFeed ──────────────┐
  │  matplotlib, 2 серии:               │  │  (обновляется через         │
  │  синий=Попытки, зелёный=Завершены   │  │   bus.attempt_finished)     │
  └─────────────────────────────────────┘  └─────────────────────────────┘

SectionLabel "Активные группы"
GroupsGrid (3 колонки): GroupCard × N
```

**BarChart параметры (matplotlib):**
```python
# Цвета серий:
ATTEMPTS_COLOR  = "rgba(0,120,212,0.75)"   # #0078D4 с 75% opacity
COMPLETED_COLOR = "rgba(16,124,16,0.75)"   # #107C10 с 75% opacity
# Bars: border_radius=5, grouped (side-by-side)
# Axes: без border, grid Y rgba(0,0,0,.05), X без grid
# Легенда: top-right, boxwidth=10
```

---

### T-6: Analytics (`ui/windows/teacher_analytics.py`)

```
FilterRow: [DropDown группа] [DropDown кейс] [DateRangePicker]
           [spacer] [Кнопка "Экспорт PDF"] [Кнопка "Excel"]

StatRow (4 карточки): Ср.балл | Завершили | Ср.время | Лучший

Grid (1.5fr 1fr, gap 20px):
  ┌─ HeatmapWidget ──────────────────┐  ┌─ GradeDistChart ──────────────┐
  │  Студенты × Задания              │  │  Гистограмма оценок            │
  │  красный(0%) → зелёный(100%)    │  │  Bins: 0-10%...90-100%         │
  │  Легенда-градиент снизу          │  │  Цвет баров: красный/жёлтый/   │
  └──────────────────────────────────┘  │  зелёный по диапазону          │
                                        └───────────────────────────────-┘

Grid (1fr 1fr, gap 20px):
  ┌─ Рейтинг студентов ──────────────┐  ┌─ Проблемные задания ──────────┐
  │  #|Студент|Балл|Прогресс|Время   │  │  WeakTasksList (топ-5)        │
  │  mini-bar цветные                │  │  + RadarChart по типам заданий │
  └──────────────────────────────────┘  └───────────────────────────────┘
```

**GradeDistChart (matplotlib):**
```python
# Цвет баров по диапазону:
# 0-50%   → #C42B1C
# 50-70%  → #F59E0B
# 70-100% → #107C10
# border_radius=4, без легенды
```

**RadarChart по типам заданий (matplotlib):**
```python
# Оси: Выбор | Текст | Расчёт | Порядок | Соответствие | Изображение
# fill: rgba(0,120,212,0.12), border: #0078D4, width 2px, points radius 4
# r_min=0, r_max=100, step=25
```

---

### T-7: Groups (`ui/windows/teacher_groups.py`)

```
Header row: [spacer] [Кнопка "+ Создать группу"]

GroupsGrid (3 колонки): GroupCard × N
  каждая карточка показывает:
  - название + подпись (факультет, год)
  - emoji-иконка
  - теги привязанных кейсов (pill-теги)
  - статистика: N студентов | N кейсов | ср.балл
  - кнопки: "Открыть" → bus.navigate_to("group_detail", {group_id})
            "Аналитика" → bus.navigate_to("teacher_analytics", {group_id})
```

---

## Sidebar и MainWindow

Сайдбар **уже существует или создаётся в рамках MainWindow** по §8 MAIN WINDOW.
Реализовать его точно по HTML-референсу:

```
Ширина:     240px fixed
Фон:        #0D1B2E
Правая граница: 1px gradient line (прозрачный→rgba(255,255,255,0.06)→прозрачный)

Верхняя секция (padding 20px, border-bottom rgba(255,255,255,0.06)):
  [Лого: 32px rounded icon + "EduCase" (Edu=синий, Case=белый)]
  [UserCard: avatar-круг 36px + имя + роль, фон rgba(255,255,255,0.05)]

Nav items (padding 9px 12px, gap 10px, border-radius 8px):
  normal:  color rgba(255,255,255,.45), hover → rgba(255,255,255,.07) bg
  active:  bg rgba(0,120,212,.18), color #fff
           + левая полоска 3×18px, цвет #4DA3E8, border-radius 0 3px 3px 0

Nav badge (число новых кейсов): bg #0078D4, 10px bold, padding 2px 7px, pill-radius

Нижняя секция:
  Кнопка Logout: нормальная = rgba(255,255,255,.3)
                 hover = bg rgba(220,50,40,.15), color #fc8080

Навигация СТУДЕНТА:  Главная | Мои кейсы | Мои результаты | Профиль
Навигация ПРЕПОДАВАТЕЛЯ: Главная | Аналитика | Кейсы | Группы | Профиль
```

---

## Общие компоненты UI

### ScorePill
```python
class ScorePill(QLabel):
    """Цветной pill с процентом. Используется в таблицах результатов."""
    # ≥75%: bg=#DFF6DD, color=#0B5E0B
    # ≥60%: bg=#FFF4CE, color=#7A4800
    # <60%: bg=#FDE7E9, color=#A01010
    # padding: 4px 10px, border-radius: 100px, font: 12px bold
```

### GradeBadge
```python
class GradeBadge(QLabel):
    """Круглый значок оценки 5/4/3/2. Размер 28×28px."""
    # 5: bg=#DFF6DD, color=#0B5E0B
    # 4: bg=#EFF6FC, color=#005A9E
    # 3: bg=#FFF4CE, color=#7A4800
    # 2: bg=#FDE7E9, color=#C42B1C
```

### SectionLabel
```python
class SectionLabel(QWidget):
    """Заголовок секции с горизонтальной линией справа."""
    # Текст: 13px, font-weight 800, color #1A1A2E
    # Линия: 1px, цвет rgba(0,0,0,0.07), тянется до конца контейнера
```

### CardFrame
```python
class CardFrame(QFrame):
    """Базовый контейнер-карточка. Все дочерние карточки наследуют."""
    # bg: #FFFFFF, radius: 12px, border: 1px solid rgba(0,0,0,0.07)
    # shadow: QGraphicsDropShadowEffect(blur=6, offset=(0,2), color=rgba(0,0,0,20))
    # padding: 22px 24px
```

---

## Цвета кнопок и QSS

### Accent-кнопка (основная)
```css
QPushButton {
    background-color: #0078D4;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 700;
}
QPushButton:hover { background-color: #006CBD; }
QPushButton:pressed { background-color: #005A9E; }
```

### Ghost-кнопка
```css
QPushButton {
    background-color: #F0F2F5;
    color: #1A1A2E;
    border: 1px solid rgba(0,0,0,0.07);
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 700;
}
QPushButton:hover { background-color: #E4E7EB; }
```

### Маленькая accent-кнопка (в CaseCard)
```css
QPushButton {
    background-color: #0078D4; color: white;
    border: none; border-radius: 6px;
    padding: 5px 12px; font-size: 11px; font-weight: 700;
}
```

---

## Анимации (QPropertyAnimation)

```python
# Hover на карточках (translateY -2px):
anim = QPropertyAnimation(widget, b"pos")
anim.setDuration(180)
anim.setEasingCurve(QEasingCurve.OutCubic)
anim.setEndValue(QPoint(widget.x(), widget.y() - 2))

# Fade-in при переключении страниц:
eff = QGraphicsOpacityEffect(widget)
widget.setGraphicsEffect(eff)
anim = QPropertyAnimation(eff, b"opacity")
anim.setDuration(280)
anim.setStartValue(0.0); anim.setEndValue(1.0)
anim.setEasingCurve(QEasingCurve.OutCubic)

# RingProgress заполнение (0 → target):
# Анимировать через QPropertyAnimation на кастомный Qt Property "_arc_value"
# Duration: 1200ms, EasingCurve: OutQuart
```

---

## Интеграция с EventBus

```python
# В каждом экране подписаться на обновления:
bus.user_logged_in.connect(self._on_user_changed)
bus.attempt_finished.connect(self._refresh_stats)   # обновить StatCard и таблицу
bus.navigate_to.connect(self._on_navigate)          # переключение экранов

# ActivityFeed в TeacherDashboard:
bus.attempt_finished.connect(self._activity_feed.prepend_event)
```

---

## Matplotlib — настройки стиля (единые для всех графиков)

```python
# ui/styles/chart_style.py
import matplotlib as mpl

def apply_dashboard_style():
    mpl.rcParams.update({
        "font.family":       "Segoe UI Variable",
        "font.size":         11,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.spines.left":  False,
        "axes.spines.bottom":False,
        "axes.grid":         True,
        "axes.grid.axis":    "y",
        "grid.color":        "rgba(0,0,0,.05)",
        "grid.linewidth":    0.8,
        "axes.facecolor":    "white",
        "figure.facecolor":  "white",
        "xtick.color":       "#9BA3B4",
        "ytick.color":       "#9BA3B4",
        "text.color":        "#5A6478",
        "axes.labelcolor":   "#5A6478",
    })
```

---

## Порядок реализации

```
Шаг 1: ui/styles/dashboard_theme.py + ui/styles/chart_style.py
Шаг 2: ui/components/stat_card.py
Шаг 3: ui/components/continue_banner.py
Шаг 4: ui/components/ring_progress.py
Шаг 5: ui/components/score_chart.py  (matplotlib)
Шаг 6: ui/components/activity_feed.py
Шаг 7: ui/components/group_card.py
Шаг 8: ui/components/heatmap_widget.py
Шаг 9: ui/components/weak_tasks_list.py
Шаг 10: ui/windows/student_dashboard.py  (S-1)
Шаг 11: ui/windows/student_results.py    (S-5)
Шаг 12: ui/windows/teacher_dashboard.py  (T-1)
Шаг 13: ui/windows/teacher_analytics.py  (T-6)
Шаг 14: ui/windows/teacher_groups.py     (T-7)
Шаг 15: Подключить экраны в MainWindow/QStackedWidget
Шаг 16: Smoke-test: запустить приложение, войти как студент, войти как преподаватель
```

---

## Чего НЕ делать

- ❌ Не использовать Qt Designer (.ui файлы) — только чистый Python код
- ❌ Не использовать сторонние UI-библиотеки кроме PySide6 и matplotlib
- ❌ Не хардкодить данные — все значения берутся из сервисов (container.*)
- ❌ Не менять цвета на глаз — только из токенов выше или из HTML-референса
- ❌ Не делать QDialog для аналитики — встраивать в QStackedWidget
- ❌ Не трогать: splash_window.py, auth_service.py, idle_guard.py, event_bus.py
- ❌ Не использовать QWebEngineView для отображения HTML-референса в runtime

---

## Справочник компонент → HTML-класс

| Qt-компонент | HTML-класс в референсе |
|---|---|
| `StatCard` | `.stat-card` + `.stat-icon` + `.stat-body` |
| `ContinueBanner` | `.continue-banner` |
| `RingProgress` | `.ring-card` + `.ring-wrap` + `.ring-center` |
| `ScoreChart` | `#scoreChart` / `#progressChart` (Chart.js line) |
| `HeatmapWidget` | `#heatmapWrap` + `.hm-cell` |
| `ActivityFeed` | `.activity-feed` + `.activity-item` |
| `GroupCard` | `.group-card` |
| `WeakTasksList` | `.weak-tasks` + `.weak-row` |
| `ScorePill` | `.score-pill.high/.mid/.low` |
| `GradeBadge` | `.grade-badge.grade-5/.grade-4/.grade-3` |
| `CardFrame` | `.card` |
| `SectionLabel` | `.section-label` |
| Sidebar nav item | `.nav-item` (active полоска 3px слева) |
| Sidebar user card | `.user-card` |
| TopBar | `.topbar` |
