# tests/unit/test_services.py
import pytest
from models.content import Discipline, Topic, Module, CaseGroup, Case
from models.task import Task
from services.case_service import CaseService
from services.module_service import ModuleService
from services.task_service import TaskService


def test_create_content_hierarchy(session, seed_users):
    """
    Тестирование создания иерархии: Discipline -> Topic -> Module -> CaseGroup -> Case -> Task
    В conftest.py у нас уже есть seed_users (admin: id 1)
    """
    mod_svc = ModuleService(session)
    case_svc = CaseService(session)
    task_svc = TaskService(session)
    
    # 1. Дисциплина
    disc = mod_svc.create_discipline("Хирургия", "Основы хирургии")
    assert disc.id is not None
    assert disc.name == "Хирургия"
    
    # 2. Тема
    topic = mod_svc.create_topic(disc.id, "Аппендицит")
    assert topic.id is not None
    assert topic.discipline_id == disc.id
    
    # 3. Модуль
    module = mod_svc.create_module(topic.id, "Острый аппендицит")
    assert module.id is not None
    
    # 4. Группа кейсов
    group = case_svc.create_group(module.id, "Диагностика")
    assert group.id is not None
    
    # 5. Кейс
    # В контесте фикстуры пользователь admin имеет ID 1
    case = case_svc.create_case(group.id, "Пациент 45 лет с болью в животе", author_id=1, difficulty=2)
    assert case.id is not None
    assert case.is_published is False
    
    # Публикация кейса
    case = case_svc.publish_case(case.id)
    assert case.is_published is True
    
    # 6. Задание
    task_config = {
        "options": [
            {"id": 1, "text": "УЗИ брюшной полости", "is_correct": True},
            {"id": 2, "text": "МРТ головного мозга", "is_correct": False}
        ]
    }
    task = task_svc.create_task(case.id, "SingleChoice", "Что назначить в первую очередь?", task_config)
    
    assert task.id is not None
    assert task.task_type == "SingleChoice"
    assert task.configuration["options"][0]["is_correct"] is True
    
    # Обновление конфига
    task_config["options"].append({"id": 3, "text": "КТ", "is_correct": False})
    task = task_svc.update_task_configuration(task.id, task_config)
    assert len(task.configuration["options"]) == 3
