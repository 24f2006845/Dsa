const state = { dashboard: null, questions: [], selected: null, selectedSavedProblem: null };
const $ = (selector) => document.querySelector(selector);

async function request(url, options = {}) {
  const response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, char => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", "'":"&#39;", '"':"&quot;" })[char]);
}

function relativeDue(days) {
  if (days < 0) return `overdue by ${-days} day${days === -1 ? "" : "s"}`;
  if (days === 0) return "due today";
  return `due in ${days} day${days === 1 ? "" : "s"}`;
}

function renderDashboard() {
  const { dashboard } = state;
  $("#solvedCount").textContent = dashboard.total_solved;
  $("#dueCount").textContent = dashboard.due_today;
  $("#topicCount").textContent = dashboard.topics;
  const list = $("#revisionList"); list.innerHTML = "";
  dashboard.problems.forEach(problem => {
    const node = $("#revisionTemplate").content.firstElementChild.cloneNode(true);
    node.querySelector(".tag").textContent = `${problem.topic} · ${problem.difficulty}`;
    node.querySelector("h3").textContent = problem.problem;
    node.querySelector("p").textContent = `${relativeDue(problem.days_until_revision)}${problem.practice_question ? " · prompt ready" : " · add its prompt"}`;
    const button = node.querySelector("button"); button.disabled = !problem.practice_question;
    button.textContent = problem.practice_question ? "Practice" : "No prompt yet";
    button.addEventListener("click", () => selectQuestion(problem.practice_question, problem.problem));
    list.append(node);
  });
}

function renderQuestions() {
  const term = $("#questionFilter").value.toLowerCase().trim();
  const list = $("#questionList"); list.innerHTML = "";
  state.questions.filter(q => `${q.title} ${q.topic} ${q.difficulty}`.toLowerCase().includes(term)).forEach(question => {
    const button = document.createElement("button"); button.className = "question-button";
    button.innerHTML = `<strong>${escapeHtml(question.title)}</strong><span>${escapeHtml(question.topic)} · ${escapeHtml(question.difficulty)}</span>`;
    button.addEventListener("click", () => selectQuestion(question)); list.append(button);
  });
}

function starterCode(question) {
  if (question.runner === "class_method") return `class Solution:\n    def ${question.method}(self, *args):\n        # Replace *args with clear parameter names, then write your solution.\n        pass\n`;
  return "# Read input, solve the problem, and print the answer.\n";
}

function selectQuestion(question, savedProblem = null) {
  state.selected = question; state.selectedSavedProblem = savedProblem;
  $("#practiceArea").classList.remove("hidden");
  $("#problemMeta").textContent = `${question.topic.toUpperCase()} · ${question.difficulty.toUpperCase()}`;
  $("#problemTitle").textContent = question.title;
  $("#problemPrompt").textContent = question.prompt;
  $("#problemConstraints").textContent = question.constraints;
  $("#edgeCases").innerHTML = question.edge_cases.map(item => `<li>${escapeHtml(item)}</li>`).join("");
  $("#sampleTests").innerHTML = question.tests.slice(0, 3).map(test => {
    const input = test.args ?? test.input ?? ""; return `<div>input: ${escapeHtml(JSON.stringify(input))} → expected: ${escapeHtml(JSON.stringify(test.expected))}</div>`;
  }).join("");
  $("#solutionHint").textContent = question.runner === "class_method" ? `Create class Solution with method ${question.method}(...)` : "Read standard input and print only the final answer.";
  $("#codeEditor").value = localStorage.getItem(`dsa-draft:${question.id}`) || starterCode(question); $("#testResults").className = "test-results muted"; $("#testResults").textContent = "Your test results will appear here.";
  $("#markRevised").classList.toggle("hidden", !savedProblem);
  $("#practiceArea").scrollIntoView({ behavior: "smooth", block: "start" });
}

async function runTests() {
  const results = $("#testResults"); results.className = "test-results muted"; results.textContent = "Running tests…";
  try {
    const data = await request("/api/check", { method: "POST", body: JSON.stringify({ question_id: state.selected.id, code: $("#codeEditor").value }) });
    results.className = "test-results";
    results.innerHTML = `<strong class="${data.passed === data.total ? "result-pass" : "result-fail"}">${data.passed}/${data.total} tests passed</strong>` + data.results.map(item => `<div class="result-line ${item.passed ? "result-pass" : "result-fail"}">${item.passed ? "PASS" : "FAIL"} ${item.number} — expected ${escapeHtml(JSON.stringify(item.expected))}, got ${escapeHtml(JSON.stringify(item.actual))}</div>`).join("");
  } catch (error) { results.className = "test-results result-fail"; results.textContent = error.message; }
}

async function markRevised() {
  try {
    const data = await request("/api/mark-revised", { method: "POST", body: JSON.stringify({ problem: state.selectedSavedProblem }) });
    state.dashboard = data.dashboard; renderDashboard(); alert(`Saved. ${data.message}`);
  } catch (error) { alert(error.message); }
}

async function initialise() {
  try {
    const [dashboard, questionData] = await Promise.all([request("/api/dashboard"), request("/api/questions")]);
    state.dashboard = dashboard; state.questions = questionData.questions; renderDashboard(); renderQuestions();
  } catch (error) { $("#revisionList").innerHTML = `<p class="result-fail">Could not load your DSA data: ${escapeHtml(error.message)}</p>`; }
}

$("#refreshButton").addEventListener("click", initialise);
$("#questionFilter").addEventListener("input", renderQuestions);
$("#runTests").addEventListener("click", runTests);
$("#markRevised").addEventListener("click", markRevised);
$("#closePractice").addEventListener("click", () => $("#practiceArea").classList.add("hidden"));
$("#codeEditor").addEventListener("input", event => {
  if (state.selected) localStorage.setItem(`dsa-draft:${state.selected.id}`, event.target.value);
});
initialise();
