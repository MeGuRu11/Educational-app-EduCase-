# ПРОМПТ ДЛЯ AI-АГЕНТА: EduCase — Реализация Admin Panel (A-1 … A-5)

## Задача

Реализовать панель администратора **AdminDashboard (A-1)**, **Users (A-2)**, **UserEditor
(A-3)**, **System (A-4)** и **Logs (A-5)** в виде PySide6-виджетов строго по визуальному
референсу `docs/educase_admin_mockup.html`.

Все цвета, отступы, радиусы и поведение компонентов берутся **только из этого файла** —
он является единственным источником истины по дизайну.

**Корень проекта:** `C:\Users\user\Desktop\Program\Educational-app-EduCase-\educase\`
**Референс:** `docs/educase_admin_mockup.html` — открой и прочитай HTML + CSS целиком перед кодом.
**Архитектура:** `docs/PROJECT_DESIGN_v2.1.md` — экраны A-1…A-5 описаны в §8.

---

## Дизайн-токены (Admin-специфичные, дополняют `dashboard_theme.py`)

Файл `ui/styles/dashboard_theme.py` уже существует (создан при реализации студент/учитель).
Добавить в него секцию admin-токенов:

```python
# --- ADMIN-SPECIFIC TOKENS ---
ADMIN = {
    # Сайдбар admin отличается от student/teacher:
    # левая полоска активного пункта — красная, не синяя
    "sidebar_accent_bar":  "#ff8080",
    "nav_active_bg":       "rgba(196,43,28,.15)",   # rgba(196,43,28,.15)
    "nav_active_color":    "#FFFFFF",
    # Бейдж "ADMIN" в лого
    "logo_badge_bg":       "rgba(196,43,28,.25)",
    "logo_badge_color":    "#ff8080",
    # Аватар администратора
    "avatar_gradient":     "qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #C42B1C,stop:1 #e85050)",
    # SystemInfoCard (тёмная плашка)
    "sysinfo_bg_start":    "#0D1B2E",
    "sysinfo_bg_end":      "#0a2040",
    "sysinfo_ok_bg":       "rgba(16,124,16,.2)",
    "sysinfo_ok_color":    "#4ee87a",
    "sysinfo_warn_bg":     "rgba(196,43,28,.2)",
    "sysinfo_warn_color":  "#ff8080",
}

ROLE_BADGE = {
    "admin":   {"bg": "rgba(196,43,28,.12)", "color": "#C42B1C"},
    "teacher": {"bg": "#EFF6FC",             "color": "#005A9E"},
    "student": {"bg": "#DFF6DD",             "color": "#0B5E0B"},
}

LOG_BADGE = {
    "INFO":    {"bg": "#EFF6FC", "color": "#005A9E"},
    "WARNING": {"bg": "#FFF4CE", "color": "#7A4800"},
    "ERROR":   {"bg": "#FDE7E9", "color": "#C42B1C"},
    "DEBUG":   {"bg": "#F0F0F0", "color": "#666666"},
}

STATUS_BADGE = {
    "active": {"bg": "#DFF6DD", "color": "#0B5E0B", "dot": "#107C10"},
    "locked": {"bg": "#FDE7E9", "color": "#C42B1C", "dot": "#C42B1C"},
}
```

---

## Архитектура файлов

Создать следующие файлы (все новые, если не существуют):

```
educase/
├── ui/
│   ├── styles/
│   │   └── dashboard_theme.py       ← ДОПОЛНИТЬ секцией ADMIN (не перезаписывать)
│   ├── components/
│   │   ├── sysinfo_card.py          ← SystemInfoCard (тёмная плашка A-1)
│   │   ├── role_badge.py            ← RoleBadge, StatusBadge, LogLevelBadge
│   │   ├── data_table.py            ← DataTable (сортируемая с checkbox)
│   │   ├── dock_panel.py            ← DockPanel (slide-in справа)
│   │   ├── tab_bar.py               ← TabBar (pill-стиль как в референсе)
│   │   ├── backup_row.py            ← BackupRow (строка бэкапа с кнопками)
│   │   ├── db_table_row.py          ← DbTableRow (имя+бар+счётчик)
│   │   └── toggle_switch.py         ← ToggleSwitch (ON/OFF)
│   └── windows/
│       ├── admin_dashboard.py       ← A-1 AdminDashboard
│       ├── admin_users.py           ← A-2 Users
│       ├── admin_user_editor.py     ← A-3 UserEditor (QDialog со stepper)
│       ├── admin_system.py          ← A-4 System (4 вкладки)
│       └── admin_logs.py            ← A-5 Logs
```

---

## КОМПОНЕНТЫ — детальные спецификации

### 1. SystemInfoCard (`ui/components/sysinfo_card.py`)

HTML-референс: `.sysinfo-card` в `educase_admin_mockup.html`

```
Фон:      QLinearGradient(135°, #0D1B2E → #0a2040)
Радиус:   12px
Граница:  1px solid rgba(255,255,255,0.06)
Тень:     QGraphicsDropShadowEffect(blur=20, offset=(0,6), color=rgba(0,0,0,60))
Padding:  22px 26px

Внутри: горизонтальный QHBoxLayout, 5 элементов SysInfoItem
Разделители между элементами: 1px vertical QFrame, цвет rgba(255,255,255,0.08)

SysInfoItem (QWidget, вертикальный):
  label:   11px, UPPERCASE, letter-spacing 0.8px, color rgba(255,255,255,.35)
  value:   22px, font-weight 800, color #FFFFFF
  sub_row: pill-QLabel (ok_pill или warn_pill)

ok_pill:   bg rgba(16,124,16,.2), color #4ee87a, padding 3px 9px, radius 100px, text "● Норма"
warn_pill: bg rgba(196,43,28,.2), color #ff8080, padding 3px 9px, radius 100px
```

```python
class SystemInfoCard(QFrame):
    def __init__(self, items: list[dict], parent=None):
        # item: {"label": str, "value": str, "sub": str,
        #        "status": "ok"|"warn"|"none", "mono": bool}
        # Пример:
        # {"label": "Размер БД", "value": "14.2 МБ", "status": "ok"}
        # {"label": "Версия", "value": "v1.0.0", "sub": "Python 3.12 · PySide6 6.7", "mono": True}
        ...

    def update_item(self, index: int, value: str, status: str = "ok") -> None:
        """Обновить конкретный элемент без пересоздания."""
        ...
```

---

### 2. RoleBadge / StatusBadge / LogLevelBadge (`ui/components/role_badge.py`)

HTML-референс: `.role-badge`, `.status-badge`, `.log-badge`

```python
class RoleBadge(QLabel):
    """Цветной pill с ролью. Размеры: padding 3px 9px, radius 100px, font 11px bold."""
    STYLES = {
        "admin":   ("rgba(196,43,28,.12)", "#C42B1C"),
        "teacher": ("#EFF6FC",             "#005A9E"),
        "student": ("#DFF6DD",             "#0B5E0B"),
    }
    def __init__(self, role: str, parent=None):
        # role: "admin" | "teacher" | "student"
        # Текст: "● Администратор" / "● Преподаватель" / "● Студент"
        ...

class StatusBadge(QLabel):
    """Статус с точкой. active=зелёный, locked=красный."""
    def __init__(self, status: str, parent=None):
        # status: "active" | "locked"
        # Текст: "● Активен" | "● Заблокирован"
        ...

    def set_status(self, status: str) -> None:
        ...

class LogLevelBadge(QLabel):
    """Уровень лога. Моноширинный шрифт (JetBrains Mono), font-size 10px."""
    STYLES = {
        "INFO":    ("#EFF6FC", "#005A9E"),
        "WARNING": ("#FFF4CE", "#7A4800"),
        "ERROR":   ("#FDE7E9", "#C42B1C"),
        "DEBUG":   ("#F0F0F0", "#666666"),
    }
    def __init__(self, level: str, parent=None):
        ...
```

---

### 3. DataTable (`ui/components/data_table.py`)

HTML-референс: `.data-table` + строки таблицы пользователей

```
Базировать на QTableWidget (НЕ QTableView — проще с кастомными ячейками)

Заголовки: font 11px, font-weight 700, color #9BA3B4, UPPERCASE, letter-spacing 0.7px
           border-bottom: 1px solid rgba(0,0,0,0.07)
           background: прозрачный

Строки: padding 11px 14px, font-size 13px
        border-bottom: 1px solid rgba(0,0,0,.03)
        последняя строка без border-bottom
        hover: background rgba(0,0,0,.015)

Checkbox-колонка: ширина 36px, QCheckBox в ячейке через setCellWidget

Колонки с виджетами (setCellWidget):
  - col "Роль":   RoleBadge
  - col "Статус": StatusBadge
  - col "Действия": QHBoxLayout с IconBtn

Сортировка: setSortingEnabled(True)
Сигнал: row_clicked = Signal(int, dict)  # (row_index, user_data)
```

```python
class DataTable(QTableWidget):
    row_clicked   = Signal(int, dict)      # клик на строку → dock panel
    bulk_selected = Signal(list)           # список id выбранных чекбоксами

    def __init__(self, columns: list[str], parent=None):
        ...

    def load_users(self, users: list[dict]) -> None:
        """Очистить и перезаполнить таблицу данными пользователей."""
        ...

    def apply_filter(self, role: str = "all", status: str = "all",
                     search: str = "") -> None:
        """Скрыть/показать строки без перезагрузки данных."""
        ...

    def get_selected_ids(self) -> list[int]:
        ...
```

---

### 4. DockPanel (`ui/components/dock_panel.py`)

HTML-референс: `.dock-panel` + `.dock-overlay`

```
Реализация: QWidget поверх MainWindow, НЕ отдельное окно

Позиция:   фиксировано справа, top=0, height=parent.height()
Ширина:    320px
Фон:       #FFFFFF
Тень:      QGraphicsDropShadowEffect(blur=40, offset=(-8,0), color=rgba(0,0,0,60))

Анимация slide-in/out:
  QPropertyAnimation(dock, b"pos")
  Открытие: x from parent.width() → parent.width()-320, duration=250ms, OutCubic
  Закрытие: x from parent.width()-320 → parent.width(), duration=220ms, InCubic

Overlay (QWidget под панелью):
  background: rgba(0,0,0,.4)
  backdrop_blur через QGraphicsBlurEffect на фоновый виджет (radius=2px)
  клик на overlay → close()

Структура DockPanel:
  ─ header: [title 15px bold] [close ×]
  ─ body (QScrollArea):
      avatar-круг 72px (инициалы)
      ФИО 16px bold, center
      subtitle: роль·группа 12px, center
      stat-row: 3 блока [Кейсов | Ср.балл | Попыток] на #F0F2F5, radius 10px
      info-rows: Логин / Роль / Статус / Группа / Последний вход / Создан
  ─ footer (border-top):
      [✏️ Редактировать] ghost full-width
      [🔒 Заблокировать] danger full-width
```

```python
class DockPanel(QWidget):
    edit_requested   = Signal(dict)   # → открыть UserEditor
    lock_requested   = Signal(int)    # → user_id
    unlock_requested = Signal(int)    # → user_id

    def __init__(self, parent: QWidget):
        ...

    def show_user(self, user_data: dict) -> None:
        """Заполнить данными и слайд-открыть."""
        ...

    def close_panel(self) -> None:
        """Анимированно закрыть."""
        ...
```

---

### 5. ToggleSwitch (`ui/components/toggle_switch.py`)

HTML-референс: `.toggle` + `.toggle.off`

```
Рисовать через QPainter в paintEvent — НЕ через QCheckBox:

Размер: 40×22px (setFixedSize)
Фон pill: если ON → #107C10, если OFF → rgba(0,0,0,.15)
Thumb:    белый круг 16×16px, анимируется QPropertyAnimation(b"_thumb_x")
          ON: x = width - 3 - 16 = 21
          OFF: x = 3
Анимация: duration=200ms, OutCubic

toggled = Signal(bool)
```

```python
class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, checked: bool = True, parent=None):
        ...

    def is_checked(self) -> bool:
        ...

    def set_checked(self, value: bool, animated: bool = True) -> None:
        ...

    def paintEvent(self, e):
        # рисует pill + thumb через QPainter
        ...

    def mousePressEvent(self, e):
        self.set_checked(not self._checked)
        self.toggled.emit(self._checked)
```

---

### 6. TabBar (`ui/components/tab_bar.py`)

HTML-референс: `.tabs` + `.tab` + `.tab.active`

```
QWidget с QHBoxLayout
Фон контейнера: #F0F2F5, radius 10px, padding 4px

Каждая Tab-кнопка:
  normal: bg transparent, color #5A6478, font 13px bold
  active: bg #FFFFFF, color #1A1A2E, shadow-sm
  hover:  color #1A1A2E
  transition: QPropertyAnimation opacity

tab_changed = Signal(int)  # индекс выбранной вкладки
```

```python
class TabBar(QWidget):
    tab_changed = Signal(int)

    def __init__(self, labels: list[str], parent=None):
        ...

    def set_current(self, index: int) -> None:
        ...
```

---

### 7. BackupRow (`ui/components/backup_row.py`)

HTML-референс: `.backup-row`

```
QFrame, border-radius 8px, bg #F0F2F5
Hover: bg #e8eaed, transition 150ms

Горизонтально:
  [🗄️ 20px emoji]  [info: имя (mono 13px bold) + meta (11px t2)]  [size t3]
  [♻️ Восстановить (ghost sm)]  [🗑 Удалить (danger sm, только иконка)]

Разделитель между Восстановить и Удалить: 1px rgba(0,0,0,0.07)
```

```python
class BackupRow(QFrame):
    restore_clicked = Signal(str)   # filename
    delete_clicked  = Signal(str)   # filename

    def __init__(self, filename: str, created_at: str,
                 size_mb: float, is_auto: bool, parent=None):
        ...
```

---

## ЭКРАНЫ — детальные спецификации

### A-1: AdminDashboard (`ui/windows/admin_dashboard.py`)

**Данные:** `container.user_service`, `container.backup_service`, `container.analytics_service`

```
Layout: QVBoxLayout → QScrollArea → content QWidget

TopBar (60px): "Панель администратора" | [spacer] | [дата]

[StatRow 4 карточки — grid 4×1fr, gap 16px]
  Карточка 1: "ПОЛЬЗОВАТЕЛЕЙ" | value=user_service.count_all() | accent=#0078D4
  Карточка 2: "СТУДЕНТОВ"     | value=user_service.count_by_role("student") | accent=#107C10
  Карточка 3: "ПРЕПОДАВАТЕЛЕЙ"| value=user_service.count_by_role("teacher") | accent=#4DA3E8
  Карточка 4: "КЕЙСОВ"        | value=case_service.count() | accent=#9D5D00

[SystemInfoCard — тёмная плашка, 5 блоков]
  Блок 1: "Размер БД" | db_maintenance.get_db_size() | ok/warn
  Блок 2: "Последний бэкап" | backup_service.last_backup_age() | ok если <48ч
  Блок 3: "Целостность БД"  | db_maintenance.integrity_check() | ok/warn
  Блок 4: "Версия"          | app_version (из config) | mono=True
  Блок 5: "Журнал ошибок"   | log_service.count_warnings() | warn если >0

[Grid 1.6fr 1fr, gap 20px]:
  [Card "Активность — 7 дней" → BarChart (matplotlib, 200px)]
    Серии: Попытки (синий), Завершены (зелёный), Новые пользователи (красный)
    Данные: analytics_service.get_activity_7days()
  [Card "Состав пользователей" → DoughnutChart (matplotlib)]
    Секции: Студенты=#107C10, Преподаватели=#0078D4, Администраторы=#C42B1C
    Данные: user_service.count_by_roles()
    Легенда: 3 строки текстом под чартом (без matplotlib-легенды)

[Grid 1fr 1fr, gap 20px]:
  [Card "Последние регистрации"]
    DataTable мини: 4 строки, колонки ФИО | Роль | Дата | Статус
    Данные: user_service.get_recent(limit=4)
    Ссылка "Все →" → bus.navigate_to("admin_users")
  [Card "Быстрые действия"]
    Список кнопок-ghost (вертикально, full-width):
    ➕ Создать пользователя    → bus.navigate_to("admin_user_editor", {"mode":"create"})
    💾 Создать резервную копию → self._backup_now()
    📋 Просмотр журнала        → bus.navigate_to("admin_logs")
    🔧 Проверить целостность   → self._integrity_check()
    📊 Экспортировать отчёт    → container.export_service.export_admin_report()
```

**Асинхронные операции (НЕ блокировать GUI):**
```python
def _backup_now(self):
    btn.setEnabled(False)
    btn.setText("Создаётся...")
    run_async(
        container.backup_service.create,
        on_result=lambda path: (
            btn.setEnabled(True),
            btn.setText("💾 Создать резервную копию"),
            bus.toast.emit("success", f"Бэкап создан: {path.name}"),
            self._refresh_sysinfo()
        ),
        on_error=lambda e: (
            btn.setEnabled(True),
            bus.toast.emit("error", f"Ошибка бэкапа: {e}")
        )
    )

def _integrity_check(self):
    run_async(
        db_maintenance.integrity_check,
        on_result=lambda ok: bus.toast.emit(
            "success" if ok else "error",
            "Целостность БД: OK" if ok else "Целостность БД: ОШИБКА"
        )
    )
```

---

### A-2: Users (`ui/windows/admin_users.py`)

**Данные:** `container.user_service`

```
Layout: QVBoxLayout

[FilterRow]:
  [+ Создать] (accent btn)
  [SearchBar — QLineEdit с иконкой]  placeholder "Поиск по ФИО или логину"
  [DropDown Роль]: Все роли | Студент | Преподаватель | Администратор
  [DropDown Статус]: Все | Активные | Заблокированные
  [spacer]
  [🔒 Заблокировать выбранных] (danger, disabled если нет выбранных)
  [🗑 Удалить выбранных] (danger, disabled если нет выбранных)

[DataTable — 1 большой card]:
  Колонки:  ☐ | ФИО / Логин | Роль | Группа | Статус | Последний вход | Действия
  Данные:   user_service.get_all()
  Сортировка по любой колонке (setSortingEnabled)
  Фильтр:   table.apply_filter() при изменении FilterRow (live, без кнопки)
  Клик строки → dock_panel.show_user(user_data)

[Pagination Bar]:
  "Показано N из M"
  Кнопки: ← 1 2 3 →
  По 20 пользователей на страницу

[DockPanel] (float поверх окна)
  dock.edit_requested → открыть UserEditor (режим "edit")
  dock.lock_requested → user_service.lock(id) + table.refresh_row(id)
  dock.unlock_requested → user_service.unlock(id) + table.refresh_row(id)
```

**Поиск с debounce:**
```python
self._search_timer = QTimer()
self._search_timer.setSingleShot(True)
self._search_timer.setInterval(300)   # 300ms debounce
self._search_timer.timeout.connect(self._apply_filter)
search_field.textChanged.connect(lambda: self._search_timer.start())
```

---

### A-3: UserEditor — QDialog (`ui/windows/admin_user_editor.py`)

HTML-референс: `.modal` + `.modal-stepper` + шаг 1/шаг 2

```
QDialog (НЕ QMainWindow):
  Размер:      520×580px (fixed), не resizable
  Фон:         #FFFFFF
  border-radius: 16px (через stylesheet)
  Тень:        QGraphicsDropShadowEffect(blur=60, offset=(0,12), color=rgba(0,0,0,50))
  Флаги:       Qt.Dialog | Qt.FramelessWindowHint + кастомный header

  Режимы: mode="create" или mode="edit"
  При "edit": заполнить поля из user_data, скрыть поле пароля (опционально)
  При "create": пустые поля, пароль обязателен

Header:
  [Создать пользователя / Редактировать] 18px bold   [✕ close-btn 32×32px]

Stepper:
  [①Основное] ────── [②Права]
  Шаг-кружок: 28×28px, border-radius 50%
    pending: bg=#F0F2F5, color=#9BA3B4, border=1px rgba(0,0,0,.07)
    active:  bg=#0078D4, color=#fff
    done:    bg=#DFF6DD, color=#107C10  (✓ вместо цифры)
  Линия между шагами: 2px, done=#107C10, pending=rgba(0,0,0,.07)
  QPropertyAnimation на цвета (200ms)

[ШАГ 1 — Основное]:
  AvatarPicker:
    Круглый QLabel 72×72px preview (инициалы auto или загруженное фото)
    Кнопка "📷 Загрузить фото" → QFileDialog(Images)
    Кнопка "🗑 Удалить"
    Инициалы вычисляются из полей ФИО в реальном времени

  Form (2-column grid):
    [Фамилия]     [Имя]
    [Логин]       [Роль: QComboBox Студент/Преп./Администратор]
    [Группа: QComboBox — из group_service.get_all() + "— Без группы —"]

  Пароль (полная ширина):
    QLineEdit (EchoMode Password) + кнопки [👁] [🔀] справа (абсолютно)
    [👁]: toggle EchoMode
    [🔀]: сгенерировать 12 символов (буквы+цифры+!@#$),
          установить в поле + скопировать в буфер (QApplication.clipboard())
    Полоска силы пароля 3px: weak=#C42B1C, fair=#F59E0B, strong=#107C10
    Алгоритм силы: len<8=weak, len<12 и нет спецсимволов=fair, else=strong

  ToggleSwitch "Учётная запись активна":
    Подпись: "Пользователь может войти в систему"

[ШАГ 2 — Права]:
  Если роль стандартная (student/teacher/admin) → info-плашка:
    bg=#EFF6FC, иконка ℹ️, текст "Права назначены автоматически по роли «...»"
    + текстовое описание прав роли

  Если роль кастомная → матрица QCheckBox:
    Строки: Просмотр кейсов | Создание кейсов | Управление пользователями |
            Просмотр аналитики | Экспорт данных | Администрирование системы

Footer:
  [← Назад] ghost (hidden на шаге 1)
  [Отмена] ghost
  [Далее → / ✓ Создать / ✓ Сохранить] accent

Валидация перед шагом 2:
  - ФИО: не пустые
  - Логин: минимум 3 символа, только [a-z0-9._-], уникальный (user_service.login_exists())
  - Пароль (режим create): не пустой
  При ошибке: подсветить поле border=1px solid #C42B1C + tooltip с причиной

Сохранение (шаг 2, кнопка Создать/Сохранить):
  Режим create: run_async(user_service.create_user, data, on_result=..., on_error=...)
  Режим edit:   run_async(user_service.update_user, user_id, data, ...)
  Во время выполнения: кнопка disabled + текст "Сохраняется..."
  При успехе: accept() + bus.toast.emit("success", "Пользователь создан")
  При ошибке: bus.toast.emit("error", str(e)), диалог остаётся открытым
```

```python
class UserEditor(QDialog):
    user_saved = Signal(dict)   # emit после успешного сохранения

    def __init__(self, mode: str = "create",
                 user_data: dict | None = None, parent=None):
        # mode: "create" | "edit"
        # user_data: заполненный dict при mode="edit"
        ...
```

---

### A-4: System (`ui/windows/admin_system.py`)

HTML-референс: вкладки системных настроек

```
Layout: QVBoxLayout
  [TabBar: "⚙️ Общее" | "🗄️ База данных" | "💾 Резервные копии" | "🎨 Дизайн"]
  [QStackedWidget — 4 страницы]

──── ВКЛАДКА "ОБЩЕЕ" ────
[Grid 1fr 1fr]:
  [Card "Информация о приложении"]:
    DbTableRow × 5 (без баров):
      Версия / Python / PySide6 / SQLAlchemy / Путь к БД
    Значения берутся из config.APP_VERSION, sys.version, PySide6.__version__

  [Card "Настройки"]:
    ToggleSwitch "Автоматические бэкапы"      → config.auto_backup
    ToggleSwitch "Логирование действий"        → config.logging_enabled
    ToggleSwitch "Анимации интерфейса"         → config.animations_enabled
    QSpinBox "Хранить бэкапы N дней"           → config.backup_keep_days
    [Сохранить настройки] accent → config.save()

──── ВКЛАДКА "БАЗА ДАННЫХ" ────
[Grid 1fr 1fr]:
  [Card "Статистика таблиц"]:
    DbTableRow × 7 (с mini-bars):
      users / cases / attempts / answers / groups / tasks / system_logs
    Данные: db_maintenance.get_table_stats() — dict[table→count]
    Бар: count / max_count * 100%

  [Card "Обслуживание"]:
    Плашка "Размер файла: N МБ · WAL: включён" 12px t2
    IntegrityCheck-строка (зелёная если ok)
    Кнопки вертикально:
      [🔧 Запустить VACUUM]
        run_async(db_maintenance.vacuum, on_result=toast_ok, on_error=toast_err)
        Во время: кнопка disabled + "Выполняется..."
      [✅ Проверить целостность]
        run_async(db_maintenance.integrity_check, ...)
      [📊 Analyze]
        run_async(db_maintenance.analyze, ...)
      [🗑 Очистить логи >90 дней] danger
        ConfirmDialog сначала, потом run_async

──── ВКЛАДКА "РЕЗЕРВНЫЕ КОПИИ" ────
Header row:
  "N резервных копий · автобэкап каждые 24ч" (label)
  [💾 Создать бэкап сейчас] accent → _create_backup_async()

[QVBoxLayout с BackupRow × N]:
  Данные: backup_service.list_backups() → list[BackupInfo]
  BackupRow.restore_clicked → ConfirmDialog → run_async(backup_service.restore)
  BackupRow.delete_clicked  → ConfirmDialog → backup_service.delete() + refresh

Пустое состояние (если нет бэкапов):
  Иконка 💾 60px + текст "Резервных копий пока нет" + [Создать первый бэкап]

──── ВКЛАДКА "ДИЗАЙН" ────
[Grid 1fr 1fr]:
  [Card "Внешний вид"]:
    ColorPicker акцента:
      QColorDialog → setAccentColor() → обновить токены в stylesheet
      Preset-кружки: 5 цветов (32×32px)
    Слайдер скорости анимаций:
      QSlider 50-200%, labels "0.5× / 1.0× / 2.0×"
      Изменяет ANIMATION_SPEED_FACTOR в config
    ToggleSwitch "Тёмная тема" (пока disabled с подписью "В разработке")

  [Card "Предпросмотр"]:
    Статичный виджет с образцами: accent-btn, ghost-btn, карточка, бейджи
    Обновляется при смене акцентного цвета
    [Применить тему] → config.save() + StyleSheet.apply_global()
```

---

### A-5: Logs (`ui/windows/admin_logs.py`)

HTML-референс: таблица журнала с фильтрами

```
Layout: QVBoxLayout

[FilterRow]:
  [SearchBar] placeholder "Поиск по событиям"
  [DropDown Уровень]: Все | INFO | WARNING | ERROR | DEBUG
  [DropDown Пользователь]: Все + список уникальных логинов из БД
  [DatePicker] — QDateEdit, default=today
  [spacer]
  [📥 Экспорт CSV] → export_service.export_logs_csv()
  [🗑 Очистить >90 дней] danger

[Warning Summary Row — показывать только если warnings_count > 0]:
  Две плашки рядом (flex):
    Плашка WARNING: bg=#FDE7E9, иконка ⚠️, "N событий WARNING"
    Плашка INFO:    bg=#EFF6FC, иконка ℹ️, "N записей всего"

[Card с DataTable]:
  Колонки: Время | Уровень | Пользователь | Действие | Детали
  Строки с WARNING: фон rgba(196,43,28,.03) — выделение строки
  "Время": JetBrains Mono 11px
  "Уровень": LogLevelBadge
  "Пользователь": JetBrains Mono 12px
  "Детали": текст 12px + кнопка [JSON] ghost sm → открыть JsonDetailDialog

  Данные: log_service.get_logs(level, user, date, limit=50)
  Фильтр live: при изменении любого фильтра → refresh (с debounce 300ms)

JsonDetailDialog (маленький QDialog 480×340px):
  Заголовок: "Детали события"
  Содержимое: QTextEdit readonly + monospace font
  JSON форматируется через json.dumps(data, indent=2, ensure_ascii=False)
  Кнопка [Копировать] → clipboard

Пагинация:
  Лимит 50 на страницу, кнопки ← страница →
```

---

## Интеграция с MainWindow

### Подключить экраны в QStackedWidget

```python
# ui/windows/main_window.py — в секции инициализации admin-экранов

if app.current_user.role == "admin":
    self._admin_dashboard = AdminDashboard(container)
    self._admin_users     = AdminUsers(container)
    self._admin_system    = AdminSystem(container)
    self._admin_logs      = AdminLogs(container)

    self._stack.addWidget(self._admin_dashboard)   # индексы запомнить
    self._stack.addWidget(self._admin_users)
    self._stack.addWidget(self._admin_system)
    self._stack.addWidget(self._admin_logs)
```

### Admin-Sidebar

Сайдбар для роли admin — **отдельная конфигурация**, не переиспользовать студент/преп.
Отличия от других ролей:

```
Лого: "EduCase" + бейдж ADMIN (bg rgba(196,43,28,.25), color #ff8080)
Аватар-градиент: #C42B1C → #e85050 (красный, не синий)
Активная полоска пункта: #ff8080 (не #4DA3E8)
Фон активного пункта: rgba(196,43,28,.15) (не rgba(0,120,212,.18))

Пункты навигации:
  🏠 Панель управления   → admin_dashboard
  👥 Пользователи        → admin_users  + badge(count_all)
  ⚙️ Система             → admin_system
  📋 Журнал событий      → admin_logs + badge(warnings_count, цвет #F59E0B)
  ── Аккаунт ──
  👤 Профиль             → профиль
```

### bus.navigate_to — маппинг

```python
# core/event_bus.py — добавить маппинг admin-экранов:
ADMIN_ROUTES = {
    "admin_dashboard":   lambda: stack.setCurrentWidget(admin_dashboard),
    "admin_users":       lambda: stack.setCurrentWidget(admin_users),
    "admin_user_editor": lambda data: UserEditor(**data, parent=main_window).exec(),
    "admin_system":      lambda: stack.setCurrentWidget(admin_system),
    "admin_logs":        lambda: stack.setCurrentWidget(admin_logs),
}
```

---

## Асинхронные операции (обязательные правила)

Все операции с БД и FS выполнять через `run_async` из `core/thread_pool.py`:

```python
# ПРАВИЛО: никогда не вызывать сервисы напрямую из GUI-потока
# если операция > 100ms (VACUUM, бэкап, integrity_check, экспорт CSV)

# ШАБЛОН для кнопок с ожиданием:
def _run_heavy_task(self, btn: QPushButton, fn, success_msg: str):
    original_text = btn.text()
    btn.setEnabled(False)
    btn.setText("Выполняется...")

    def on_result(result):
        btn.setEnabled(True)
        btn.setText(original_text)
        bus.toast.emit("success", success_msg)

    def on_error(err):
        btn.setEnabled(True)
        btn.setText(original_text)
        bus.toast.emit("error", f"Ошибка: {err}")

    run_async(fn, on_result=on_result, on_error=on_error)
```

---

## Компонент: ConfirmDialog

Использовать везде где нужно подтверждение (удаление, блокировка, восстановление бэкапа):

```python
# ui/components/confirm_dialog.py — уже должен существовать (§8.1.3)

# Использование:
dlg = ConfirmDialog(
    title="Восстановить бэкап?",
    message=f"База данных будет заменена содержимым файла\n{filename}.\nПриложение перезапустится.",
    confirm_text="Восстановить",
    confirm_style="danger",   # "danger" | "primary"
    parent=self
)
if dlg.exec() == QDialog.Accepted:
    self._restore_backup(filename)
```

---

## Порядок реализации

```
Шаг 1:  ui/styles/dashboard_theme.py     ← ДОПОЛНИТЬ (не перезаписать)
Шаг 2:  ui/components/toggle_switch.py
Шаг 3:  ui/components/tab_bar.py
Шаг 4:  ui/components/role_badge.py      (RoleBadge + StatusBadge + LogLevelBadge)
Шаг 5:  ui/components/sysinfo_card.py
Шаг 6:  ui/components/data_table.py
Шаг 7:  ui/components/dock_panel.py
Шаг 8:  ui/components/backup_row.py
Шаг 9:  ui/components/db_table_row.py
Шаг 10: ui/windows/admin_dashboard.py    (A-1)
Шаг 11: ui/windows/admin_users.py        (A-2)
Шаг 12: ui/windows/admin_user_editor.py  (A-3 — QDialog)
Шаг 13: ui/windows/admin_system.py       (A-4 — 4 вкладки)
Шаг 14: ui/windows/admin_logs.py         (A-5)
Шаг 15: Подключить в MainWindow (admin sidebar + stack)
Шаг 16: Smoke-test: войти как admin (логин: admin, пароль: Admin1234)
```

---

## Чего НЕ делать

- ❌ Не изменять существующие компоненты студент/учитель — добавлять рядом
- ❌ Не перезаписывать `dashboard_theme.py` — только дополнять
- ❌ Не вызывать backup_service.create() и db_maintenance.vacuum() в GUI-потоке
- ❌ Не использовать QDialog.exec() для UserEditor если он открывается из run_async
- ❌ Не открывать DockPanel как отдельное окно — только как child поверх MainWindow
- ❌ Не делать ToggleSwitch через QCheckBox — только QPainter (для точного дизайна)
- ❌ Не трогать: auth_service.py, idle_guard.py, splash_window.py, event_bus.py

---

## Справочник компонент → HTML-класс

| Qt-компонент | HTML-класс в референсе |
|---|---|
| `SystemInfoCard` | `.sysinfo-card` + `.sysinfo-item` |
| `RoleBadge` | `.role-badge.role-admin/.role-teacher/.role-student` |
| `StatusBadge` | `.status-badge.status-active/.status-locked` |
| `LogLevelBadge` | `.log-badge.log-info/.log-warning/.log-error` |
| `DataTable` | `.data-table` |
| `DockPanel` | `.dock-panel` + `.dock-overlay` |
| `ToggleSwitch` | `.toggle` + `.toggle.off` |
| `TabBar` | `.tabs` + `.tab.active` |
| `BackupRow` | `.backup-row` |
| `DbTableRow` | `.db-row` + `.db-bar-wrap` |
| `UserEditor` | `.modal` + `.modal-stepper` |
| Admin TopBar | `.topbar` с title "Панель администратора" |
| Admin Sidebar | `.sidebar` + `.logo-admin-badge` + красная полоска |

---

## Справочник сервисов → методы

| Сервис | Метод | Используется в |
|---|---|---|
| `user_service` | `get_all() → list[User]` | A-2 таблица |
| `user_service` | `get_recent(limit) → list[User]` | A-1 последние регистрации |
| `user_service` | `count_all() → int` | A-1 стат-карточка |
| `user_service` | `count_by_role(role) → int` | A-1 стат-карточки |
| `user_service` | `count_by_roles() → dict` | A-1 пончик-чарт |
| `user_service` | `create_user(data) → User` | A-3 |
| `user_service` | `update_user(id, data) → User` | A-3 |
| `user_service` | `lock(id)` / `unlock(id)` | A-2 dock |
| `user_service` | `login_exists(login) → bool` | A-3 валидация |
| `backup_service` | `create() → Path` | A-1, A-4 |
| `backup_service` | `list_backups() → list[BackupInfo]` | A-4 |
| `backup_service` | `restore(path)` | A-4 |
| `backup_service` | `delete(path)` | A-4 |
| `backup_service` | `last_backup_age() → str` | A-1 sysinfo |
| `db_maintenance` | `get_db_size() → str` | A-1 sysinfo, A-4 |
| `db_maintenance` | `integrity_check() → bool` | A-1 sysinfo, A-4 |
| `db_maintenance` | `get_table_stats() → dict` | A-4 |
| `db_maintenance` | `vacuum()` | A-4 |
| `db_maintenance` | `analyze()` | A-4 |
| `analytics_service` | `get_activity_7days() → dict` | A-1 barchart |
| `log_service` | `get_logs(level, user, date, limit) → list` | A-5 |
| `log_service` | `count_warnings() → int` | A-1 sysinfo |
| `export_service` | `export_logs_csv()` | A-5 |
