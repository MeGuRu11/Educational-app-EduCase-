# services/grader_service.py
"""
Сервис автопроверки ответов для всех 12 типов заданий.
Принимает конфигурацию задания и данные ответа студента,
возвращает GradeResult.
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class GradeResult:
    """Результат проверки одного задания."""
    is_correct: bool
    score: float          # Заработанные баллы
    max_score: float      # Максимум
    feedback: str = ""    # Текст обратной связи


class GraderService:
    """
    Автоматическая проверка ответов.
    Каждый метод grade_* принимает:
        config  — Task.configuration (dict, правильные ответы)
        answer  — answer_data (dict, что ввёл студент)
        max_score — максимальный балл за задание
    """

    def grade(self, task_type: str, config: dict, answer: dict,
              max_score: float = 1.0) -> GradeResult:
        """Единый вход: по task_type выбирает проверяющую функцию."""
        graders = {
            "single_choice": self._grade_single_choice,
            "multi_choice": self._grade_multi_choice,
            "text_input": self._grade_text_input,
            "form_fill": self._grade_form_fill,
            "ordering": self._grade_ordering,
            "matching": self._grade_matching,
            "calculation": self._grade_calculation,
            "image_annotation": self._grade_image_annotation,
            "timeline": self._grade_timeline,
            "table_input": self._grade_table_input,
            "document_editor": self._grade_document,
            "branching": self._grade_branching,
        }
        fn = graders.get(task_type)
        if not fn:
            return GradeResult(
                is_correct=False, score=0, max_score=max_score,
                feedback=f"Неизвестный тип задания: {task_type}"
            )
        return fn(config, answer, max_score)

    # ── single_choice ────────────────────────────────────────────────────
    def _grade_single_choice(self, config: dict, answer: dict,
                             max_score: float) -> GradeResult:
        options = config.get("options", [])
        correct_id = None
        for opt in options:
            if opt.get("is_correct"):
                correct_id = opt.get("id")
                break

        selected = answer.get("selected_option_id")
        is_correct = selected is not None and str(selected) == str(correct_id)

        return GradeResult(
            is_correct=is_correct,
            score=max_score if is_correct else 0,
            max_score=max_score,
            feedback="Правильно!" if is_correct else "Неверный ответ."
        )

    # ── multi_choice ─────────────────────────────────────────────────────
    def _grade_multi_choice(self, config: dict, answer: dict,
                            max_score: float) -> GradeResult:
        options = config.get("options", [])
        correct_ids = {str(o["id"]) for o in options if o.get("is_correct")}
        selected_ids = {str(s) for s in answer.get("selected_option_ids", [])}

        if not correct_ids:
            return GradeResult(True, max_score, max_score, "Нет правильных ответов.")

        # Частичные баллы: правильные - штраф за лишние
        correct_selected = correct_ids & selected_ids
        wrong_selected = selected_ids - correct_ids

        if correct_selected == correct_ids and not wrong_selected:
            return GradeResult(True, max_score, max_score, "Все ответы верны!")

        # Частичный балл
        partial = len(correct_selected) / len(correct_ids)
        penalty = len(wrong_selected) / max(len(options) - len(correct_ids), 1)
        score = max(0, partial - penalty) * max_score
        score = round(score, 2)

        return GradeResult(
            is_correct=False,
            score=score,
            max_score=max_score,
            feedback=f"Частично верно: {len(correct_selected)}/{len(correct_ids)} правильных."
        )

    # ── text_input ───────────────────────────────────────────────────────
    def _grade_text_input(self, config: dict, answer: dict,
                          max_score: float) -> GradeResult:
        correct_answers = config.get("correct_answers", [])
        case_sensitive = config.get("case_sensitive", False)
        user_text = answer.get("text", "").strip()

        if not user_text:
            return GradeResult(False, 0, max_score, "Ответ не дан.")

        for correct in correct_answers:
            if case_sensitive:
                if user_text == correct.strip():
                    return GradeResult(True, max_score, max_score, "Верно!")
            else:
                if user_text.lower() == correct.strip().lower():
                    return GradeResult(True, max_score, max_score, "Верно!")

        return GradeResult(False, 0, max_score, "Неверный ответ.")

    # ── form_fill ────────────────────────────────────────────────────────
    def _grade_form_fill(self, config: dict, answer: dict,
                         max_score: float) -> GradeResult:
        correct_answers = config.get("answers", {})  # {"1": "кошка", "word": "собака"}
        user_answers = answer.get("answers", {})      # {"1": "кошка", "word": "кот"}

        if not correct_answers:
            return GradeResult(True, max_score, max_score)

        total = len(correct_answers)
        correct_count = 0

        for token, expected in correct_answers.items():
            user_val = user_answers.get(token, "").strip()
            if user_val.lower() == expected.strip().lower():
                correct_count += 1

        is_correct = correct_count == total
        score = (correct_count / total) * max_score if total > 0 else 0
        score = round(score, 2)

        return GradeResult(
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=f"Верно {correct_count} из {total} пропусков."
        )

    # ── ordering ─────────────────────────────────────────────────────────
    def _grade_ordering(self, config: dict, answer: dict,
                        max_score: float) -> GradeResult:
        items = config.get("items", [])
        correct_order = [item["id"] for item in sorted(items, key=lambda x: x.get("order", 0))]
        user_order = answer.get("order", [])

        if not correct_order:
            return GradeResult(True, max_score, max_score)

        if len(user_order) != len(correct_order):
            return GradeResult(False, 0, max_score, "Не все элементы размещены.")

        # Подсчёт правильных позиций
        correct_positions = sum(
            1 for i, item_id in enumerate(user_order)
            if i < len(correct_order) and str(item_id) == str(correct_order[i])
        )
        total = len(correct_order)

        is_correct = correct_positions == total
        score = (correct_positions / total) * max_score if total > 0 else 0
        score = round(score, 2)

        return GradeResult(
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=f"Верных позиций: {correct_positions}/{total}."
        )

    # ── matching ─────────────────────────────────────────────────────────
    def _grade_matching(self, config: dict, answer: dict,
                        max_score: float) -> GradeResult:
        pairs = config.get("pairs", [])
        correct_map = {str(p["id"]): p["right"] for p in pairs}
        user_map = answer.get("matches", {})  # {"pair_0": "Определение A", ...}

        if not correct_map:
            return GradeResult(True, max_score, max_score)

        total = len(correct_map)
        correct_count = 0

        for pair_id, expected_right in correct_map.items():
            user_right = user_map.get(pair_id, "").strip()
            if user_right.lower() == expected_right.strip().lower():
                correct_count += 1

        is_correct = correct_count == total
        score = (correct_count / total) * max_score if total > 0 else 0
        score = round(score, 2)

        return GradeResult(
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=f"Верных пар: {correct_count}/{total}."
        )

    # ── calculation ──────────────────────────────────────────────────────
    def _grade_calculation(self, config: dict, answer: dict,
                           max_score: float) -> GradeResult:
        target = float(config.get("target_value", 0))
        margin = float(config.get("error_margin", 0))

        try:
            user_val = float(answer.get("value", ""))
        except (ValueError, TypeError):
            return GradeResult(False, 0, max_score, "Введите числовое значение.")

        is_correct = abs(user_val - target) <= margin

        return GradeResult(
            is_correct=is_correct,
            score=max_score if is_correct else 0,
            max_score=max_score,
            feedback="Верно!" if is_correct else f"Неверно. Ожидалось: {target} ± {margin}."
        )

    # ── image_annotation ─────────────────────────────────────────────────
    def _grade_image_annotation(self, config: dict, answer: dict,
                                max_score: float) -> GradeResult:
        correct_zones = config.get("zones", [])
        user_zones = answer.get("zones", [])

        if not correct_zones:
            return GradeResult(True, max_score, max_score)

        matched = 0
        for cz in correct_zones:
            for uz in user_zones:
                iou = self._calc_iou(cz, uz)
                if iou >= 0.3:
                    matched += 1
                    break

        total = len(correct_zones)
        is_correct = matched == total
        score = (matched / total) * max_score if total > 0 else 0
        score = round(score, 2)

        return GradeResult(
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=f"Найдено зон: {matched}/{total}."
        )

    @staticmethod
    def _calc_iou(zone_a: dict, zone_b: dict) -> float:
        """Intersection over Union для двух прямоугольников {x,y,w,h}."""
        ax, ay = zone_a.get("x", 0), zone_a.get("y", 0)
        aw, ah = zone_a.get("w", 0), zone_a.get("h", 0)
        bx, by = zone_b.get("x", 0), zone_b.get("y", 0)
        bw, bh = zone_b.get("w", 0), zone_b.get("h", 0)

        x1 = max(ax, bx)
        y1 = max(ay, by)
        x2 = min(ax + aw, bx + bw)
        y2 = min(ay + ah, by + bh)

        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area_a = aw * ah
        area_b = bw * bh
        union = area_a + area_b - inter

        return inter / union if union > 0 else 0.0

    # ── timeline ─────────────────────────────────────────────────────────
    def _grade_timeline(self, config: dict, answer: dict,
                        max_score: float) -> GradeResult:
        events = config.get("events", [])
        correct_order = [e["id"] for e in sorted(events, key=lambda x: x.get("order", 0))]
        user_order = answer.get("order", [])

        if not correct_order:
            return GradeResult(True, max_score, max_score)

        correct_positions = sum(
            1 for i, eid in enumerate(user_order)
            if i < len(correct_order) and str(eid) == str(correct_order[i])
        )
        total = len(correct_order)
        is_correct = correct_positions == total
        score = (correct_positions / total) * max_score if total > 0 else 0
        score = round(score, 2)

        return GradeResult(
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=f"Верных позиций: {correct_positions}/{total}."
        )

    # ── table_input ──────────────────────────────────────────────────────
    def _grade_table_input(self, config: dict, answer: dict,
                           max_score: float) -> GradeResult:
        correct_cells = config.get("cells", [])
        header_row = config.get("header_row", True)
        header_col = config.get("header_col", False)
        user_cells = answer.get("cells", [])

        total = 0
        correct_count = 0

        for r, row in enumerate(correct_cells):
            for c, expected in enumerate(row):
                # Пропускаем заголовочные ячейки
                if header_row and r == 0:
                    continue
                if header_col and c == 0:
                    continue

                total += 1
                user_val = ""
                if r < len(user_cells) and c < len(user_cells[r]):
                    user_val = str(user_cells[r][c]).strip()

                if user_val.lower() == str(expected).strip().lower():
                    correct_count += 1

        if total == 0:
            return GradeResult(True, max_score, max_score)

        is_correct = correct_count == total
        score = (correct_count / total) * max_score
        score = round(score, 2)

        return GradeResult(
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=f"Верных ячеек: {correct_count}/{total}."
        )

    # ── document_editor ──────────────────────────────────────────────────
    def _grade_document(self, config: dict, answer: dict,
                        max_score: float) -> GradeResult:
        questions = config.get("questions", [])
        user_answers = answer.get("answers", [])

        if not questions:
            return GradeResult(True, max_score, max_score)

        total = len(questions)
        correct_count = 0

        for i, q in enumerate(questions):
            expected = q.get("answer", "").strip().lower()
            user_ans = ""
            if i < len(user_answers):
                user_ans = str(user_answers[i]).strip().lower()

            if user_ans == expected:
                correct_count += 1

        is_correct = correct_count == total
        score = (correct_count / total) * max_score if total > 0 else 0
        score = round(score, 2)

        return GradeResult(
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=f"Верных ответов: {correct_count}/{total}."
        )

    # ── branching ────────────────────────────────────────────────────────
    def _grade_branching(self, config: dict, answer: dict,
                         max_score: float) -> GradeResult:
        """
        Ветвление проверяется через ScenarioService.
        Здесь просто фиксируем выбор — баллы начисляются
        в зависимости от финального узла сценария (осознанное решение: любой выбор корректен для навигации).
        """
        selected_edge = answer.get("selected_edge_id")
        if selected_edge is not None:
            return GradeResult(
                is_correct=True,
                score=max_score,
                max_score=max_score,
                feedback="Выбор принят."
            )
        return GradeResult(False, 0, max_score, "Вариант не выбран.")
