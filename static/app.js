let token = "";

function addMessage(text, sender = "ai") {
  const chat = document.getElementById("chat");
  const div = document.createElement("div");
  div.className = sender;
  div.innerText = text;
  chat.appendChild(div);
}

async function register() {
  const u = username.value;
  const p = password.value;

  const res = await fetch(`/register?username=${u}&password=${p}`, { method: "POST" });
  alert(await res.text());
}

async function login() {
  const u = username.value;
  const p = password.value;

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: u, password: p })
  });

  const data = await res.json();
  token = data.access_token;

  document.getElementById("auth").classList.add("hidden");
  document.getElementById("chat").classList.remove("hidden");
  document.getElementById("generator").classList.remove("hidden");

  addMessage("Logged in successfully 🔓");
}

async function generate() {
  const hint = document.getElementById("hint").value;
  const platform = document.getElementById("platform").value;

  addMessage("Generating password...", "user");

  const res = await fetch("/ai/generate-and-save", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ hint, platform })
  });

  const data = await res.json();
  addMessage(`🔑 ${data.password}`);
}

  const data = await res.json();

  if (res.ok) {
    addMessage(`Generated Password:\n${data.password}`, "ai");
  } else {
    addMessage(`Error: ${data.detail}`, "ai");
  }

  async function loadVault() {
  const res = await fetch("/vault/", {
    headers: { "Authorization": `Bearer ${token}` }
  });

  const data = await res.json();
  addMessage("📦 Saved Passwords:");

  data.forEach(v => {
    addMessage(`${v.platform}: ${v.password}`);
  });
}

}
