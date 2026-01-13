let mode = "login";

// Toggle login / register
function toggleMode() {
    mode = mode === "login" ? "register" : "login";
    document.getElementById("authTitle").innerText =
        mode === "login" ? "Login" : "Register";
    document.getElementById("toggle").innerText =
        mode === "login"
            ? "Don't have an account? Sign up"
            : "Already have an account? Login";
}

// Submit auth
async function submitAuth() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    document.getElementById("authError").innerText = "";

    let res;

    if (mode === "login") {
        // 🔴 LOGIN → FORM DATA (REQUIRED)
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);

        res = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData.toString()
        });

    } else {
        // 🟢 REGISTER → JSON
        res = await fetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
    }

    if (!res.ok) {
        document.getElementById("authError").innerText =
            "Authentication failed";
        return;
    }

    const data = await res.json();

    // Login returns token, register may not
    if (data.access_token) {
        localStorage.setItem("token", data.access_token);
    }

    document.getElementById("auth").style.display = "none";
    document.getElementById("userLabel").innerText = username;
    document.getElementById("logoutBtn").hidden = false;
}

// Logout
document.getElementById("logoutBtn").onclick = () => {
    localStorage.removeItem("token");
    location.reload();
};

// Generate password
async function generate() {
    const hint = document.getElementById("hint").value;
    const token = localStorage.getItem("token");

    const res = await fetch("/ai/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ hint })
    });

    if (!res.ok) {
        document.getElementById("output").innerText =
            "Generation failed";
        return;
    }

    const data = await res.json();
    document.getElementById("output").innerText = data.password;
}








