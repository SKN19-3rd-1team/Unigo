const chatInput = document.querySelector('.chat-input');
const sendBtn = document.getElementById('chat-send-btn');
const chatCanvas = document.querySelector('.chat-canvas');

const STORAGE_KEY_HISTORY = 'unigo.app.chatHistory';
const STORAGE_KEY_ONBOARDING = 'unigo.app.onboarding';
const STORAGE_KEY_CONVERSATION_ID = 'unigo.app.currentConversationId';
const STORAGE_KEY_RESULT_PANEL = 'unigo.app.resultPanel';

const API_CHAT_URL = '/api/chat';
const API_ONBOARDING_URL = '/api/onboarding';

// Onboarding Questions Definition
const ONBOARDING_QUESTIONS = [
    {
        key: "subjects",
        label: "선호 교과목",
        prompt: "안녕하세요! 고등학교 과목 중 가장 자신 있거나 흥미로운 과목은 무엇인가요? (예: 수학, 물리를 잘하고 과학 실험을 좋아합니다)",
        placeholder: "예: 수학, 영어, 사회문화"
    },
    {
        key: "interests",
        label: "관심사 및 활동",
        prompt: "평소 즐겨 하는 활동이나 관심 있는 주제는 무엇인가요? 동아리 활동이나 취미도 좋아요.",
        placeholder: "예: 코딩 동아리, 역사 소설 읽기, 유튜브 영상 편집"
    },
    {
        key: "career_goal",
        label: "장래 희망",
        prompt: "장래 희망이나 관심 있는 직업 분야가 있나요? 구체적인 직업명이 아니어도 괜찮아요.",
        placeholder: "예: 인공지능 개발자, 교사, 마케터, 창업"
    },
    {
        key: "strengths",
        label: "성격 및 장점",
        prompt: "본인의 성격이나 장점은 무엇이라고 생각하나요? (예: 논리적이다, 상상력이 풍부하다, 꼼꼼하다)",
        placeholder: "예: 호기심이 많고 논리적으로 생각하는 것을 좋아해요."
    },
    {
        key: "career_field",
        label: "희망 진출 분야",
        prompt: "마지막으로, 졸업 후 어떤 분야에서 일하고 싶으신가요? (예: IT, 의료, 금융, 예술, 교육 등)",
        placeholder: "예: IT 플랫폼 기업, 병원, 은행, 방송국"
    },
];

let chatHistory = [];
let currentConversationId = null; // 현재 Conversation ID (로그인 사용자용)
let onboardingState = {
    isComplete: false,
    step: 0,
    answers: {}
};

// -- Initialization --

const init = async () => {
    await loadState();
    detectReloadAndReset(); // Reset on full reload if needed, or keep persistence
    renderHistory();
    restoreResultPanel(); // Restore right panel state

    if (!onboardingState.isComplete && onboardingState.step > 0) {
        // 이미 진행 중이던 온보딩이 있다면 계속 진행
        startOnboardingStep();
    } else {
        // 처음 접속했거나 온보딩이 완료된 상태라면 일반 대화 모드로 시작
        // 단, 진행 중이 아니면 isComplete를 true로 간주하여 placeholder 등이 일반 대화용으로 나오게 함
        onboardingState.isComplete = true;

        // 온보딩 완료 상태라면 Placeholder 업데이트
        if (chatInput) chatInput.placeholder = "궁금한 점을 물어보세요!";

        // 초기 환영 메시지 (채팅 기록이 비어 있을 때만)
        if (chatHistory.length === 0) {
            const welcomeMsg =
                "안녕하세요! 저는 대학 전공 선택과 입시 정보를 도와주는 멘토 AI입니다.\n\n" +
                "🎓 **저는 이런 정보를 드릴 수 있어요:**\n" +
                "- 관심사에 맞는 대학 전공 및 학과 추천\n" +
                "- 특정 학과의 진로 및 취업 정보\n" +
                "- 대학별 입시 전형 및 입결 정보\n\n" +
                "전공 추천을 받고 싶다면 **'추천 시작'**이라고 입력해주세요.";
            await appendBubbleWithTyping(welcomeMsg, 'ai', false, 20);
        }
    }

};

const loadState = async () => {
    // 1. 로그인된 사용자 확인
    try {
        const authResponse = await fetch('/api/auth/me');
        const authData = await authResponse.json();

        if (authData.is_authenticated) {
            console.log("User is authenticated. Fetching server history...");
            // [NEW] Update character image
            if (authData.user) {
                // [NEW] Handle custom image vs character persistence
                if (authData.user.custom_image_url) {
                    console.log("Loading custom image from server:", authData.user.custom_image_url);
                    updateCharacterImage(authData.user.character, authData.user.custom_image_url);
                    localStorage.setItem('user_custom_image', authData.user.custom_image_url);
                } else {
                    // If server says no custom image (or use_custom_image is False), remove from local
                    localStorage.removeItem('user_custom_image');

                    if (authData.user.character) {
                        console.log("Loading character from server:", authData.user.character);
                        updateCharacterImage(authData.user.character);
                    }
                }

                if (authData.user.character) {
                    localStorage.setItem('user_character', authData.user.character);
                }
            } else {
                // Fallback: check local storage just in case server returned nothing (guest/error?)
                const saved = localStorage.getItem('user_character');
                const savedCustom = localStorage.getItem('user_custom_image');
                if (savedCustom) updateCharacterImage(saved, savedCustom);
                else if (saved) updateCharacterImage(saved);
            }
            await fetchHistory();
            console.log("User is authenticated. Initializing fresh chat session...");

            // 로그인 사용자는 기본적으로 새로운 대화 세션으로 시작
            // 단, 이전에 불러온 conversation id가 sessionStorage에 있으면 복원
            try {
                const storedConvId = sessionStorage.getItem(STORAGE_KEY_CONVERSATION_ID);
                if (storedConvId) {
                    currentConversationId = storedConvId;
                    console.log('Restored conversation id from sessionStorage:', currentConversationId);
                } else {
                    currentConversationId = null;
                }
            } catch (e) {
                currentConversationId = null;
            }

            // 클라이언트 세션 상태도 초기화 (온보딩은 완료 상태로 유지)
            chatHistory = [];
            onboardingState = {
                isComplete: true,  // 이미 온보딩을 완료한 사용자로 간주
                step: 0,
                answers: {}
            };
            saveState();

            return; // Skip loading from local storage if logged in
        }
    } catch (e) {
        console.error("Auth check failed:", e);
    }

    // 2. Fallback: Load Chat History from SessionStorage (Guest)
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

const fetchHistory = async () => {
    // 로그인 사용자의 최근 대화 목록을 조회 (참고용)
    // 이 함수는 현재 대화 화면에는 영향을 주지 않고, 
    // 사용자가 이전 대화를 확인하고 싶을 때 "폴더" 버튼을 통해 호출됨
    try {
        const response = await fetch('/api/chat/history');
        if (!response.ok) throw new Error('Failed to fetch history');

        const data = await response.json();
        if (data.history && Array.isArray(data.history)) {
            // Server history format match: { role, content, ... }
            // NOTE: 이 함수는 대화 화면을 업데이트하지 않음.
            // 필요한 경우에만 폴더 버튼 등에서 호출되어 이전 대화를 복원함
            console.log("Fetched server history (for reference):", data.history);
        }
    } catch (e) {
        console.error("Error fetching history:", e);
    }
};

const saveState = () => {
    sessionStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(chatHistory));
    sessionStorage.setItem(STORAGE_KEY_ONBOARDING, JSON.stringify(onboardingState));
    try {
        if (currentConversationId) sessionStorage.setItem(STORAGE_KEY_CONVERSATION_ID, String(currentConversationId));
        else sessionStorage.removeItem(STORAGE_KEY_CONVERSATION_ID);
    } catch (e) {
        console.warn('Failed to save conversation id to sessionStorage', e);
    }
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

// Helper to get avatar URL
const getAvatarUrl = (type) => {
    // [MODIFIED] Check for custom image first for BOTH 'user' and 'ai'
    // Since the "Character" setting controls the AI Persona (and potentially User avatar),
    // the Custom Image should also apply to the AI to replace the character.

    // Check custom image first
    const customImg = (window.USER_CUSTOM_IMAGE_URL && window.USER_CUSTOM_IMAGE_URL !== '')
        ? window.USER_CUSTOM_IMAGE_URL
        : localStorage.getItem('user_custom_image');

    if (customImg) return customImg;

    // Fallback to character if no custom image
    const savedChar = (window.USER_CHARACTER && window.USER_CHARACTER !== 'None')
        ? window.USER_CHARACTER
        : localStorage.getItem('user_character');
    let filename = savedChar || 'rabbit';
    if (filename === 'hedgehog') filename = 'hedgehog_ver1';
    return `/static/images/${filename}.png`;
};

const createBubble = (text, type) => {
    // Container
    const container = document.createElement('div');
    container.classList.add('bubble-container', type);

    // Avatar
    const avatar = document.createElement('img');
    avatar.classList.add('chat-avatar');
    avatar.src = getAvatarUrl(type);
    avatar.alt = type === 'ai' ? 'AI' : 'User';
    container.appendChild(avatar);

    // Bubble
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');

    // Markdown-style Link Parsing: [Label](URL) -> <a href="URL">Label</a>
    let formattedText = text.replace(/\n/g, '<br>');
    formattedText = formattedText.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:#0066cc; text-decoration:underline;">$1</a>');

    bubble.innerHTML = formattedText;
    container.appendChild(bubble);

    return container; // Return container instead of just bubble
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

    // Create container
    const container = document.createElement('div');
    container.classList.add('bubble-container', type);

    // Avatar
    const avatar = document.createElement('img');
    avatar.classList.add('chat-avatar');
    avatar.src = getAvatarUrl(type);
    container.appendChild(avatar);

    // Bubble
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    container.appendChild(bubble);

    chatCanvas.appendChild(container);

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

    return container;
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

    // Use createBubble for loading state too to keep layout consistent
    // But text is just '...'
    const loadingContainer = createBubble('...', 'ai');
    loadingContainer.classList.add('loading'); // You might need CSS for .bubble-container.loading or .bubble.loading

    chatCanvas.appendChild(loadingContainer);
    chatCanvas.scrollTop = chatCanvas.scrollHeight;
    return loadingContainer;
};

// -- Onboarding Logic --

const startOnboardingStep = async () => {
    // 모든 질문이 끝나면 온보딩 완료 처리
    if (onboardingState.step >= ONBOARDING_QUESTIONS.length) {
        finishOnboarding();
        return;
    }

    const currentQ = ONBOARDING_QUESTIONS[onboardingState.step];

    // Check if we already asked this question in history (to avoid duplicates on refresh)
    // Simple heuristic: check if last AI message is the current prompt
    // 새로고침 시 이전에 질문했던 내용이 중복 출력되는 것을 방지합니다.
    const lastAiMsg = chatHistory.slice().reverse().find(m => m.role === 'assistant');
    if (!lastAiMsg || lastAiMsg.content !== currentQ.prompt) {
        // Use typing effect for onboarding questions
        // 온보딩 질문은 타이핑 효과와 함께 출력되어 사용자 몰입감을 높입니다.
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
            headers: getPostHeaders(),
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

    // 최종적으로 채팅 입력창의 placeholder를 변경하여 자유 질문이 가능함을 알림
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
        // 프론트엔드에서 방금 추가한 사용자 메시지가 chatHistory에 포함되어 있으므로,
        // 백엔드로 보낼 때는 이를 제외하고 보냅니다. (백엔드에서 현재 질문을 별도 파라미터로 받기 때문)

        const historyToSend = chatHistory.slice(0, -1);
        const requestBody = {
            message: text,
            history: historyToSend
        };

        // 로그인 사용자의 경우 현재 대화 ID를 함께 전송
        if (currentConversationId) {
            requestBody.conversation_id = currentConversationId;
        }

        const response = await fetch(API_CHAT_URL, {
            method: 'POST',
            headers: getPostHeaders(),
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) throw new Error('Network error');

        const data = await response.json();

        if (loadingBubble) loadingBubble.remove();

        // 로그인 사용자의 경우 첫 성공 응답에서 conversation_id 업데이트
        if (data.conversation_id && !currentConversationId) {
            currentConversationId = data.conversation_id;
            console.log('Conversation started with ID:', currentConversationId);
        }

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

    // Trigger check for Onboarding
    if (text === '추천 시작') {
        appendBubble(text, 'user');

        // Reset onboarding state
        onboardingState = {
            isComplete: false,
            step: 0,
            answers: {}
        };
        saveState(); // Save reset state

        // Start onboarding
        await startOnboardingStep();

        chatInput.focus();
        return;
    }

    if (!onboardingState.isComplete) {
        await handleOnboardingInput(text);
    } else {
        await handleChatInput(text);
    }

    chatInput.focus();
};

const resetChat = async () => {
    if (!confirm("대화 내용을 모두 지우고 처음부터 다시 시작하시겠습니까?")) return;

    // 1. 로그인 사용자에 한해 현재 채팅 내용을 DB에 저장 (새 채팅 생성 전)
    if (chatHistory.length > 0) {
        try {
            const authRes = await fetch('/api/auth/me');
            const authData = await authRes.json();

            if (authData && authData.is_authenticated) {
                const saveResponse = await fetch('/api/chat/save', {
                    method: 'POST',
                    headers: getPostHeaders(),
                    body: JSON.stringify({ history: chatHistory })
                });

                if (saveResponse.ok) {
                    const saveData = await saveResponse.json();
                    console.log('Chat history saved for user:', saveData);
                } else {
                    console.error('Failed to save chat history (server)');
                }
            } else {
                console.log('Guest user — skipping server save.');
            }
        } catch (e) {
            console.error('Error checking auth or saving chat history:', e);
        }
    }

    // 2. Backend Reset (If logged in)
    try {
        await fetch('/api/chat/reset', {
            method: 'POST',
            headers: getPostHeaders()
        });
    } catch (e) {
        console.error("Reset API check failed (might be guest):", e);
    }

    // 3. Clear Local State
    chatHistory = [];
    currentConversationId = null; // Reset conversation ID for new chat
    onboardingState = {
        isComplete: false,
        step: 0,
        answers: {}
    };
    saveState();
    sessionStorage.removeItem(STORAGE_KEY_HISTORY);
    sessionStorage.removeItem(STORAGE_KEY_ONBOARDING);
    sessionStorage.removeItem(STORAGE_KEY_RESULT_PANEL);
    sessionStorage.removeItem(STORAGE_KEY_CONVERSATION_ID);

    // 4. UI Reset
    if (chatCanvas) chatCanvas.innerHTML = '';
    const resultCard = document.querySelector('.result-card');
    if (resultCard) resultCard.innerHTML = `
        제가 당신에게 추천드리는 학과들로는 생명공학, 컴퓨터공학, AI융합전공, 데이터사이언스과, 소프트웨어공학과 등이 있으며 추가적으로 물리학과, 천문학 등도 고려하실 수 있습니다.
        <br><br>
        이외 더 자세한 학과정보 및 진로상담이 필요하시면 채팅창에 추가 질문을 해주세요.
    `;

    // 5. Restart Onboarding
    startOnboardingStep();
};

// -- Event Listeners --

// New Chat Button (using aria-label="새 채팅")
const newChatBtn = document.querySelector('.action-btn[aria-label="새 채팅"]');
if (newChatBtn) {
    newChatBtn.addEventListener('click', resetChat);
}

// Folder / History Button (using aria-label="폴더")
const folderBtn = document.querySelector('.action-btn[aria-label="폴더"]');
const showConversationList = async () => {
    const resultCard = document.querySelector('.result-card');
    if (!resultCard) return;

    // 로그인 사용자에 한해 대화 목록 가져오기
    try {
        const resp = await fetch('/api/chat/list');
        if (!resp.ok) throw new Error('Failed to fetch conversations');

        const data = await resp.json();
        const convs = data.conversations || [];

        if (convs.length === 0) {
            resultCard.innerHTML = '<p>저장된 과거 대화가 없습니다.</p>';
            return;
        }

        // 목록 HTML 생성
        let html = '<div class="conv-list"><h3>과거 대화 목록</h3><ul style="list-style:none;padding:0;">';
        convs.forEach(c => {
            html += `<li style="padding:8px 6px;border-bottom:1px solid #eee;cursor:pointer;" data-id="${c.id}">`;
            html += `<strong>${c.title || '(제목 없음)'}</strong><br>`;
            html += `<small style="color:#666">${c.updated_at.split('T')[0]} · ${c.message_count} messages</small><br>`;
            html += `<span style="color:#333">${c.last_message_preview || ''}</span>`;
            html += `</li>`;
        });
        html += '</ul><button id="conv-back-btn" style="margin-top:8px;">뒤로</button></div>';

        resultCard.innerHTML = html;

        // 각 대화 항목에 클릭 리스너 추가
        const items = resultCard.querySelectorAll('li[data-id]');
        items.forEach(it => {
            it.addEventListener('click', async (e) => {
                const convId = it.getAttribute('data-id');
                await loadConversation(convId);
            });
        });

        const backBtn = document.getElementById('conv-back-btn');
        if (backBtn) backBtn.addEventListener('click', () => restoreResultPanel());

    } catch (e) {
        console.error('Error loading conversation list:', e);
    }
};

const loadConversation = async (convId) => {
    if (!convId) return;

    // 충돌 처리: 현재 세션에 내용이 있으면 사용자에게 확인
    if (chatHistory.length > 0) {
        const saveConfirm = confirm('현재 대화가 있습니다. 서버에 저장한 후 불러오시겠습니까? (확인: 저장 후 불러오기 / 취소: 저장하지 않고 불러오기)');
        if (saveConfirm) {
            try {
                const saveResp = await fetch('/api/chat/save', {
                    method: 'POST',
                    headers: getPostHeaders(),
                    body: JSON.stringify({ history: chatHistory })
                });
                if (!saveResp.ok) console.error('Failed to save current conversation before loading');
            } catch (e) {
                console.error('Error saving before load:', e);
            }
        } else {
            const discardConfirm = confirm('저장하지 않고 불러오시겠습니까? (확인: 불러오기 / 취소: 취소)');
            if (!discardConfirm) return; // 사용자 취소
        }
    }

    try {
        const resp = await fetch(`/api/chat/load?conversation_id=${encodeURIComponent(convId)}`);
        if (!resp.ok) throw new Error('Failed to load conversation');

        const data = await resp.json();
        const conv = data.conversation;
        if (!conv) throw new Error('Invalid conversation data');

        // 현재 대화 기록 교체 및 렌더링
        chatHistory = conv.messages.map(m => ({ role: m.role, content: m.content }));
        currentConversationId = conv.id; // 과거 대화 불러올 때 대화 ID 업데이트
        saveState();
        renderHistory();

        // 온보딩 상태 업데이트: 완료로 표시하여 온보딩 프롬프트 방지
        onboardingState.isComplete = true;
        saveState();

        // 오른쪽 패널을 불러온 세션 제목으로 업데이트
        const resultCard = document.querySelector('.result-card');
        if (resultCard) resultCard.innerHTML = `<h3>불러온 대화: ${conv.title}</h3><p>${conv.messages.length}개의 메시지를 불러왔습니다.</p><button id="conv-back-btn2">뒤로</button>`;
        const backBtn = document.getElementById('conv-back-btn2');
        if (backBtn) backBtn.addEventListener('click', () => restoreResultPanel());

        console.log('Conversation loaded with ID:', currentConversationId);

    } catch (e) {
        console.error('Error loading conversation:', e);
        alert('세션 불러오기에 실패했습니다. 콘솔을 확인하세요.');
    }
};

if (folderBtn) {
    folderBtn.addEventListener('click', showConversationList);
}

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
function updateCharacterImage(characterId, customImageUrl = null) {
    console.log("updateCharacterImage called with:", characterId, customImageUrl);
    const imgEl = document.querySelector('.result-rabbit');
    if (!imgEl) {
        console.warn(".result-rabbit element not found!");
        return;
    }

    if (customImageUrl) {
        imgEl.src = customImageUrl;
        imgEl.alt = 'User Custom Character';
        imgEl.style.borderRadius = '20px'; // Style for custom image
        return;
    }

    // Map character IDs to image paths (simple wrapper)
    // If you have a more complex mapping, consider a dictionary, 
    // but here we can assume the ID matches filenames except maybe 'hedgehog'
    let filename = characterId;
    if (characterId === 'hedgehog') filename = 'hedgehog_ver1';

    // Safety check for valid ID or default
    if (!filename) filename = 'rabbit';

    imgEl.src = `/static/images/${filename}.png`;

    // Update alt text for accessibility
    imgEl.alt = `${Object.keys({
        'rabbit': '토끼', 'bear': '곰', 'fox': '여우',
        'hedgehog': '고슴도치', 'koala': '코알라', 'otter': '수달',
        'penguin': '펭귄', 'raccoon': '너구리', 'sloth': '나무늘보', 'turtle': '거북이'
    }).find(key => key === characterId) || 'User Character'}`;
}
