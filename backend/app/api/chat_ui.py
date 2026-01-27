from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/chat", response_class=HTMLResponse)
def chat_ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>PV-Connect Chatbot</title>
    <style>
        body { font-family: Arial; background: #f4f4f4; }
        #chat { width: 400px; margin: auto; background: white; padding: 10px; }
        #messages { height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 5px; }
        input, button { width: 100%; margin-top: 5px; }
    </style>
</head>
<body>
    <div id="chat">
        <h3>PV-Connect Test Bot</h3>
        <div id="messages"></div>
        <input id="text" placeholder="Type message..." />
        <input type="file" id="file" />
        <button onclick="send()">Send</button>
    </div>

<script>
async function send() {
    const text = document.getElementById("text").value;
    const file = document.getElementById("file").files[0];
    const messages = document.getElementById("messages");

    messages.innerHTML += "<div><b>You:</b> " + text + "</div>";

    let formData = new FormData();
    if (text) formData.append("text", text);
    if (file) formData.append("file", file);

    const res = await fetch("/api/chat", {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    messages.innerHTML += "<div><b>Bot:</b> " + data.reply + "</div>";
    document.getElementById("text").value = "";
}
</script>
</body>
</html>
"""
