const $ = selector => document.querySelector(selector);
const interview = { questions: [], queue: [], index: 0, seconds: 2700, timer: null, feedback: [], startedAt: null };

async function request(url, options = {}) {
  const response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}
function esc(value) { return String(value ?? "").replace(/[&<>'"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[c]); }
function starter(question) { return question.runner === "class_method" ? `class Solution:\n    def ${question.method}(self, *args):\n        # Explain your choices as you code.\n        pass\n` : "# Read input, solve the problem, and print the answer.\n"; }
function formatTime(total) { return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`; }
function setMessage(message) { $("#interviewerMessage").textContent = message; }
function setStage(stage) { document.querySelectorAll(".interview-steps div").forEach((node, i) => node.classList.toggle("active", i === stage)); }

function renderQuestion() {
  const question = interview.queue[interview.index];
  $("#questionPill").textContent = `${question.topic} · ${question.difficulty}`;
  $("#questionCounter").textContent = `Question ${interview.index + 1} of ${interview.queue.length}`;
  $("#interviewTitle").textContent = question.title;
  $("#interviewPrompt").textContent = question.prompt;
  $("#interviewConstraints").textContent = question.constraints || "Clarify the input limits before choosing an approach.";
  $("#interviewEdges").innerHTML = (question.edge_cases || []).map(item => `<li>${esc(item)}</li>`).join("");
  const examples = question.examples || (question.tests || []).slice(0, 2).map((test, i) => ({ label: `Example ${i + 1}`, input: JSON.stringify(test.args ?? test.input ?? ""), output: JSON.stringify(test.expected) }));
  $("#interviewExamples").innerHTML = examples.length ? examples.map((example, i) => `<article class="example-card"><h4>${esc(example.label || `Example ${i + 1}`)}</h4><div><strong>Input</strong><code>${esc(example.input)}</code></div><div><strong>Output</strong><code>${esc(example.output)}</code></div></article>`).join("") : "";
  $("#approachEditor").value = ""; $("#interviewCode").value = starter(question); $("#codingSection").classList.add("hidden"); $("#interviewResults").className = "test-results muted"; $("#interviewResults").textContent = "Run the tests when you are ready."; $("#nextQuestion").classList.add("hidden");
  setStage(0); setMessage(`Thanks for joining. Take a moment to read “${question.title}.” What questions would you ask to clarify the problem?`);
}
function tick() { interview.seconds -= 1; $("#timer").textContent = formatTime(Math.max(interview.seconds, 0)); if (interview.seconds <= 0) finishInterview(true); }

function startInterview(event) {
  event.preventDefault();
  const topic = $("#interviewTopic").value, difficulty = $("#interviewDifficulty").value;
  const pool = interview.questions.filter(q => (!topic || q.topic === topic) && (!difficulty || q.difficulty === difficulty));
  if (!pool.length) { $("#lobbyMessage").textContent = "No saved interview questions match that focus. Try another filter or add a prompt on the dashboard."; return; }
  interview.queue = [...pool].sort(() => Math.random() - 0.5).slice(0, Math.min(2, pool.length)); interview.index = 0; interview.feedback = []; interview.seconds = Number($("#interviewLength").value) * 60; interview.startedAt = Date.now();
  $("#timer").textContent = formatTime(interview.seconds); $("#interviewLobby").classList.add("hidden"); $("#interviewRoom").classList.remove("hidden"); clearInterval(interview.timer); interview.timer = setInterval(tick, 1000); renderQuestion();
}
function shareApproach() { const text = $("#approachEditor").value.trim(); if (!text) { setMessage("Before we code, please talk me through your proposed solution and its time complexity."); return; } $("#codingSection").classList.remove("hidden"); setStage(2); setMessage("Good. Now implement it carefully. Narrate any important decisions, and test edge cases when you’re ready."); $("#codingSection").scrollIntoView({ behavior: "smooth", block: "start" }); }
function askHint() { const q = interview.queue[interview.index]; const hint = q.edge_cases?.[0] || "Start by stating the brute-force approach, then look for repeated work or a useful data structure."; setMessage(`Here’s one small nudge: consider ${hint.toLowerCase()}. What does that suggest about your approach?`); }
async function runTests() { const q = interview.queue[interview.index], box = $("#interviewResults"); box.className = "test-results muted"; box.textContent = "Interviewer is checking your solution…"; try { const data = await request("/api/check", { method: "POST", body: JSON.stringify({ question_id: q.id, code: $("#interviewCode").value }) }); const perfect = data.passed === data.total; box.className = "test-results"; box.innerHTML = `<strong class="${perfect ? "result-pass" : "result-fail"}">${data.passed}/${data.total} tests passed</strong>` + data.results.map(r => `<div class="result-line ${r.passed ? "result-pass" : "result-fail"}">${r.passed ? "PASS" : "FAIL"} ${r.number} — expected ${esc(JSON.stringify(r.expected))}, got ${esc(JSON.stringify(r.actual))}</div>`).join(""); interview.feedback[interview.index] = { title: q.title, passed: data.passed, total: data.total, approach: $("#approachEditor").value.trim() }; setStage(3); setMessage(perfect ? "Nice work — all tests pass. Briefly explain the time and space complexity, then we’ll move on." : "Some cases still fail. Trace through one failing input aloud and look for the assumption that breaks."); if (perfect && interview.index < interview.queue.length - 1) $("#nextQuestion").classList.remove("hidden"); } catch (error) { box.className = "test-results result-fail"; box.textContent = error.message; } }
function nextQuestion() { interview.index += 1; renderQuestion(); window.scrollTo({ top: 0, behavior: "smooth" }); }
function finishInterview(timedOut = false) { if (!interview.queue.length) return; clearInterval(interview.timer); $("#codingSection").classList.add("hidden"); const completed = interview.feedback.filter(Boolean), passed = completed.reduce((sum, item) => sum + item.passed, 0), total = completed.reduce((sum, item) => sum + item.total, 0); $("#interviewSummary").classList.remove("hidden"); $("#interviewSummary").innerHTML = `<p class="eyebrow">INTERVIEW COMPLETE</p><h2>${timedOut ? "Time’s up." : "Great session."}</h2><p>You completed ${completed.length} of ${interview.queue.length} question${interview.queue.length === 1 ? "" : "s"}${total ? ` and passed ${passed}/${total} test cases` : ""}.</p><div class="summary-list">${interview.queue.map((q, i) => { const result = interview.feedback[i]; return `<div><strong>${esc(q.title)}</strong><span>${result ? `${result.passed}/${result.total} tests passed` : "Not submitted"}</span></div>`; }).join("")}</div><button class="primary-button" onclick="location.href='index.html'">Return to dashboard</button>`; setStage(3); setMessage("Thanks for interviewing today. Review your solutions in the dashboard, then come back for another round."); $("#interviewSummary").scrollIntoView({ behavior: "smooth", block: "start" }); }
async function init() { try { const data = await request("/api/questions"); interview.questions = data.questions.filter(q => q.prompt && !q.auto_generated); const topics = [...new Set(interview.questions.map(q => q.topic))].sort(); $("#interviewTopic").innerHTML = '<option value="">Any topic</option>' + topics.map(t => `<option value="${esc(t)}">${esc(t)}</option>`).join(""); $("#lobbyMessage").textContent = interview.questions.length ? `${interview.questions.length} prepared question${interview.questions.length === 1 ? "" : "s"} available for your interview.` : "Add detailed question prompts on the dashboard to create interview-ready questions."; } catch (error) { $("#lobbyMessage").className = "result-fail"; $("#lobbyMessage").textContent = `Could not load questions: ${error.message}`; } }
$("#interviewSetup").addEventListener("submit", startInterview); $("#confirmApproach").addEventListener("click", shareApproach); $("#hintButton").addEventListener("click", askHint); $("#runInterviewTests").addEventListener("click", runTests); $("#nextQuestion").addEventListener("click", nextQuestion); $("#finishInterview").addEventListener("click", () => finishInterview()); $("#endInterview").addEventListener("click", () => { if (confirm("End this interview and view your summary?")) finishInterview(); }); init();
