const synth = window.speechSynthesis;
const inputPregunta = document.getElementById('inputPregunta');
const form = document.getElementById('formBusqueda');
const chatWindow = document.getElementById('chat-window');
const listaFuentes = document.getElementById('fuentes');
const listaConversaciones = document.getElementById('lista-preguntas');
const btnDictar = document.getElementById('btnDictar');
const btnSilenciar = document.getElementById('btnSilenciarVoz');
let chatHistory = [];
let currentChatId = null;
let targetChatId = null;

document.addEventListener('DOMContentLoaded', cargarListaChats);

async function cargarListaChats() {
    try {
        const resp = await fetch('/api/chats');
        const chats = await resp.json();
        listaConversaciones.innerHTML = "";
        chats.reverse().forEach(chat => {
            const item = document.createElement('div');
            item.className = 'pregunta-item';
            item.textContent = chat.title || "Nueva conversación";
            item.onclick = () => cargarChat(chat.id);
            item.oncontextmenu = (e) => showContextMenu(e, chat.id);
            listaConversaciones.appendChild(item);
        });
    } catch (e) {
        console.error("Error al cargar chats:", e);
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
        console.error("Error al crear chat:", e);
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
        console.error("Error al cargar chat:", e);
    }
}

async function deleteChat() {
    if (!targetChatId) return;
    if (!confirm("¿Eliminar este chat?")) return;
    try {
        await fetch(`/api/chats/${targetChatId}`, { method: 'DELETE' });
        if (currentChatId === targetChatId) {
            currentChatId = null;
            chatWindow.innerHTML = "";
            chatHistory = [];
        }
        await cargarListaChats();
    } catch (e) {
        console.error("Error al eliminar:", e);
    }
}

document.getElementById('ctx-delete').onclick = deleteChat;

function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    msgDiv.innerHTML = role === 'user' ? text : marked.parse(text);
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

form.onsubmit = async (e) => {
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
            
            chatHistory.push({ role: "user", content: pregunta });
            chatHistory.push({ role: "model", content: data.answer });
            
            hablar(data.answer);
            if (chatHistory.length <= 2) await cargarListaChats();
        }
    } catch (error) {
        appendMessage('assistant', "Error de conexión.");
    }
};

function hablar(texto) {
    const cleanText = texto.replace(/[#*`]/g, '').replace(/```[\s\S]*?```/g, 'código');
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

if ('webkitSpeechRecognition' in window) {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'es-ES';
    btnDictar.onclick = () => {
        synth.cancel();
        recognition.start();
    };
    recognition.onresult = (event) => {
        inputPregunta.value = event.results[0][0].transcript;
        form.dispatchEvent(new Event('submit'));
    };
}