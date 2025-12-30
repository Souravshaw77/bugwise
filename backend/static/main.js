document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "/api";

  const analyzeBtn = document.getElementById("analyzeBtn");
  const loading = document.getElementById("loading");
  const result = document.getElementById("result");
  const errorMsg = document.getElementById("errorMsg");
  const historyEl = document.getElementById("historyList");

  if (!analyzeBtn) {
    console.error("Analyze button not found. JS not wired correctly.");
    return;
  }

  // Restore last analysis
  const cached = localStorage.getItem("lastAnalysis");
  if (cached) {
    try {
      renderResult(JSON.parse(cached));
    } catch {
      localStorage.removeItem("lastAnalysis");
    }
  }

  analyzeBtn.addEventListener("click", async () => {
    errorMsg.classList.add("hidden");

    const bugText = document.getElementById("bugText").value.trim();
    const language = document.getElementById("language").value.trim();

    if (!bugText) {
      errorMsg.textContent = "Bug text is required.";
      errorMsg.classList.remove("hidden");
      return;
    }

    result.classList.add("hidden");
    loading.classList.remove("hidden");

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing…";

    try {
      const response = await fetch(`${API_BASE}/analyze-bug`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bug_text: bugText, language })
      });

      if (!response.ok) throw new Error("API failed");

      const data = await response.json();
      renderResult(data);
      localStorage.setItem("lastAnalysis", JSON.stringify(data));
      loadHistory();

    } catch (err) {
      console.error(err);
      errorMsg.textContent = "Something went wrong. Please try again.";
      errorMsg.classList.remove("hidden");
    } finally {
      loading.classList.add("hidden");
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze Bug";
    }
  });

  function renderResult(data) {
    document.getElementById("explanation").textContent = data.explanation || "";
    document.getElementById("rootCause").textContent = data.root_cause || "";

    const fixSteps = document.getElementById("fixSteps");
    fixSteps.innerHTML = "";
    (data.fix_steps || []).forEach(step => {
      const li = document.createElement("li");
      li.textContent = step;
      fixSteps.appendChild(li);
    });

    document.getElementById("exampleCode").textContent =
      data.example_code || "";

    result.classList.remove("hidden");
  }

  async function loadHistory() {
    try {
      const res = await fetch(`${API_BASE}/bugs`);
      const bugs = await res.json();

      historyEl.innerHTML = "";

      if (!bugs.length) {
        historyEl.innerHTML = `<li class="text-gray-500 italic">No bugs yet.</li>`;
        return;
      }

      bugs.forEach(bug => {
        const li = document.createElement("li");
        li.className = "cursor-pointer border-b pb-2 hover:text-blue-600";
        li.textContent = `${bug.language || "Unknown"} – ${bug.bug_text.slice(0, 80)}…`;

        li.onclick = () => {
          renderResult(bug);
          localStorage.setItem("lastAnalysis", JSON.stringify(bug));
        };

        historyEl.appendChild(li);
      });
    } catch (err) {
      console.error("History load failed", err);
    }
  }

  loadHistory();
});
