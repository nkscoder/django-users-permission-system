(function () {
  const form = document.getElementById("ups-chat-form");
  const input = document.getElementById("ups-chat-input");
  const log = document.getElementById("ups-chat-log");
  if (!form || !input || !log) return;

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? match[2] : "";
  }

  function appendMessage(text, type) {
    const node = document.createElement("div");
    node.className = "ups-chat-msg ups-chat-msg--" + type;
    node.textContent = text;
    log.appendChild(node);
    log.scrollTop = log.scrollHeight;
  }

  async function ask(question) {
    const q = (question || "").trim();
    if (!q) return;
    appendMessage(q, "user");
    input.value = "";

    const apiUrl = window.UPS_AI_API_URL || "/permissions/api/ai-assistant/";
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ question: q }),
    });
    const data = await response.json();
    appendMessage(data.answer || "No answer available.", "bot");
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    ask(input.value);
  });

  document.querySelectorAll(".ups-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      ask(chip.getAttribute("data-prompt"));
    });
  });
})();
