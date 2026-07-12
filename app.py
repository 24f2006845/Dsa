#!/usr/bin/env python3
"""Local web interface for the DSA manager.

Run `python3 app.py`, then open http://127.0.0.1:8000 in a browser.
"""

from __future__ import annotations

import json
import tempfile
from datetime import date, timedelta
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dsa_manager import (
    PROGRESS_FILE,
    QUESTION_FILE,
    REVISION_INTERVALS,
    find_problem,
    load_progress,
    load_questions,
    question_matches_problem,
    run_class_method,
    run_script,
    save_json,
)


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"


def question_for_problem(problem_name: str, questions: list[dict]) -> dict | None:
    return next((question for question in questions if question_matches_problem(question, problem_name)), None)


def dashboard_data() -> dict:
    progress = load_progress()
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
