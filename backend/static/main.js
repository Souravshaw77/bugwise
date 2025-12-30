document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "http://127.0.0.1:5000/api";

  const analyzeBtn = document.getElementById("analyzeBtn");
  const loading = document.getElementById("loading");
  const result = document.getElementById("result");
  const errorMsg = document.getElementById("errorMsg");
  const historyEl = document.getElementById("historyList");

  // Restore last analysis (page refresh safety)
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
    analyzeBtn.classList.add("opacity-50", "cursor-not-allowed");

    try {
      const response = await fetch(`${API_BASE}/analyze-bug`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bug_text: bugText,
          language: language || null
        })
      });

      if (!response.ok) {
        throw new Error("API request failed");
      }

      const data = await response.json();

      renderResult(data);
      localStorage.setItem("lastAnalysis", JSON.stringify(data));
      await loadHistory();

    } catch (err) {
      console.error(err);
      errorMsg.textContent = "Something went wrong. Please try again.";
      errorMsg.classList.remove("hidden");

    } finally {
      loading.classList.add("hidden");
      analyzeBtn.disabled = false;
      analyzeBtn.textContent = "Analyze Bug";
      analyzeBtn.classList.remove("opacity-50", "cursor-not-allowed");
    }
  });

  // -----------------------------
  // Render AI result
  // -----------------------------
  function renderResult(data) {
    document.getElementById("explanation").textContent =
      data.explanation || "";

    document.getElementById("rootCause").textContent =
      data.root_cause || "";

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

  // -----------------------------
  // Load history from backend
  // -----------------------------
  async function loadHistory() {
    try {
      const res = await fetch(`${API_BASE}/bugs`);
      const bugs = await res.json();

      historyEl.innerHTML = "";

      if (!bugs.length) {
        const li = document.createElement("li");
        li.className = "text-gray-500 italic";
        li.textContent = "No bugs analyzed yet.";
        historyEl.appendChild(li);
        return;
      }

      bugs.forEach(bug => {
        const li = document.createElement("li");
        li.className =
          "cursor-pointer border-b pb-2 hover:text-blue-600";

        li.textContent =
          `${bug.language || "Unknown"} – ${bug.bug_text.slice(0, 80)}…`;

        li.addEventListener("click", () => {
          const analysis = {
            explanation: bug.explanation,
            root_cause: bug.root_cause,
            fix_steps: bug.fix_steps || [],
            example_code: bug.example_code
          };

          renderResult(analysis);
          localStorage.setItem("lastAnalysis", JSON.stringify(analysis));
        });

        historyEl.appendChild(li);
      });

    } catch (err) {
      console.error("Failed to load history", err);
    }
  }

  loadHistory();
});
