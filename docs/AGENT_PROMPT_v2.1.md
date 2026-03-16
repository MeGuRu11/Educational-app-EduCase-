# ПРОМПТ ДЛЯ AI-АГЕНТА: EduCase v2.1 — Учёт изменений сессионного управления

## Контекст

Ты работаешь над проектом **EduCase** — десктопное PySide6-приложение для прохождения
интерактивных медицинских кейсов. Вся архитектура описана в файле `PROJECT_DESIGN_v2.1.md`.

**Критически важное условие эксплуатации, которое необходимо учесть:**
Приложение работает на **одном компьютере в учебном кабинете**.
Студенты и преподаватели работают **по очереди**, каждый под своим логином.
Это не сетевое приложение — данные между устройствами не передаются.

---

## Что изменилось в v2.1 (относительно v2.0)

В спецификацию добавлен раздел **§8.1** и сопутствующие изменения.
Прочитай эти разделы в PROJECT_DESIGN_v2.1.md **перед тем, как писать любой код**.

### Список изменений:

**1. Новый файл: `core/idle_guard.py`** (§8.1.2)
Реализовать класс `IdleGuard` точно по коду в §8.1.2. Никаких отклонений.
Файл уже добавлен в дерево проекта (§7) и в TODO-лист (§10).

**2. Новый сигнал в `core/event_bus.py`**
Добавить сигнал `idle_logout = Signal()` в класс `EventBus` (уже прописан в §4.1).

**3. Изменения в `core/di_container.py`** (§4.2)
- В датакласс `Container` добавить поле: `idle_guard: "IdleGuard | None" = None`
- В функцию `build_container()` в конце (после `BackupService`) добавить:
  ```python
  from core.idle_guard import IdleGuard
  c.idle_guard = IdleGuard()
  c.auth_service._attempt_service_ref = c.attempt_service
  ```

**4. Изменения в `services/auth_service.py`** (§8.1.5)
Методы `login()` и `logout()` реализовать по логике из §8.1.5:
- `login()`: перед установкой `current_user` — проверять `app.current_user is not None`
- `login()`: после успешного входа вызывать `app.idle_guard.start()`
- `logout()`: перед сбросом `current_user` — вызывать `attempt_service.abandon()` если есть активная попытка
- `logout()`: вызывать `app.idle_guard.stop()` перед `bus.user_logged_out.emit()`

**5. Изменения в `ui/windows/main_window.py`**
- Подписаться на `bus.idle_logout` → вызывать `auth_service.logout()`
- При показе Toast при автовыходе: «Выход по бездействию (15 мин)»
- Подписаться на `bus.user_logged_out` → вызывать `self.hide()` + `login_window.reset_for_next_user()` + `login_window.show()`
- **НЕ вызывать `QApplication.quit()` при logout** — приложение продолжает работать

**6. Изменения в `ui/windows/login_window.py`** (§8.1.4)
Добавить публичный метод `reset_for_next_user()`:
```python
def reset_for_next_user(self):
    self.login_field.clear()
    self.password_field.clear()
    self.error_label.hide()
    self.login_field.setFocus()
```

**7. Изменения в `ui/windows/case_player.py`** (§8.1.3)
Кнопка **[← Выйти]** в CasePlayer должна:
- Показывать `ConfirmDialog` с текстом: «Текущая попытка будет прервана и засчитана как незавершённая. Выйти?»
- При подтверждении: `attempt_service.abandon(current_attempt)` → `auth_service.logout()`
- При отмене: ничего не делать

**8. Кнопка Logout в Sidebar** (§8.1.3)
- Если есть активная попытка → тот же `ConfirmDialog`
- Если нет → выход немедленно (без диалога)

**9. `main.py` — завершение приложения** (§8.1.1)
`QApplication.quit()` вызывается **только** из `closeEvent` главного окна (`MainWindow`).
Не добавлять `app.quit()` или `sys.exit()` в логику logout.

---

## Готовые файлы (не генерировать, использовать из архива)

В архиве `educase_sources.zip` находятся готовые исходники (см. §16 → «ГОТОВЫЕ ИСХОДНИКИ»):

| Файл | Статус |
|------|--------|
| `assets/icon_master.svg` | ✅ Готов — не изменять |
| `tools/make_ico.py` | ✅ Готов — запустить однократно |
| `ui/windows/splash_window.py` | ✅ Готов — не переписывать |
| `main.py` | ✅ Готов — только дополнить импортами если нужно |

---

## Порядок реализации (рекомендуемый)

```
Этап 0: Распаковать educase_sources.zip → python tools/make_ico.py
Этап 1: core/idle_guard.py                ← новый файл
Этап 2: core/event_bus.py                 ← добавить idle_logout
Этап 3: core/di_container.py              ← IdleGuard в Container + build_container
Этап 4: services/auth_service.py          ← login/logout с idle_guard
Этап 5: ui/windows/login_window.py        ← reset_for_next_user()
Этап 6: ui/windows/main_window.py         ← подписки на idle_logout / user_logged_out
Этап 7: ui/windows/case_player.py         ← ConfirmDialog при выходе
Этап 8: Smoke-test (§16 → ШАГ 5)
```

---

## Чего НЕ делать

- ❌ Не закрывать приложение (`app.quit()`) при logout пользователя
- ❌ Не сохранять логин в поле после выхода — общий ПК, приватность
- ❌ Не показывать ConfirmDialog при автовыходе по таймеру (пользователя нет за ПК)
- ❌ Не переписывать `splash_window.py` — он уже готов и выверен
- ❌ Не изменять тайминги анимации splash — они согласованы с HTML-превью
- ❌ Не генерировать `icon_master.svg` — он уже готов, использовать из архива

---

## Справочник по ключевым параметрам

| Параметр | Значение | Где |
|---|---|---|
| Idle timeout | 15 минут (900 000 мс) | `core/idle_guard.py` → `IDLE_TIMEOUT_MS` |
| Активные события | MouseMove, MouseButtonPress, KeyPress, Wheel, TouchBegin | `ACTIVITY_EVENTS` |
| Статус прерванной попытки | `'abandoned'` | `attempts.status` в БД |
| Сигнал автовыхода | `bus.idle_logout` | EventBus |
| Сигнал штатного выхода | `bus.user_logged_out` | EventBus |
| Текст ConfirmDialog | «Текущая попытка будет прервана и засчитана как незавершённая. Выйти?» | CasePlayer / Sidebar |
| Toast при автовыходе | «Выход по бездействию (15 мин)» | MainWindow |
