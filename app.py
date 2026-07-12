#!/usr/bin/env python3
"""Local web interface for the DSA manager.

Run `python3 app.py`, then open http://127.0.0.1:8000 in a browser.
"""

from __future__ import annotations

import json
import tempfile
from datetime import date, datetime, timedelta
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dsa_manager import (
    PROGRESS_FILE,
    QUESTION_FILE,
    REVISION_INTERVALS,
    ensure_question_for_problem,
    find_problem,
    load_progress,
    load_questions,
    question_matches_problem,
    save_question_for_problem,
    run_class_method,
    run_script,
    save_json,
)
from upload import TOPICS, detect_patterns, display_topic, slugify_problem_name, update_readme, upsert_problem


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
TOPIC_FILE = ROOT / ".dsa_topics.json"


def question_for_problem(problem_name: str, questions: list[dict]) -> dict | None:
    return next((question for question in questions if question_matches_problem(question, problem_name)), None)


def dashboard_data() -> dict:
    progress = load_progress()
    # Repair any older upload that saved the solution but stopped before its
    # generated revision prompt was written.
    for problem in progress["problems"]:
        ensure_question_for_problem(problem)
    questions = load_questions()
    today = date.today()
    problems = []
    for problem in progress["problems"]:
        item = dict(problem)
        due = date.fromisoformat(item["revision_due"])
        item["days_until_revision"] = (due - today).days
        item["practice_question"] = question_for_problem(item["problem"], questions)
        problems.append(item)
    problems.sort(key=lambda item: (item["revision_due"], item["problem"]))
    return {
        "today": today.isoformat(),
        "total_solved": len(problems),
        "due_today": sum(item["days_until_revision"] <= 0 for item in problems),
        "topics": len({item.get("topic", "General") for item in problems}),
        "problems": problems,
    }


def topic_options() -> list[dict[str, str]]:
    defaults = [{"directory": directory, "name": display_topic(directory)} for directory in TOPICS.values()]
    custom = json.loads(TOPIC_FILE.read_text(encoding="utf-8")) if TOPIC_FILE.exists() else []
    return defaults + custom


def topic_directory(topic_name: str) -> tuple[str, str]:
    clean_name = topic_name.strip()
    for topic in topic_options():
        if topic["name"].casefold() == clean_name.casefold():
            return topic["directory"], topic["name"]
    if not clean_name or len(clean_name) > 50:
        raise ValueError("Enter a category name between 1 and 50 characters.")
    slug = slugify_problem_name(clean_name).strip("_")
    if not slug:
        raise ValueError("Category name must contain letters or numbers.")
    existing_numbers = [int(item["directory"].split("_", 1)[0]) for item in topic_options() if item["directory"].split("_", 1)[0].isdigit()]
    directory = f"{max(existing_numbers, default=0) + 1:02d}_{slug}"
    custom = json.loads(TOPIC_FILE.read_text(encoding="utf-8")) if TOPIC_FILE.exists() else []
    custom.append({"directory": directory, "name": clean_name})
    save_json(TOPIC_FILE, custom)
    return directory, clean_name


def save_solution(payload: dict) -> dict:
    problem_name = str(payload.get("problem", "")).strip()
    code = str(payload.get("code", ""))
    difficulty = str(payload.get("difficulty", ""))
    question_detail = str(payload.get("question_detail", "")).strip()
    if not problem_name:
        raise ValueError("Enter a problem name.")
    if not code.strip():
        raise ValueError("Paste your Python solution before saving.")
    if difficulty not in {"Easy", "Medium", "Hard"}:
        raise ValueError("Choose Easy, Medium, or Hard.")

    directory, topic_name = topic_directory(str(payload.get("topic", "")))
    destination = ROOT / directory / difficulty / f"{slugify_problem_name(problem_name)}.py"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(code.rstrip() + "\n", encoding="utf-8")
    progress = load_progress()
    saved, was_revision = upsert_problem(
        progress,
        {
            "problem": problem_name,
            "topic": topic_name,
            "topic_dir": directory,
            "difficulty": difficulty,
            "path": destination.relative_to(ROOT).as_posix(),
            "patterns": detect_patterns(problem_name, directory, code),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    save_json(PROGRESS_FILE, progress)
    if question_detail:
        prompt_added = True
        generated_question = save_question_for_problem(saved, question_detail)
    else:
        prompt_added = ensure_question_for_problem(saved)
        generated_question = next(
            (question for question in load_questions() if question_matches_problem(question, saved["problem"])),
            None,
        )
    update_readme(progress)
    return {
        "message": f"{'Updated revision' if was_revision else 'Saved solution'} in {destination.relative_to(ROOT)}.",
        "prompt_added": prompt_added,
        "question": generated_question,
        "dashboard": dashboard_data(),
        "topics": topic_options(),
    }


def delete_solution(problem_name: str) -> dict:
    progress = load_progress()
    problem = find_problem(progress["problems"], problem_name)
    if not problem:
        raise ValueError("Saved problem not found.")
    solution_path = (ROOT / problem["path"]).resolve()
    if ROOT not in solution_path.parents:
        raise ValueError("Invalid saved solution path.")
    if solution_path.is_file():
        solution_path.unlink()
    progress["problems"] = [item for item in progress["problems"] if item is not problem]
    save_json(PROGRESS_FILE, progress)
    update_readme(progress)

    # Preserve hand-written question cards. Remove only an orphaned generated card.
    remaining = progress["problems"]
    questions = load_questions()
    kept = [
        question
        for question in questions
        if not (
            question.get("auto_generated")
            and question_matches_problem(question, problem["problem"])
            and not any(question_matches_problem(question, item["problem"]) for item in remaining)
        )
    ]
    if len(kept) != len(questions):
        save_json(QUESTION_FILE, kept)
    return {"message": f"Deleted '{problem['problem']}'.", "dashboard": dashboard_data()}


def judge_solution(code: str, question_id: str) -> dict:
    question = next((item for item in load_questions() if item["id"] == question_id), None)
    if not question:
        raise ValueError("Unknown practice question.")
    if not code.strip():
        raise ValueError("Paste your Python solution before running tests.")

    results = []
    with tempfile.TemporaryDirectory(prefix="dsa-manager-") as directory:
        candidate = Path(directory) / "solution.py"
        candidate.write_text(code, encoding="utf-8")
        for number, test in enumerate(question.get("tests", []), start=1):
            if question.get("runner", "stdin") == "class_method":
                ok, actual = run_class_method(candidate, question["method"], test.get("args", []))
                expected = test["expected"]
                shown_input = test.get("args", [])
                passed = ok and actual == expected
            else:
                ok, actual = run_script(candidate, test.get("input", ""))
                expected = str(test["expected"]).strip()
                shown_input = test.get("input", "").rstrip("\n")
                passed = ok and actual == expected
            results.append(
                {
                    "number": number,
                    "input": shown_input,
                    "expected": expected,
                    "actual": actual,
                    "passed": passed,
                }
            )
    return {"title": question["title"], "passed": sum(item["passed"] for item in results), "total": len(results), "results": results}


class DSAHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def send_json(self, data: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/dashboard":
            self.send_json(dashboard_data())
            return
        if path == "/api/questions":
            self.send_json({"questions": load_questions()})
            return
        if path == "/api/topics":
            self.send_json({"topics": topic_options()})
            return
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        try:
            path = urlparse(self.path).path
            payload = self.read_json()
            if path == "/api/check":
                self.send_json(judge_solution(payload.get("code", ""), payload.get("question_id", "")))
                return
            if path == "/api/mark-revised":
                progress = load_progress()
                problem = find_problem(progress["problems"], payload.get("problem", ""))
                if not problem:
                    raise ValueError("Saved problem not found.")
                count = int(problem.get("revision_count", 0)) + 1
                interval = REVISION_INTERVALS[min(count, len(REVISION_INTERVALS) - 1)]
                problem["revision_count"] = count
                problem["revision_due"] = (date.today() + timedelta(days=interval)).isoformat()
                save_json(PROGRESS_FILE, progress)
                self.send_json({"message": f"Next revision: {problem['revision_due']}", "dashboard": dashboard_data()})
                return
            if path == "/api/upload":
                self.send_json(save_solution(payload))
                return
            if path == "/api/delete-solution":
                self.send_json(delete_solution(payload.get("problem", "")))
                return
            self.send_json({"error": "Endpoint not found."}, HTTPStatus.NOT_FOUND)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        except Exception as error:  # keep browser errors readable for a local tool
            self.send_json({"error": f"Unexpected error: {error}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args) -> None:
        print(f"[DSA manager] {format % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), DSAHandler)
    print("DSA Manager is running at http://127.0.0.1:8000")
    print("Press Ctrl+C to stop it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDSA Manager stopped.")
    finally:
        server.server_close()
