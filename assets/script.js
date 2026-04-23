// Elementos DOM
const chatContainer = document.getElementById('chat-container');
const mensagemInput = document.getElementById('mensagem-input');
const enviarBtn = document.getElementById('enviar-btn');
const typingIndicator = document.getElementById('typingIndicator');
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const newChatBtn = document.getElementById('newChatBtn');
const clearChatBtn = document.getElementById('clearChatBtn');
const exportChatBtn = document.getElementById('exportChatBtn');

// Estado da aplicação
let currentConversationId = Date.now().toString();
let conversations = JSON.parse(localStorage.getItem('finance_chat_conversations') || '{}');
let currentMessages = [];
let isTyping = false;
let currentTypingInterval = null;

// Configurações do efeito de digitação
const TYPING_SPEED = 20;

// Inicialização
function init() {
    loadConversationsFromStorage();
    renderChatHistory();
    
    const lastConversation = localStorage.getItem('last_conversation');
    if (lastConversation && conversations[lastConversation]) {
        currentConversationId = lastConversation;
        currentMessages = conversations[currentConversationId];
        renderMessages();
    } else {
        showWelcomeMessage();
    }
    
    setupEventListeners();
    autoResizeTextarea();
}

// Setup Event Listeners
function setupEventListeners() {
    enviarBtn.addEventListener('click', processarEnvio);
    
    mensagemInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            processarEnvio();
        }
    });
    
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
    
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        }
    });
    
    newChatBtn.addEventListener('click', createNewChat);
    clearChatBtn.addEventListener('click', clearAllMessages);
    exportChatBtn.addEventListener('click', exportConversation);
}

// Auto-resize textarea
function autoResizeTextarea() {
    mensagemInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

// Efeito de digitação
async function typeMessage(contentElement, fullText, onComplete) {
    if (isTyping) {
        if (currentTypingInterval) clearTimeout(currentTypingInterval);
        isTyping = false;
    }
    
    isTyping = true;
    let index = 0;
    contentElement.innerHTML = '';
    
    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    contentElement.appendChild(cursor);
    
    function typeNext() {
        if (index < fullText.length) {
            const char = fullText[index];
            cursor.remove();
            contentElement.innerHTML += char;
            contentElement.appendChild(cursor);
            index++;
            chatContainer.scrollTop = chatContainer.scrollHeight;
            currentTypingInterval = setTimeout(typeNext, TYPING_SPEED);
        } else {
            cursor.remove();
            contentElement.innerHTML = marked.parse(fullText);
            isTyping = false;
            currentTypingInterval = null;
            if (onComplete) onComplete();
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    typeNext();
}

// Adicionar mensagem com efeito
function adicionarMensagemComEfeito(texto, tipo, isStreaming = true) {
    return new Promise((resolve) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${tipo}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = tipo === 'ai' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        if (tipo === 'user') {
            content.textContent = texto;
            resolve(messageDiv);
        } else if (isStreaming && texto && texto.length > 0) {
            typeMessage(content, texto, () => resolve(messageDiv));
        } else {
            content.innerHTML = marked.parse(texto);
            resolve(messageDiv);
        }
    });
}

// Adicionar mensagem sem efeito (para histórico)
function adicionarMensagemSemEfeito(texto, tipo) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${tipo}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = tipo === 'ai' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    if (tipo === 'ai') {
        content.innerHTML = marked.parse(texto);
    } else {
        content.textContent = texto;
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Mostrar welcome message
function showWelcomeMessage() {
    chatContainer.innerHTML = `
        <div class="welcome-message">
            <div class="welcome-icon">
                <i class="fas fa-calculator"></i>
            </div>
            <h2>Bem-vindo ao FinançaAI</h2>
            <p>O seu assistente especializado em contabilidade municipal e SNC-AP</p>
            <div class="suggestions">
                <button class="suggestion-btn" data-question="Como registar uma despesa municipal?">
                    <i class="fas fa-receipt"></i>
                    Como registar uma despesa municipal?
                </button>
                <button class="suggestion-btn" data-question="Explique o plano de contas SNC-AP">
                    <i class="fas fa-chart-pie"></i>
                    Explique o plano de contas SNC-AP
                </button>
                <button class="suggestion-btn" data-question="O que é o controlo interno na administração local?">
                    <i class="fas fa-shield-alt"></i>
                    O que é o controlo interno?
                </button>
            </div>
        </div>
    `;
    
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.getAttribute('data-question');
            mensagemInput.value = question;
            processarEnvio();
        });
    });
}

// Mostrar/esconder typing indicator
function setTypingIndicator(visible) {
    if (visible) {
        typingIndicator.classList.add('visible');
    } else {
        typingIndicator.classList.remove('visible');
    }
}

// Processar envio
async function processarEnvio() {
    const texto = mensagemInput.value.trim();
    if (texto === "" || isTyping) return;
    
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) welcomeMsg.remove();
    
    await adicionarMensagemComEfeito(texto, 'user', false);
    currentMessages.push({ role: 'user', content: texto, timestamp: Date.now() });
    
    mensagemInput.value = '';
    mensagemInput.style.height = 'auto';
    autoResizeTextarea();
    
    setTypingIndicator(true);
    
    try {
        const resposta = await fetch('http://127.0.0.1:5000/perguntar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pergunta: texto })
        });
        
        const dados = await resposta.json();
        setTypingIndicator(false);
        
        if (dados.resposta) {
            await adicionarMensagemComEfeito(dados.resposta, 'ai', true);
            currentMessages.push({ role: 'assistant', content: dados.resposta, timestamp: Date.now() });
        } else {
            const errorMsg = dados.erro || "Erro ao processar a solicitação";
            await adicionarMensagemComEfeito(`❌ ${errorMsg}`, 'ai', true);
            currentMessages.push({ role: 'assistant', content: errorMsg, timestamp: Date.now() });
        }
        
        saveCurrentConversation();
        
    } catch (erro) {
        console.error('Erro:', erro);
        setTypingIndicator(false);
        const errorMessage = "❌ Erro de ligação ao servidor. Verifique se o servidor está ativo em http://127.0.0.1:5000";
        await adicionarMensagemComEfeito(errorMessage, 'ai', true);
        currentMessages.push({ role: 'assistant', content: errorMessage, timestamp: Date.now() });
    }
}

// Salvar conversa
function saveCurrentConversation() {
    if (currentMessages.length > 0) {
        conversations[currentConversationId] = currentMessages;
        localStorage.setItem('finance_chat_conversations', JSON.stringify(conversations));
        localStorage.setItem('last_conversation', currentConversationId);
        renderChatHistory();
    }
}

// Carregar conversas
function loadConversationsFromStorage() {
    const stored = localStorage.getItem('finance_chat_conversations');
    if (stored) {
        conversations = JSON.parse(stored);
    }
}

// Renderizar histórico
function renderChatHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;
    
    historyList.innerHTML = '';
    const sorted = Object.entries(conversations).sort((a, b) => {
        const aTime = a.value[a.value.length - 1]?.timestamp || 0;
        const bTime = b.value[b.value.length - 1]?.timestamp || 0;
        return bTime - aTime;
    });
    
    sorted.slice(0, 20).forEach(([id, messages]) => {
        if (messages.length === 0) return;
        
        const firstMessage = messages.find(m => m.role === 'user');
        let preview = firstMessage ? firstMessage.content.substring(0, 30) : 'Nova conversa';
        if (firstMessage && firstMessage.content.length > 30) preview += '...';
        
        const item = document.createElement('div');
        item.className = `history-item ${id === currentConversationId ? 'active' : ''}`;
        item.innerHTML = `<i class="fas fa-comment"></i><span>${escapeHtml(preview)}</span>`;
        item.addEventListener('click', () => loadConversation(id));
        historyList.appendChild(item);
    });
    
    if (sorted.length === 0) {
        historyList.innerHTML = '<div style="color: #64748B; text-align: center; padding: 20px;">Nenhuma conversa</div>';
    }
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Carregar conversa
function loadConversation(id) {
    if (conversations[id]) {
        if (currentTypingInterval) {
            clearTimeout(currentTypingInterval);
            isTyping = false;
        }
        currentConversationId = id;
        currentMessages = conversations[id];
        renderMessages();
        localStorage.setItem('last_conversation', id);
        renderChatHistory();
        if (window.innerWidth <= 768) sidebar.classList.remove('open');
    }
}

// Renderizar mensagens
function renderMessages() {
    chatContainer.innerHTML = '';
    if (currentMessages.length === 0) {
        showWelcomeMessage();
        return;
    }
    
    currentMessages.forEach(msg => {
        adicionarMensagemSemEfeito(msg.content, msg.role === 'user' ? 'user' : 'ai');
    });
}

// Criar nova conversa
function createNewChat() {
    if (currentTypingInterval) {
        clearTimeout(currentTypingInterval);
        isTyping = false;
    }
    currentConversationId = Date.now().toString();
    currentMessages = [];
    showWelcomeMessage();
    localStorage.setItem('last_conversation', currentConversationId);
    renderChatHistory();
    if (window.innerWidth <= 768) sidebar.classList.remove('open');
}

// Limpar conversa atual
function clearAllMessages() {
    if (confirm('Tem certeza que deseja limpar todas as mensagens desta conversa?')) {
        if (currentTypingInterval) {
            clearTimeout(currentTypingInterval);
            isTyping = false;
        }
        currentMessages = [];
        showWelcomeMessage();
        saveCurrentConversation();
        renderChatHistory();
    }
}

// Exportar conversa
function exportConversation() {
    if (currentMessages.length === 0) {
        alert('Não há mensagens para exportar.');
        return;
    }
    
    let exportText = `FinançaAI - Conversa de Contabilidade Municipal\n`;
    exportText += `Data: ${new Date().toLocaleString('pt-PT')}\n`;
    exportText += `${'='.repeat(60)}\n\n`;
    
    currentMessages.forEach(msg => {
        const role = msg.role === 'user' ? 'UTILIZADOR' : 'FINANÇAAI';
        exportText += `[${role}]\n${msg.content}\n\n`;
        exportText += `${'-'.repeat(40)}\n\n`;
    });
    
    const blob = new Blob([exportText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversa_financai_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

init();