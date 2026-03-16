# План коммита изменений UI

Цель: Зафиксировать исправления UI (логотип, цвета графиков, стили карточек) и предоставить пользователю данные для входа.

## Предложенные изменения

### UI Bug Fixes
Исправления, сделанные в текущей сессии:
- [educase/ui/styles/chart_style.py](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/styles/chart_style.py): Исправлен формат цвета Grid (RGBA -> HEX).
- [educase/ui/components/score_chart.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/score_chart.py): Исправлены цвета Matplotlib (RGBA -> HEX).
- [educase/ui/windows/teacher_dashboard.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/windows/teacher_dashboard.py): Исправлены цвета Matplotlib (RGBA -> HEX).
- [educase/ui/windows/login_window.py](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/windows/login_window.py): Переход на `QSvgWidget` для корректного отображения логотипа.
- [educase/ui/windows/splash_window.py](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/windows/splash_window.py): Обновлен метод рендеринга логотипа.
- [assets/icon_master.svg](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/assets/icon_master.svg): Очищен от неподдерживаемых Qt SVG фильтров.
- [educase/ui/components/stat_card.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/stat_card.py): Удалена серая обводка (фон иконки `transparent`).

### Прочие изменения
В репозитории обнаружено много других изменений (41 файл). Вероятно, это результат предыдущих сессий или автоматической генерации.
**ВАЖНО:** Я предложу команды для коммита только моих изменений, либо спрошу пользователя, нужно ли комитить все.

## Данные для входа (Logins/Passwords)
Я найду их в файлах сидирования БД и укажу в итоговом сообщении.

## Верификация
- [ ] Проверка `git status`
- [ ] Проверка `git diff` для ключевых файлов
- [ ] Формирование команд для пользователя
