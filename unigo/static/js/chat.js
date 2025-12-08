const chatInput = document.querySelector('.chat-input');
const sendBtn = document.getElementById('chat-send-btn');
const chatCanvas = document.querySelector('.chat-canvas');

const STORAGE_KEY_HISTORY = 'unigo.app.chatHistory';
const STORAGE_KEY_ONBOARDING = 'unigo.app.onboarding';
const STORAGE_KEY_RESULT_PANEL = 'unigo.app.resultPanel';

const API_CHAT_URL = '/api/chat';
const API_ONBOARDING_URL = '/api/onboarding';

// Onboarding Questions Definition
const ONBOARDING_QUESTIONS = [
    {
        key: "subjects",
        label: "선호 고교 과목",
        prompt: "안녕하세요! 가장 좋아하거나 자신 있는 고등학교 과목은 무엇인가요? 좋아하는 이유도 함께 알려주세요.",
        placeholder: "예: 수학과 물리를 특히 좋아하고 실험 수업을 즐깁니다."
    },
    {
        key: "interests",
        label: "흥미 및 취미",
        prompt: "학교 밖에서는 어떤 주제나 취미에 가장 흥미를 느끼나요?",
        placeholder: "예: 로봇 동아리 활동, 디지털 드로잉, 음악 감상 등"
    },
    {
        key: "desired_salary",
        label: "희망 연봉",
        prompt: "졸업 후 어느 정도의 연봉을 희망하나요? 대략적인 수준을 알려주세요.",
        placeholder: "예: 연 4천만 원 이상이면 좋겠습니다."
    },
    {
        key: "preferred_majors",
        label: "희망 학과",
        prompt: "가장 진학하고 싶은 학과나 전공은 무엇인가요? 복수로 답해도 괜찮아요.",
        placeholder: "예: 컴퓨터공학과, 데이터사이언스학과"
    },
];

let chatHistory = [];
let onboardingState = {
    isComplete: false,
    step: 0,
    answers: {}
};

// -- Initialization --

const init = () => {
    loadState();
    detectReloadAndReset(); // Reset on full reload if needed, or keep persistence
    renderHistory();
    restoreResultPanel(); // Restore right panel state

    if (!onboardingState.isComplete) {
        // Start or continue onboarding
        startOnboardingStep();
    }
};

const loadState = () => {
    // Load Chat History
    try {
        const storedHistory = sessionStorage.getItem(STORAGE_KEY_HISTORY);
        if (storedHistory) chatHistory = JSON.parse(storedHistory);
    } catch { chatHistory = []; }

    // Load Onboarding State
    try {
        const storedOnboarding = sessionStorage.getItem(STORAGE_KEY_ONBOARDING);
        if (storedOnboarding) {
            onboardingState = JSON.parse(storedOnboarding);
        }
    } catch {
        // Default state
    }
};

const saveState = () => {
    sessionStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(chatHistory));
    sessionStorage.setItem(STORAGE_KEY_ONBOARDING, JSON.stringify(onboardingState));
};

const detectReloadAndReset = () => {
    const navEntry = performance.getEntriesByType('navigation')[0];
    const isReload = navEntry
        ? navEntry.type === 'reload'
        : performance.navigation && performance.navigation.type === 1;

    // Optional: Clear session on reload if strictly desired. 
    // Usually users prefer persistence. Let's keep persistence for now.
    // if (isReload) { ... }
};

// -- UI Rendering --

const createBubble = (text, type) => {
    const bubble = document.createElement('div');
    bubble.classList.add('bubble', type);

    // Markdown-style Link Parsing: [Label](URL) -> <a href="URL">Label</a>
    let formattedText = text.replace(/\n/g, '<br>');
    formattedText = formattedText.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:#0066cc; text-decoration:underline;">$1</a>');

    bubble.innerHTML = formattedText;
    return bubble;
};

const appendBubble = (text, type, shouldPersist = true) => {
    if (!chatCanvas) return;
    const bubble = createBubble(text, type);
    chatCanvas.appendChild(bubble);
    chatCanvas.scrollTop = chatCanvas.scrollHeight;

    if (shouldPersist) {
        const role = type === 'user' ? 'user' : 'assistant';
        chatHistory.push({ role, content: text });
        saveState();
    }
    return bubble;
};

// Streaming/Typing effect for AI messages
const appendBubbleWithTyping = async (text, type, shouldPersist = true, speed = 20) => {
    if (!chatCanvas) return;

    const bubble = document.createElement('div');
    bubble.classList.add('bubble', type);
    chatCanvas.appendChild(bubble);

    // Typing effect
    let currentText = '';
    for (let i = 0; i < text.length; i++) {
        currentText += text[i];

        // Format with markdown links
        let formattedText = currentText.replace(/\n/g, '<br>');
        formattedText = formattedText.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:#0066cc; text-decoration:underline;">$1</a>');

        bubble.innerHTML = formattedText;
        chatCanvas.scrollTop = chatCanvas.scrollHeight;

        // Wait for next character
        await new Promise(resolve => setTimeout(resolve, speed));
    }

    if (shouldPersist) {
        const role = type === 'user' ? 'user' : 'assistant';
        chatHistory.push({ role, content: text });
        saveState();
    }

    return bubble;
};

const renderHistory = () => {
    if (!chatCanvas) return;
    chatCanvas.innerHTML = ''; // Clear existing
    chatHistory.forEach(msg => {
        const type = msg.role === 'user' ? 'user' : 'ai';
        chatCanvas.appendChild(createBubble(msg.content, type));
    });
    chatCanvas.scrollTop = chatCanvas.scrollHeight;
};

const showLoadingDetails = () => {
    if (!chatCanvas) return null;
    const loadingBubble = document.createElement('div');
    loadingBubble.classList.add('bubble', 'ai', 'loading');
    loadingBubble.textContent = '...';
    chatCanvas.appendChild(loadingBubble);
    chatCanvas.scrollTop = chatCanvas.scrollHeight;
    return loadingBubble;
};

// -- Onboarding Logic --

const startOnboardingStep = async () => {
    if (onboardingState.step >= ONBOARDING_QUESTIONS.length) {
        finishOnboarding();
        return;
    }

    const currentQ = ONBOARDING_QUESTIONS[onboardingState.step];

    // Check if we already asked this question in history (to avoid duplicates on refresh)
    // Simple heuristic: check if last AI message is the current prompt
    const lastAiMsg = chatHistory.slice().reverse().find(m => m.role === 'assistant');
    if (!lastAiMsg || lastAiMsg.content !== currentQ.prompt) {
        // Use typing effect for onboarding questions
        await appendBubbleWithTyping(currentQ.prompt, 'ai', true, 15);
    }

    if (chatInput) {
        chatInput.placeholder = currentQ.placeholder || "답변을 입력하세요...";
    }
};

const handleOnboardingInput = async (text) => {
    // 1. Show user answer
    appendBubble(text, 'user');

    // 2. Save answer
    const currentQ = ONBOARDING_QUESTIONS[onboardingState.step];
    onboardingState.answers[currentQ.key] = text;
    onboardingState.step++;
    saveState();

    // 3. Next step
    if (onboardingState.step < ONBOARDING_QUESTIONS.length) {
        startOnboardingStep();
    } else {
        await finishOnboarding();
    }
};

const finishOnboarding = async () => {
    onboardingState.isComplete = true;
    saveState();

    const loadingBubble = showLoadingDetails();

    try {
        // Call Major Recommendation API
        const response = await fetch(API_ONBOARDING_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: onboardingState.answers })
        });

        if (!response.ok) throw new Error("Onboarding API failed");

        const result = await response.json();

        if (loadingBubble) loadingBubble.remove();

        // Show Summary with typing effect
        const recs = result.recommended_majors || [];
        let summaryText = "온보딩 답변을 바탕으로 추천 전공 TOP 5를 정리했어요:\n";
        recs.slice(0, 5).forEach((major, idx) => {
            summaryText += `${idx + 1}. ${major.major_name} (점수 ${major.score.toFixed(2)})\n`;
        });
        summaryText += "\n필요하면 위 전공 중 궁금한 학과를 지정해서 더 물어봐도 좋아요!";

        await appendBubbleWithTyping(summaryText, 'ai', true, 15);

        // Update Setting Board (Right Panel) and save state
        updateResultPanel(result);

    } catch (e) {
        console.error(e);
        if (loadingBubble) loadingBubble.remove();
        await appendBubbleWithTyping("죄송합니다. 추천 정보를 불러오는데 실패했습니다.", 'ai', true, 20);
    }

    if (chatInput) chatInput.placeholder = "궁금한 점을 물어보세요!";
};

const updateResultPanel = (result) => {
    const resultCard = document.querySelector('.result-card');
    if (!resultCard) return;

    const recs = result.recommended_majors || [];
    if (recs.length === 0) {
        resultCard.innerHTML = "추천 결과가 없습니다.";
        sessionStorage.setItem(STORAGE_KEY_RESULT_PANEL, "추천 결과가 없습니다.");
        return;
    }

    let html = "<strong>추천 전공 결과:</strong><br><br>";
    recs.slice(0, 5).forEach((major, idx) => {
        html += `${idx + 1}. ${major.major_name}<br>`;
        html += `<small style="color:#666">${major.cluster || ''} - ${major.salary || '연봉정보 없음'}</small><br><br>`;
    });

    resultCard.innerHTML = html;

    // Save result panel state to sessionStorage
    sessionStorage.setItem(STORAGE_KEY_RESULT_PANEL, html);
};

// Restore result panel from sessionStorage
const restoreResultPanel = () => {
    const resultCard = document.querySelector('.result-card');
    if (!resultCard) return;

    const savedContent = sessionStorage.getItem(STORAGE_KEY_RESULT_PANEL);
    if (savedContent) {
        resultCard.innerHTML = savedContent;
    }
};

// -- Main Chat Logic --

const handleChatInput = async (text) => {
    // 1. Show user message
    appendBubble(text, 'user');

    const loadingBubble = showLoadingDetails();

    try {
        // Send history excluding the latest user message we just added
        // The backend `run_mentor` takes `chat_history`.
        // However, we just added the user message to `chatHistory` in `appendBubble`.
        // We should send `chatHistory` WITHOUT the last element, OR let backend handle it.
        // `run_mentor` code: 
        // messages.append(HumanMessage(content=question))
        // So we should NOT include the current question in history list passed to backend.

        const historyToSend = chatHistory.slice(0, -1);

        const response = await fetch(API_CHAT_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                history: historyToSend
            })
        });

        if (!response.ok) throw new Error('Network error');

        const data = await response.json();

        if (loadingBubble) loadingBubble.remove();

        // Use typing effect for AI responses
        await appendBubbleWithTyping(data.response, 'ai', true, 15);

    } catch (error) {
        console.error(error);
        if (loadingBubble) loadingBubble.remove();
        await appendBubbleWithTyping("오류가 발생했습니다.", 'ai', false, 20);
    }
};

const handleSubmit = async () => {
    if (!chatInput) return;
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = '';

    if (!onboardingState.isComplete) {
        await handleOnboardingInput(text);
    } else {
        await handleChatInput(text);
    }

    chatInput.focus();
};

// -- Event Listeners --

if (sendBtn) {
    sendBtn.addEventListener('click', handleSubmit);
}

if (chatInput) {
    chatInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.isComposing) {
            event.preventDefault();
            handleSubmit();
        }
    });
}

// Start
init();
