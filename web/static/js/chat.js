const synth = window.speechSynthesis;
const btnDictar = document.getElementById('btnDictar');
const btnSilenciar = document.getElementById('btnSilenciarVoz');
const inputPregunta = document.getElementById('inputPregunta');
const form = document.getElementById('formBusqueda');
const chatWindow = document.getElementById('chat-window');
const listaFuentes = document.getElementById('fuentes');
const listaConversaciones = document.getElementById('lista-preguntas');

let chatHistory = [];
let currentChatId = null;
let recognition;
let isListening = false;
let manualStop = false;
let targetChatId = null;

const contextMenu = document.getElementById('context-menu');
const deleteOption = document.getElementById('ctx-delete');

document.addEventListener('click', (e) => {
    if (contextMenu.style.display === 'block') {
        contextMenu.style.display = 'none';
    }
});

deleteOption.addEventListener('click', async () => {
    if (targetChatId) {
        await deleteChat(targetChatId);
        contextMenu.style.display = 'none';
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    await cargarListaChats();
});

async function cargarListaChats() {
    try {
        const resp = await fetch('/api/chats');
        const chats = await resp.json();
        listaConversaciones.innerHTML = "";
        chats.reverse().forEach(chat => {
            const item = document.createElement('div');
            item.className = 'pregunta-item';
            item.textContent = chat.title;
            item.onclick = () => cargarChat(chat.id);
            item.oncontextmenu = (e) => {
                e.preventDefault();
                showContextMenu(e, chat.id);
            };
            listaConversaciones.appendChild(item);
        });
    } catch (e) {
        console.error("Error al cargar lista de chats");
    }
}

async function nuevoChat() {
    try {
        const resp = await fetch('/api/chats', { method: 'POST' });
        const chat = await resp.json();
        currentChatId = chat.id;
        chatHistory = [];
        chatWindow.innerHTML = "";
        listaFuentes.innerHTML = "";
        await cargarListaChats();
    } catch (e) {
        console.error("Error al crear nuevo chat");
    }
}

async function cargarChat(id) {
    try {
        const resp = await fetch(`/api/chats/${id}`);
        const chat = await resp.json();
        currentChatId = id;
        chatWindow.innerHTML = "";
        chatHistory = chat.messages || [];
        chatHistory.forEach(m => {
            appendMessage(m.role === 'model' ? 'assistant' : 'user', m.content);
        });
    } catch (e) {
        console.error("Error al cargar chat");
    }
}

function showContextMenu(e, chatId) {
    targetChatId = chatId;
    contextMenu.style.display = 'block';
    contextMenu.style.left = `${e.pageX}px`;
    contextMenu.style.top = `${e.pageY}px`;
}

async function deleteChat(chatId) {
    if (!confirm("¿Seguro que deseas eliminar este chat?")) return;
    try {
        await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
        if (currentChatId === chatId) {
            currentChatId = null;
            chatWindow.innerHTML = "";
            chatHistory = [];
        }
        await cargarListaChats();
    } catch (e) {
        console.error("Error al eliminar chat");
    }
}

function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    if (role === 'user') {
        msgDiv.textContent = text;
    } else {
        msgDiv.innerHTML = marked.parse(text);
    }
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function guardarMensajeEnServidor(role, content) {
    if (!currentChatId) return;
    try {
        await fetch(`/api/chats/${currentChatId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role, content })
        });
    } catch (e) {
        console.error("Error al guardar mensaje");
    }
}

async function actualizarApuntes() {
    if (!confirm("¿Actualizar base de datos?")) return;
    try {
        const resp = await fetch('/admin/unify', { method: 'POST' });
        const data = await resp.json();
        alert(data.message);
    } catch (e) {
        alert("Error: " + e.message);
    }
}

function limpiarChat() {
    nuevoChat();
}

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
        isListening = true;
        manualStop = false;
        btnDictar.textContent = "🛑";
        btnDictar.style.backgroundColor = "#ff4d4d";
    };

    recognition.onresult = (event) => {
        let currentText = '';
        for (let i = 0; i < event.results.length; ++i) {
            currentText += event.results[i][0].transcript;
        }
        inputPregunta.value = currentText;
    };

    recognition.onend = () => {
        if (isListening && !manualStop) {
            recognition.start();
        } else {
            btnDictar.textContent = "🎤";
            btnDictar.style.backgroundColor = "";
        }
    };

    btnDictar.onclick = () => {
        if (isListening) {
            manualStop = true;
            isListening = false;
            recognition.stop();
            if (inputPregunta.value.trim() !== "") form.dispatchEvent(new Event('submit'));
        } else {
            synth.cancel();
            inputPregunta.value = "";
            recognition.start();
        }
    };
}

function hablar(texto) {
    const cleanText = texto.replace(/[#*`]/g, '').replace(/\[.*?\]/g, '').replace(/```[\s\S]*?```/g, 'código');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'es-ES';
    utterance.onstart = () => btnSilenciar.style.display = 'block';
    utterance.onend = () => btnSilenciar.style.display = 'none';
    synth.speak(utterance);
}

btnSilenciar.onclick = () => {
    synth.cancel();
    btnSilenciar.style.display = 'none';
};

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const pregunta = inputPregunta.value.trim();
    if (!pregunta) return;

    if (!currentChatId) await nuevoChat();

    appendMessage('user', pregunta);
    inputPregunta.value = "";
    synth.cancel();

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: pregunta, history: chatHistory })
        });

        const data = await response.json();
        if (response.ok) {
            appendMessage('assistant', data.answer);
            listaFuentes.innerHTML = data.sources.map(f => `<li>${f}</li>`).join('');

            await guardarMensajeEnServidor('user', pregunta);
            await guardarMensajeEnServidor('model', data.answer);

            chatHistory.push({ role: "user", content: pregunta });
            chatHistory.push({ role: "model", content: data.answer });

            hablar(data.answer);
            if (chatHistory.length <= 2) await cargarListaChats();
        }
    } catch (error) {
        appendMessage('assistant', "Error de conexión.");
    }
});