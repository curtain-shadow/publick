// ==================== 页面交互逻辑（完整适配后端路由） ====================
(function() {
    // ---------- API 配置 ----------
    const API_BASE = '';  // 使用绝对路径，因为同域
    
    // ---------- 全局元素 ----------
    const userMenu = document.getElementById('userMenu');
    const dropdown = document.getElementById('userDropdown');
    const toggleBtn = document.getElementById('toggleHeroCardBtn');
    const heroContent = document.querySelector('.hero-content');
    const recommendGrid = document.getElementById('recommendGrid');
    const hotGrid = document.getElementById('hotGrid');
    const patternCountSpan = document.getElementById('patternCount');
    const designCountSpan = document.getElementById('designCount');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const dynastyFilter = document.getElementById('dynastyFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const navbar = document.getElementById('navbar');

    // 滚动观察器
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

    // ---------- 辅助函数：图片URL处理 ----------
    function getThumbUrl(pattern) {
        if (pattern.thumbnail) {
            if (pattern.thumbnail.startsWith('/media/') || pattern.thumbnail.startsWith('http')) {
                return pattern.thumbnail;
            }
            return `/media/${pattern.thumbnail}`;
        }
        return generatePlaceholderSVG(pattern.name);
    }

    function generatePlaceholderSVG(text, bgColor = '#D4A373', textColor = '#4A2A1E') {
        const svg = `
            <svg xmlns="http://www.w3.org/2000/svg" width="200" height="160" viewBox="0 0 200 160">
                <rect width="200" height="160" fill="${bgColor}" />
                <text x="50%" y="50%" font-size="24" fill="${textColor}" text-anchor="middle" dy=".3em" font-family="'Noto Serif SC', serif">${text}</text>
            </svg>
        `;
        return 'data:image/svg+xml,' + encodeURIComponent(svg);
    }
    
    // ---------- 创建卡片（精简版，无任何特效元素）----------
    function createPatternCard(pattern, isHot = false) {
        const card = document.createElement('div');
        card.className = 'pattern-card';
        
        const imgUrl = getThumbUrl(pattern);
        const dynastyName = pattern.dynasty_name || pattern.dynasty_detail?.name || '未知';
        const desc = pattern.meaning || pattern.story || '';
        
        if (isHot) {
            // 热门纹样：图片在上，文字在下，信息全部显示
            card.innerHTML = `
                <div class="card-img-wrapper">
                    <img src="${imgUrl}" alt="${pattern.name}" onerror="this.src='${generatePlaceholderSVG(pattern.name)}'">
                </div>
                <div class="pattern-info">
                    <h3>${pattern.name}</h3>
                    <div class="pattern-meta">
                        <span>${dynastyName}</span>
                        <span>点赞数： ${pattern.like_count || 0}</span>
                    </div>
                    ${desc ? `<div class="pattern-desc">${desc}</div>` : ''}
                </div>
            `;
        } else {
            // 推荐纹样：图片在上，文字在下，寓意默认隐藏，悬停时展开
            card.innerHTML = `
                <div class="card-img-wrapper">
                    <img src="${imgUrl}" alt="${pattern.name}" onerror="this.src='${generatePlaceholderSVG(pattern.name)}'">
                </div>
                <div class="pattern-info">
                    <h3>${pattern.name}</h3>
                    <div class="info-basic">${dynastyName}</div>
                    ${desc ? `<div class="info-expand">${desc}</div>` : ''}
                </div>
            `;
        }

        // 点击跳转详情
        card.addEventListener('click', (e) => {
            e.stopPropagation();
            window.location.href = `/pattern/${pattern.id}/`;
        });

        observer.observe(card);
        return card;
    }

    // ---------- 加载统计数据 ----------
    async function loadStats() {
        try {
            const res = await fetch('/api/patterns/stats/');
            const data = await res.json();
            if (patternCountSpan) patternCountSpan.textContent = data.pattern_count || '2486';
            if (designCountSpan) designCountSpan.textContent = data.design_count || '157';
        } catch (err) {
            console.warn('统计数据加载失败', err);
        }
    }

    // ---------- 加载筛选选项（朝代、分类）----------
    async function loadFilterOptions() {
        try {
            const dynastyRes = await fetch('/api/patterns/dynasties/');
            const dynastyData = await dynastyRes.json();
            const dynasties = Array.isArray(dynastyData) ? dynastyData : (dynastyData.results || []);
            if (dynastyFilter) {
                dynasties.forEach(d => {
                    if (d.name !== '不明') {
                        const option = document.createElement('option');
                        option.value = d.id;
                        option.textContent = d.name;
                        dynastyFilter.appendChild(option);
                    }
                });
            }
            
            const categoryRes = await fetch('/api/patterns/categories/');
            const categoryData = await categoryRes.json();
            const categories = Array.isArray(categoryData) ? categoryData : (categoryData.results || []);
            if (categoryFilter) {
                categories.forEach(c => {
                    const option = document.createElement('option');
                    option.value = c.id;
                    option.textContent = c.name;
                    categoryFilter.appendChild(option);
                });
            }
        } catch (err) {
            console.warn('筛选选项加载失败', err);
        }
    }

    // ---------- 加载推荐纹样 ----------
    async function loadRecommendedPatterns() {
        if (!recommendGrid) return;
        try {
            const res = await fetch('/api/patterns/patterns/recommended/');
            const data = await res.json();
            let patterns = Array.isArray(data) ? data : (data.results || []);
            patterns = patterns.slice(0, 8);
            recommendGrid.innerHTML = '';
            if (patterns.length === 0) {
                recommendGrid.innerHTML = '<div class="loading-spinner">暂无推荐纹样</div>';
                return;
            }
            patterns.forEach(p => {
                recommendGrid.appendChild(createPatternCard(p, false));
            });
        } catch (err) {
            console.error('推荐纹样加载失败', err);
            recommendGrid.innerHTML = '<div class="loading-spinner">加载失败，请刷新</div>';
        }
    }

    // ---------- 加载热门纹样 ----------
    async function loadHotPatterns() {
        if (!hotGrid) return;
        try {
            const res = await fetch('/api/patterns/patterns/hot/');
            const data = await res.json();
            let patterns = Array.isArray(data) ? data : (data.results || []);
            patterns = patterns.slice(0, 6);
            hotGrid.innerHTML = '';
            if (patterns.length === 0) {
                hotGrid.innerHTML = '<div class="loading-spinner">暂无热门纹样</div>';
                return;
            }
            patterns.forEach(p => {
                hotGrid.appendChild(createPatternCard(p, true));
            });
        } catch (err) {
            console.error('热门纹样加载失败', err);
            hotGrid.innerHTML = '<div class="loading-spinner">加载失败，请刷新</div>';
        }
    }

    // ---------- 筛选功能 ----------
    async function performSearch() {
        const keyword = searchInput?.value || '';
        const dynasty = dynastyFilter?.value || '';
        const category = categoryFilter?.value || '';
        
        let url = '/api/patterns/patterns/';
        const params = [];
        if (keyword) params.push(`search=${encodeURIComponent(keyword)}`);
        if (dynasty) params.push(`dynasty=${dynasty}`);
        if (category) params.push(`category=${category}`);
        if (params.length) url += '?' + params.join('&');
        
        try {
            const res = await fetch(url);
            const data = await res.json();
            const patterns = Array.isArray(data) ? data : (data.results || []);
            recommendGrid.innerHTML = '';
            patterns.slice(0, 12).forEach(p => {
                recommendGrid.appendChild(createPatternCard(p, false));
            });
            const header = document.querySelector('#recommendGrid').closest('.section').querySelector('h2');
            if (keyword) {
                header.textContent = `搜索"${keyword}"的结果`;
            } else if (dynasty || category) {
                const dynastyText = dynastyFilter.options[dynastyFilter.selectedIndex]?.text || '';
                const categoryText = categoryFilter.options[categoryFilter.selectedIndex]?.text || '';
                if (dynasty && category) header.textContent = `${dynastyText} · ${categoryText}`;
                else if (dynasty) header.textContent = dynastyText;
                else if (category) header.textContent = categoryText;
            } else {
                header.textContent = '推荐纹样';
            }
            recommendGrid.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } catch (err) {
            console.error('筛选失败', err);
        }
    }

    // ---------- 事件绑定 ----------
    function bindEvents() {
        if (userMenu) {
            userMenu.addEventListener('click', (e) => {
                e.stopPropagation();
                const dropdown = document.getElementById('userDropdown');
                // 仅当存在下拉菜单且当前为已登录状态（即下拉菜单内有内容）时才切换
                if (dropdown && dropdown.children.length > 0) {
                    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
                }
            });
            document.addEventListener('click', () => {
                const dropdown = document.getElementById('userDropdown');
                if (dropdown) dropdown.style.display = 'none';
            });
        }
        
        let isCardVisible = true;
        if (toggleBtn && heroContent) {
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (isCardVisible) {
                    heroContent.classList.add('card-hidden');
                    toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
                    toggleBtn.title = '显示标题卡片';
                    isCardVisible = false;
                } else {
                    heroContent.classList.remove('card-hidden');
                    toggleBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
                    toggleBtn.title = '隐藏标题卡片';
                    isCardVisible = true;
                }
            });
        }
        
        window.addEventListener('scroll', () => {
            if (navbar) {
                if (window.scrollY > 50) navbar.classList.add('scrolled');
                else navbar.classList.remove('scrolled');
            }
        });

        if (searchBtn) searchBtn.addEventListener('click', performSearch);
        if (searchInput) searchInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') performSearch(); });
        if (dynastyFilter) dynastyFilter.addEventListener('change', performSearch);
        if (categoryFilter) categoryFilter.addEventListener('change', performSearch);
        // 游客按钮：点击直接跳转登录页
        const guestBtn = document.getElementById('guestLoginBtn');
        if (guestBtn) {
            guestBtn.addEventListener('click', (e) => {
                e.stopPropagation();           // 阻止事件冒泡，避免触发 userMenu 的下拉切换
                window.location.href = '/accounts/login/';
            });
        }

        const logoutForm = document.getElementById('logoutForm');
        if (logoutForm) {
            logoutForm.addEventListener('submit', () => {
                localStorage.removeItem('token');
                localStorage.removeItem('username');
                localStorage.removeItem('userId');
                localStorage.removeItem('email');
            });
        }
    }

    // ---------- 初始化 ----------
    async function init() {
        loadStats();
        await loadFilterOptions();
        loadRecommendedPatterns();
        loadHotPatterns();
        bindEvents();
        document.querySelectorAll('.section-header, .filter-bar').forEach(el => observer.observe(el));
    }

    init();

    // ========== 热门纹样 3D 悬停左右区分增强 ==========
    setTimeout(() => {
        const hotGrid = document.getElementById('hotGrid');
        if (!hotGrid) return;

        const cards = hotGrid.querySelectorAll('.pattern-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                // 为当前卡片之前的所有兄弟添加 left 类
                let prev = card.previousElementSibling;
                while (prev) {
                    prev.classList.add('hot-hover-left');
                    prev = prev.previousElementSibling;
                }
            });
            card.addEventListener('mouseleave', () => {
                cards.forEach(c => c.classList.remove('hot-hover-left'));
            });
        });
    }, 800);
})();