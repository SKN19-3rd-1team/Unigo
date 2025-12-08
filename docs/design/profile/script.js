// 캐릭터 데이터
const characters = [
    {
        name: '토끼',
        image: '../../assets/rabbit.png',
        description: '활발하고 호기심 많은 성격으로 새로운 것을 탐험하는 것을 좋아합니다.',
    },
    {
        name: '곰',
        image: '../../assets/bear.png',
        description: '든든하고 믿음직한 성격으로 친구들을 보호하고 배려합니다.',
    },
    {
        name: '여우',
        image: '../../assets/fox.png',
        description: '영리하고 재치있는 성격으로 문제 해결 능력이 뛰어납니다.',
    },
    {
        name: '고슴도치',
        image: '../../assets/hedgehog_ver1.png',
        description: '조심스럽지만 따뜻한 마음을 가진 성격으로 진정한 친구를 소중히 여깁니다.',
    },
    {
        name: '코알라',
        image: '../../assets/koala.png',
        description: '느긋하고 평화로운 성격으로 안정감을 주는 존재입니다.',
    },
    {
        name: '수달',
        image: '../../assets/otter.png',
        description: '장난기 많고 사교적인 성격으로 주변을 즐겁게 만듭니다.',
    },
    {
        name: '펭귄',
        image: '../../assets/penguin.png',
        description: '충성스럽고 성실한 성격으로 목표를 향해 꾸준히 나아갑니다.',
    },
    {
        name: '너구리',
        image: '../../assets/raccoon.png',
        description: '호기심 많고 창의적인 성격으로 독특한 시각을 가지고 있습니다.',
    },
    {
        name: '나무늘보',
        image: '../../assets/sloth.png',
        description: '여유롭고 사려 깊은 성격으로 신중하게 생각하며 행동합니다.',
    },
    {
        name: '거북이',
        image: '../../assets/turtle.png',
        description: '인내심 있고 지혜로운 성격으로 장기적인 목표를 추구합니다.',
    }
];

let currentIndex = 0;
const totalItems = characters.length;
const theta = 360 / totalItems; // 각 아이템 사이의 각도
const radius = 400; // 회전 반경

// 초기화
function init() {
    const carousel = document.getElementById('carousel3d');

    // 캐러셀 아이템 생성
    characters.forEach((character, index) => {
        const item = document.createElement('div');
        item.className = `carousel-item ${index === 0 ? 'active' : ''}`;
        item.innerHTML = `
            <img src="${character.image}" alt="${character.name}" class="character-image">
        `;

        // 3D 원형 배치
        const angle = theta * index;
        item.style.transform = `rotateY(${angle}deg) translateZ(${radius}px)`;

        // 클릭 이벤트
        item.addEventListener('click', () => {
            const clickedIndex = index;
            const diff = clickedIndex - currentIndex;

            if (diff > totalItems / 2) {
                rotateCarousel(-(totalItems - diff));
            } else if (diff < -totalItems / 2) {
                rotateCarousel(totalItems + diff);
            } else {
                rotateCarousel(diff);
            }
        });

        carousel.appendChild(item);
    });

    // 버튼 이벤트
    document.getElementById('prevBtn').addEventListener('click', () => rotateCarousel(-1));
    document.getElementById('nextBtn').addEventListener('click', () => rotateCarousel(1));
    document.getElementById('selectBtn').addEventListener('click', selectCharacter);

    // 키보드 이벤트
    document.addEventListener('keydown', handleKeyboard);

    // 마우스 드래그
    setupDrag();

    // 초기 정보 업데이트
    updateCharacterInfo();
}

// 캐러셀 회전
function rotateCarousel(direction) {
    currentIndex = (currentIndex + direction + totalItems) % totalItems;

    const carousel = document.getElementById('carousel3d');
    const angle = -theta * currentIndex;
    carousel.style.transform = `rotateY(${angle}deg)`;

    // 활성 아이템 업데이트
    const items = document.querySelectorAll('.carousel-item');
    items.forEach((item, index) => {
        item.classList.toggle('active', index === currentIndex);
    });

    updateCharacterInfo();
}

// 캐릭터 정보 업데이트
function updateCharacterInfo() {
    const character = characters[currentIndex];
    document.getElementById('characterName').textContent = character.name;
    document.getElementById('characterDesc').textContent = character.description;
}

// 캐릭터 선택
function selectCharacter() {
    const character = characters[currentIndex];
    alert(`${character.name}을(를) 선택하셨습니다!\n\n${character.description}`);
    // 여기에 다음 페이지로 이동하거나 데이터를 저장하는 로직 추가
}

// 키보드 네비게이션
function handleKeyboard(e) {
    if (e.key === 'ArrowLeft') {
        rotateCarousel(-1);
    } else if (e.key === 'ArrowRight') {
        rotateCarousel(1);
    } else if (e.key === 'Enter') {
        selectCharacter();
    }
}

// 드래그 기능
function setupDrag() {
    const scene = document.querySelector('.carousel-scene');
    let isDragging = false;
    let startX = 0;
    let currentX = 0;

    scene.addEventListener('mousedown', (e) => {
        isDragging = true;
        startX = e.clientX;
        scene.style.cursor = 'grabbing';
    });

    scene.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        currentX = e.clientX;
    });

    scene.addEventListener('mouseup', (e) => {
        if (!isDragging) return;

        const diff = startX - currentX;

        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                rotateCarousel(1);
            } else {
                rotateCarousel(-1);
            }
        }

        isDragging = false;
        scene.style.cursor = 'grab';
    });

    scene.addEventListener('mouseleave', () => {
        isDragging = false;
        scene.style.cursor = 'grab';
    });

    // 터치 이벤트
    scene.addEventListener('touchstart', (e) => {
        isDragging = true;
        startX = e.touches[0].clientX;
    });

    scene.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        currentX = e.touches[0].clientX;
    });

    scene.addEventListener('touchend', () => {
        if (!isDragging) return;

        const diff = startX - currentX;

        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                rotateCarousel(1);
            } else {
                rotateCarousel(-1);
            }
        }

        isDragging = false;
    });

    scene.style.cursor = 'grab';
}

// 자동 회전 (선택사항 - 주석 해제하면 자동으로 회전)
// setInterval(() => {
//     rotateCarousel(1);
// }, 3000);

// 페이지 로드시 초기화
init();