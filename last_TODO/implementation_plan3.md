# План коммита изменений UI

Цель: Зафиксировать исправления UI (логотип, цвета графиков, стили карточек) и предоставить пользователю данные для входа.

## Предложенные изменения

### UI Implementations & Bug Fixes
Изменения текущей сессии и предыдущего этапа (Phase 6 & 7), которые еще не закоммичены:
- **Новые компоненты и экраны (Untracked):**
  - Дашборды студента и преподавателя ([student_dashboard.py](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/windows/student_dashboard.py), [teacher_dashboard.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/windows/teacher_dashboard.py)).
  - Компоненты графиков и статистики ([score_chart.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/score_chart.py), [stat_card.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/stat_card.py), [ring_progress.py](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/ring_progress.py), [heatmap_widget.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/heatmap_widget.py)).
  - Аналитика и лента активности ([teacher_analytics.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/windows/teacher_analytics.py), [activity_feed.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/activity_feed.py)).
- **Исправления UI:**
  - [educase/ui/styles/chart_style.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/styles/chart_style.py): Исправлен формат цвета Grid.
  - [educase/ui/windows/login_window.py](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/windows/login_window.py): Переход на `QSvgWidget` для логотипа.
  - [assets/icon_master.svg](file:///c:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/assets/icon_master.svg): Очистка SVG от фильтров.
  - [educase/ui/components/stat_card.py](file:///C:/Users/user/Desktop/Program/Educational-app-EduCase-/educase/ui/components/stat_card.py): Прозрачный фон иконок.

## Данные для входа (Учетные записи)
- **Админ:** `admin` / `admin_pass`
- **Преподаватель:** `teacher1` / `12345`
- **Студент:** `student1` / `12345`

## Команды для коммита
Я предложу пользователю следующие команды:
1. `git add .` (включая новые файлы и исправления)
2. `git commit -m "feat(ui): implement dashboards and fix styling issues"`
