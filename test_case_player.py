"""
Демо-тест экрана CasePlayer.
Запускает плеер с 5 тестовыми заданиями разных типов.
"""
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "educase"))

from PySide6.QtWidgets import QApplication
from educase.ui.screens.student.case_player import CasePlayer

def main():
    app = QApplication(sys.argv)

    # Демо-кейс с 5 заданиями разных типов
    case_data = {
        "name": "Демо-кейс: Основы физиологии",
        "time_limit_min": 0,  # без лимита для тестирования
        "tasks": [
            {
                "id": 1,
                "task_type": "single_choice",
                "title": "Вопрос 1",
                "body": "<b>Какой орган отвечает за фильтрацию крови?</b><br><br>Выберите один правильный ответ из предложенных вариантов.",
                "max_score": 2,
                "hint": "Этот орган расположен в брюшной полости",
                "explanation": "Почки фильтруют кровь, удаляя отходы и лишнюю жидкость.",
                "topic": "Анатомия выделительной системы",
                "configuration": {
                    "options": [
                        {"id": 1, "text": "Печень", "is_correct": False},
                        {"id": 2, "text": "Почки", "is_correct": True},
                        {"id": 3, "text": "Селезёнка", "is_correct": False},
                        {"id": 4, "text": "Поджелудочная железа", "is_correct": False},
                    ]
                }
            },
            {
                "id": 2,
                "task_type": "multi_choice",
                "title": "Вопрос 2",
                "body": "<b>Какие из перечисленных веществ являются витаминами?</b><br>Выберите все правильные ответы.",
                "max_score": 3,
                "hint": "Их четыре в списке",
                "explanation": "Витамины A, C, D и группы B — органические вещества, необходимые организму.",
                "topic": "Биохимия и витамины",
                "configuration": {
                    "options": [
                        {"id": 1, "text": "Витамин A (ретинол)", "is_correct": True},
                        {"id": 2, "text": "Кальций", "is_correct": False},
                        {"id": 3, "text": "Витамин C (аскорбиновая кислота)", "is_correct": True},
                        {"id": 4, "text": "Железо", "is_correct": False},
                        {"id": 5, "text": "Витамин D", "is_correct": True},
                    ]
                }
            },
            {
                "id": 3,
                "task_type": "text_input",
                "title": "Вопрос 3",
                "body": "<b>Как называется процесс деления клетки, при котором образуются две генетически идентичные дочерние клетки?</b>",
                "max_score": 1,
                "hint": "Начинается на букву 'М'",
                "explanation": "Митоз — деление клетки с сохранением числа хромосом.",
                "topic": "Клеточная биология",
                "configuration": {
                    "correct_answers": ["Митоз", "митоз", "МИТОЗ"],
                    "case_sensitive": False,
                }
            },
            {
                "id": 4,
                "task_type": "ordering",
                "title": "Вопрос 4",
                "body": "<b>Расположите этапы митоза в правильном порядке:</b>",
                "max_score": 2,
                "hint": "Профаза идёт первой",
                "explanation": "Правильный порядок: Профаза → Метафаза → Анафаза → Телофаза",
                "topic": "Фазы клеточного деления",
                "configuration": {
                    "items": [
                        {"id": 1, "text": "Метафаза", "order": 2},
                        {"id": 2, "text": "Телофаза", "order": 4},
                        {"id": 3, "text": "Профаза", "order": 1},
                        {"id": 4, "text": "Анафаза", "order": 3},
                    ]
                }
            },
            {
                "id": 5,
                "task_type": "calculation",
                "title": "Вопрос 5",
                "body": "<b>Рассчитайте индекс массы тела (ИМТ) для пациента:</b><br>Масса тела: <b>75 кг</b>, Рост: <b>1.75 м</b><br><br>Формула: ИМТ = масса / рост²",
                "max_score": 2,
                "hint": "75 / (1.75 × 1.75)",
                "explanation": "ИМТ = 75 / 3.0625 ≈ 24.49",
                "topic": "Клиническая антропометрия",
                "configuration": {
                    "target_value": 24.49,
                    "error_margin": 0.1,
                    "unit": "кг/м²",
                }
            },
        ]
    }

    player = CasePlayer(case_data)
    result = player.exec()

    if result:
        # Показать результат
        from educase.ui.screens.student.case_result import CaseResultDialog
        result_data = {
            "case_name": case_data["name"],
            "score_earned": 7.5,
            "score_max": 10,
            "time_spent_seconds": 125,
            "tasks": [
                {"topic": "Анатомия выделительной системы"},
                {"topic": "Биохимия и витамины"},
                {"topic": "Клеточная биология"},
                {"topic": "Фазы клеточного деления"},
                {"topic": "Клиническая антропометрия"},
            ]
        }
        dlg = CaseResultDialog(result_data)
        dlg.exec()

    print("Готово!")

if __name__ == "__main__":
    main()
