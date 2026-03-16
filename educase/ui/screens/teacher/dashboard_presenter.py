# educase/ui/screens/teacher/dashboard_presenter.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TeacherStat:
    label: str
    value: str
    delta: str
    delta_type: str
    icon_svg: str = ""
    accent: str = "#0078D4"

@dataclass
class ActivityEvent:
    name: str
    action: str
    score: Optional[int] = None
    time: str = ""
    type: str = "info"

class TeacherDashboardPresenter:
    def __init__(self, view, container):
        self.view = view
        self.container = container

    def load_data(self):
        """Загрузка реальных данных для дашборда преподавателя."""
        if not self.container:
            return

        user_repo = self.container.user_repo
        attempt_repo = self.container.attempt_repo
        case_repo = self.container.case_repo
        group_repo = self.container.group_repo

        # 1. Stats
        cases_count = case_repo.count_published()
        students_count = user_repo.count_by_role("student")
        attempts_today = attempt_repo.count_today()
        avg_score = attempt_repo.get_avg_score()

        stats = [
            TeacherStat("МОИ КЕЙСЫ", str(cases_count), "", "neutral", 
                        '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5z"/><path d="M8 7h6M8 11h8"/>'),
            TeacherStat("СТУДЕНТОВ", str(students_count), "Всего в системе", "neutral", 
                        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
                        "#107C10"),
            TeacherStat("ПОПЫТОК СЕГОДНЯ", str(attempts_today), "Активность", "neutral", 
                        '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
                        "#4DA3E8"),
            TeacherStat("СР. БАЛЛ", f"{avg_score:.1f}%", "Успеваемость", "neutral", 
                        '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
                        "#F59E0B")
        ]
        
        # 2. Chart Data (Real)
        chart_data = attempt_repo.get_daily_stats(days=7)
        
        # 3. Activity Feed (Real)
        recent_attempts = attempt_repo.get_recent_activity(limit=10)
        events = []
        for att in recent_attempts:
            user_name = att.user.full_name if att.user else "Anon"
            case_name = att.case.title if att.case else "Кейс"
            
            status_map = {
                "completed": ("завершил", "success"),
                "failed": ("не справился с", "fail"),
                "in_progress": ("начал", "start")
            }
            action_verb, evt_type = status_map.get(att.status, ("участвует в", "info"))
            
            events.append(ActivityEvent(
                name=user_name,
                action=f"{action_verb} \"{case_name}\"",
                score=int(att.score_earned) if att.status == "completed" else None,
                time="недавно",
                type=evt_type
            ))
        
        if not events: # Fallback if empty
            events = [ActivityEvent("Система", "ожидает новых активностей", None, "сейчас", "info")]

        # 4. Groups (Real)
        groups = group_repo.get_all(limit=3)
        group_list = []
        for g in groups:
            group_list.append({
                "title": g.name,
                "subtitle": f"Группа #{g.id}", # Or more specific info if available
                "icon": "🏥",
                "cases": [],
                "stats": {"students": 0, "cases": 0, "avg_score": 0}
            })

        self.view.display_stats(stats)
        self.view.display_chart(chart_data)
        self.view.display_feed(events)
        self.view.display_groups(group_list)
