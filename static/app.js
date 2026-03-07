const serverInput = document.querySelector("#server");
const tokenInput = document.querySelector("#token");
const connectBtn = document.querySelector("#connect");
const commandsEl = document.querySelector("#commands");
const resultEl = document.querySelector("#result");

function setResult(obj) {
  resultEl.textContent = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
}

function authHeader() {
  return { Authorization: `Bearer ${tokenInput.value.trim()}` };
}

function baseUrl() {
  const raw = serverInput.value.trim();
  return raw.endsWith("/") ? raw.slice(0, -1) : raw;
}

function saveState() {
  localStorage.setItem("remote_server", serverInput.value.trim());
  localStorage.setItem("remote_token", tokenInput.value.trim());
}

function restoreState() {
  const savedServer = localStorage.getItem("remote_server");
  if (savedServer) {
    serverInput.value = savedServer;
  } else if (location.origin.startsWith("http")) {
    serverInput.value = location.origin;
  } else {
    serverInput.value = "http://ubuntu.local:8000";
  }
  tokenInput.value = localStorage.getItem("remote_token") || "";
}

async function runCommand(commandId) {
  saveState();
  try {
    const response = await fetch(`${baseUrl()}/api/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeader() },
      body: JSON.stringify({ command_id: commandId }),
    });
    const data = await response.json();
    setResult(data);
  } catch (error) {
    setResult(`Fel vid kommandokorning: ${error}`);
  }
}

function renderCommands(commands) {
  commandsEl.innerHTML = "";
  commands.forEach((cmd) => {
    const button = document.createElement("button");
    button.className = "cmd-btn";
    if (cmd.id.includes("reboot") || cmd.id.includes("shutdown")) {
      button.classList.add("cmd-danger");
    }
    button.textContent = cmd.title;
    button.addEventListener("click", () => runCommand(cmd.id));
    commandsEl.appendChild(button);
  });
}

async function connect() {
  saveState();
  try {
    const response = await fetch(`${baseUrl()}/api/commands`, {
      headers: authHeader(),
    });
    const data = await response.json();
    if (!response.ok) {
      setResult(data);
      return;
    }
    renderCommands(data.commands);
    setResult(`Laddade ${data.commands.length} knappar`);
  } catch (error) {
    setResult(`Kunde inte ansluta: ${error}`);
  }
}

connectBtn.addEventListener("click", connect);
restoreState();
if (serverInput.value.trim() && tokenInput.value.trim()) {
  connect();
}
