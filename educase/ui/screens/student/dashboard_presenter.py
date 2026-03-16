# educase/ui/screens/student/dashboard_presenter.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class StudentStat:
    label: str
    value: str
    delta: str
    delta_type: str
    icon_svg: str
    accent: Optional[str] = None
    icon_bg: Optional[str] = None

@dataclass
class ActiveCaseInfo:
    title: str
    subtitle: str
    progress: int
    score_info: str

@dataclass
class HistoryEntry:
    name: str
    score: int
    grade: int
    date: str

class StudentDashboardPresenter:
    def __init__(self, view, container):
        self.view = view
        self.container = container

    def load_data(self):
        """Загрузка реальных данных для дашборда студента."""
        import app
        if not self.container or not app.current_user:
            return

        user_id = app.current_user.id
        attempt_repo = self.container.attempt_repo
        case_repo = self.container.case_repo

        # 1. Stats
        total_cases = case_repo.count_published()
        user_attempts = attempt_repo.get_all_for_user(user_id)
        completed_count = len([a for a in user_attempts if a.status == "completed"])
        avg_score = attempt_repo.get_avg_score(user_id)

        stats = [
            StudentStat("ДОСТУПНО КЕЙСОВ", str(total_cases), "Всего", "neutral", 
                        '<rect x="4" y="4" width="16" height="16" rx="3" stroke="#0078D4" stroke-width="2"/>'),
            StudentStat("ВЫПОЛНЕНО", str(completed_count), "Попыток", "neutral", 
                        '<circle cx="12" cy="12" r="8" stroke="#107C10" stroke-width="2"/>'
                        '<path d="M8 12l3 3 5-5" stroke="#107C10" stroke-width="2"/>',
                         "#107C10", "#DFF6DD"),
            StudentStat("СРЕДНИЙ БАЛЛ", f"{avg_score:.1f}%", "Успеваемость", "neutral", 
                        '<path d="M4 18h16M4 12h16M4 6h16" stroke="#4DA3E8" stroke-width="2"/>',
                        "#4DA3E8", "#EFF6FC")
        ]
        
        # 2. Active Case (Find first in_progress)
        active_att = next((a for a in user_attempts if a.status == "in_progress"), None)
        active_case = None
        if active_att:
            title = active_att.case.title if active_att.case else "Текущий кейс"
            # Для прогресса пока заглушка, если нет поля progress в Attempt
            active_case = ActiveCaseInfo(
                title,
                "Продолжите изучение",
                50, f"Набранный балл: {active_att.score_earned:.0f}"
            )
        
        # 3. Chart Data (History of scores)
        recent_5 = user_attempts[:5][::-1] # 5 последних, в хронологическом порядке
        chart_data = {
            "labels": [a.started_at[:10] if a.started_at else "—" for a in recent_5],
            "values": [int(a.score_earned) for a in recent_5]
        }
        if not chart_data["values"]:
            chart_data = {"labels": ["Нет данных"], "values": [0]}
        
        # 4. History
        history = []
        for a in user_attempts[:10]:
            case_name = a.case.title if a.case else "Кейс"
            # Оценка (grade) — упрощенный расчет
            grade = 5 if a.score_earned >= 85 else (4 if a.score_earned >= 70 else (3 if a.score_earned >= 50 else 2))
            history.append(HistoryEntry(
                case_name, int(a.score_earned), grade, a.finished_at[:10] if a.finished_at else "—"
            ))
        
        self.view.display_stats(stats)
        if active_case:
            self.view.display_active_case(active_case)
        self.view.display_chart(chart_data)
        self.view.display_history(history)
