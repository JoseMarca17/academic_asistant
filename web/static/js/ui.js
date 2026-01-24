document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const btnToggle = document.getElementById('btnToggleSidebar');
    const btnSettings = document.getElementById('btnSettings');
    const settingsPanel = document.getElementById('settings-panel');
    const ctxMenu = document.getElementById('context-menu');

    if (btnToggle) {
        btnToggle.onclick = () => {
            sidebar.classList.toggle('collapsed');
        };
    }

    if (btnSettings) {
        btnSettings.onclick = (e) => {
            e.stopPropagation();
            settingsPanel.classList.toggle('hidden');
        };
    }

    document.addEventListener('click', (e) => {
        if (settingsPanel && !settingsPanel.contains(e.target)) {
            settingsPanel.classList.add('hidden');
        }
        if (ctxMenu) {
            ctxMenu.classList.add('hidden');
        }
    });
});

function showContextMenu(e, chatId) {
    e.preventDefault();
    targetChatId = chatId;
    const ctxMenu = document.getElementById('context-menu');
    if (ctxMenu) {
        ctxMenu.classList.remove('hidden');
        ctxMenu.style.left = `${e.pageX}px`;
        ctxMenu.style.top = `${e.pageY}px`;
    }
}