// ProTech Main JavaScript - Fixed CLS & LCP Issues

// Global variables
let currentFilter = 'all';
let displayedArticles = 12;
const articlesPerPage = 12;

// =============================================
// FIX 1: PRELOAD LCP IMAGE في <head> مباشرة
// أضف هذا الكود في HTML قبل أي شيء آخر:
// <link rel="preload" as="image" href="PATH_TO_FIRST_IMAGE" fetchpriority="high">
// =============================================

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    loadFeaturedArticle();
    loadArticles();
    initializeSearch();
    updateCategoryCounts();
});

// Navigation
function initializeNavigation() {
    const mobileMenu = document.getElementById('mobile-menu');
    const navList = document.getElementById('nav-list');

    if (mobileMenu) {
        mobileMenu.addEventListener('click', function() {
            navList.classList.toggle('active');
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });
    }
}

// =============================================
// FIX 2: Load Featured Article - إصلاح CLS
// المشكلة: الصور بدون أبعاد محددة مسبقاً تسبب CLS
// الحل: استخدام aspect-ratio + skeleton placeholder
// =============================================
function loadFeaturedArticle() {
    const container = document.getElementById('featured-article');
    if (!container || !articles || articles.length === 0) return;

    const article = articles[0];

    // FIX: حجز المساحة مسبقاً قبل تحميل الصورة لمنع CLS
    container.innerHTML = `
        <div class="featured-image" style="aspect-ratio: 16/9; position: relative; overflow: hidden; background: #1a1a2e;">
            <img src="${article.img}" 
                 alt="${article.title}" 
                 width="1200" 
                 height="675" 
                 loading="eager" 
                 fetchpriority="high" 
                 decoding="sync"
                 style="width: 100%; height: 100%; object-fit: cover; display: block;"
                 onerror="this.style.display='none'">
        </div>
        <div class="featured-content">
            <div class="featured-meta">
                <span class="featured-badge">${article.cat.toUpperCase()}</span>
                <span class="featured-date">
                    <i class="fas fa-calendar" aria-hidden="true"></i>
                    ${formatDate(article.date)}
                </span>
            </div>
            <h3>${article.title}</h3>
            <p>${article.desc}</p>
            <a href="${article.url}" class="read-more" aria-label="Read full story: ${article.title}">
                <span>Read Full Story</span>
                <i class="fas fa-arrow-right" aria-hidden="true"></i>
            </a>
        </div>
    `;

    // FIX: استخدام <a> بدل onclick لتحسين الأداء وتجنب reflow
    container.style.cursor = 'pointer';
    container.addEventListener('click', function(e) {
        if (!e.target.closest('a')) {
            window.location.href = article.url;
        }
    });
}

// =============================================
// FIX 3: Load Articles - إصلاح CLS للبطاقات
// المشكلة: البطاقات تظهر فجأة وتدفع المحتوى
// الحل: تحديد أبعاد ثابتة + skeleton loading
// =============================================
function loadArticles(filter = 'all') {
    const container = document.getElementById('news-grid');
    if (!container || !articles) return;

    currentFilter = filter;

    let filteredArticles = articles;
    if (filter !== 'all') {
        filteredArticles = articles.filter(article => article.cat === filter);
    }

    // Skip first article as it's featured
    filteredArticles = filteredArticles.slice(1);

    const articlesToShow = filteredArticles.slice(0, displayedArticles);

    // FIX: استخدام DocumentFragment لتجنب reflow متعدد
    const fragment = document.createDocumentFragment();
    const tempDiv = document.createElement('div');

    tempDiv.innerHTML = articlesToShow.map(article => `
        <article class="news-card" role="article">
            <a href="${article.url}" class="news-card-link" aria-label="${article.title}">
                <div class="news-card-image" 
                     style="aspect-ratio: 16/10; overflow: hidden; background: #1a1a2e; position: relative;">
                    <img src="${article.img}" 
                         alt="${article.title}" 
                         width="400" 
                         height="250" 
                         loading="lazy" 
                         decoding="async"
                         style="width: 100%; height: 100%; object-fit: cover; display: block;"
                         onerror="this.parentElement.style.background='#2a2a3e'">
                </div>
                <div class="news-card-content">
                    <div class="news-card-meta">
                        <span class="news-card-category cat-${article.cat}">${article.cat.toUpperCase()}</span>
                        <span class="news-card-date">${formatDate(article.date)}</span>
                    </div>
                    <h3>${article.title}</h3>
                    <p>${article.desc}</p>
                </div>
            </a>
        </article>
    `).join('');

    // FIX: استبدال المحتوى دفعة واحدة بدل innerHTML متعدد
    while (tempDiv.firstChild) {
        fragment.appendChild(tempDiv.firstChild);
    }

    container.innerHTML = '';
    container.appendChild(fragment);

    updateLoadMoreButton(filteredArticles.length);
}

// Filter Articles
function filterArticles(category) {
    displayedArticles = articlesPerPage;
    loadArticles(category);

    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    document.getElementById('news-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Filter by category (from hero tags)
function filterByCategory(category) {
    displayedArticles = articlesPerPage;
    loadArticles(category);
    document.getElementById('news-grid').scrollIntoView({ behavior: 'smooth' });
}

// Load More Articles
function loadMoreArticles() {
    displayedArticles += articlesPerPage;
    loadArticles(currentFilter);
}

// Update Load More Button
function updateLoadMoreButton(totalArticles) {
    const button = document.getElementById('load-more-btn');
    if (!button) return;

    if (displayedArticles >= totalArticles - 1) {
        button.style.display = 'none';
    } else {
        button.style.display = 'inline-flex';
    }
}

// Update Category Counts
function updateCategoryCounts() {
    if (!articles) return;

    const counts = {
        ai: 0,
        tech: 0,
        ios: 0,
        gaming: 0,
        leaks: 0,
        hardware: 0
    };

    articles.forEach(article => {
        if (counts.hasOwnProperty(article.cat)) {
            counts[article.cat]++;
        } else {
            counts.tech++;
        }
    });

    const updateCount = (id, count) => {
        const el = document.getElementById(id);
        if (el) el.textContent = `${count} article${count !== 1 ? 's' : ''}`;
    };

    updateCount('ai-count', counts.ai);
    updateCount('tech-count', counts.tech);
    updateCount('gadget-count', counts.ios);
    updateCount('gaming-count', counts.gaming);
    updateCount('leaks-count', counts.leaks);
    updateCount('trends-count', counts.hardware);
    updateCount('ios-count', counts.ios);
}

// Search Modal
function toggleSearchModal() {
    const modal = document.getElementById('searchModal');
    if (!modal) return;

    modal.classList.toggle('active');

    if (modal.classList.contains('active')) {
        document.getElementById('searchInputModal').focus();
    }
}

// =============================================
// FIX 4: Search - debounce لتقليل TBT
// =============================================
function initializeSearch() {
    const searchInput = document.getElementById('searchInputModal');
    const searchResults = document.getElementById('searchResultsModal');

    if (!searchInput || !searchResults) return;

    let debounceTimer;

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = this.value.toLowerCase().trim();

            if (query.length === 0) {
                searchResults.innerHTML = `
                    <div class="no-results">
                        <i class="fas fa-search"></i>
                        <p>Start typing to search...</p>
                    </div>
                `;
                return;
            }

            if (query.length < 2) return;

            const results = articles.filter(article => 
                article.title.toLowerCase().includes(query) ||
                article.desc.toLowerCase().includes(query) ||
                article.cat.toLowerCase().includes(query)
            );

            if (results.length === 0) {
                searchResults.innerHTML = `
                    <div class="no-results">
                        <i class="fas fa-search"></i>
                        <p>No results found for "${query}"</p>
                    </div>
                `;
                return;
            }

            searchResults.innerHTML = results.slice(0, 10).map(article => `
                <a href="${article.url}" class="search-result-item">
                    <img src="${article.img}" 
                         alt="${article.title}" 
                         width="80" 
                         height="80" 
                         loading="lazy" 
                         decoding="async"
                         style="width:80px;height:80px;object-fit:cover;border-radius:8px;flex-shrink:0;">
                    <div class="search-result-content">
                        <span class="search-result-category cat-${article.cat}">${article.cat.toUpperCase()}</span>
                        <h4>${highlightText(article.title, query)}</h4>
                        <p>${highlightText(article.desc.substring(0, 100) + '...', query)}</p>
                        <span class="search-result-date">${formatDate(article.date)}</span>
                    </div>
                </a>
            `).join('');
        }, 200); // debounce 200ms
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('searchModal');
            if (modal && modal.classList.contains('active')) {
                toggleSearchModal();
            }
        }
    });
}

// Highlight search text
function highlightText(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
}

// Format date
function formatDate(dateStr) {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const date = new Date(dateStr);
    return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
}

// Legal modals
function showLegal(type) {
    const url = type === 'privacy' ? 'privacy-policy.html' : 'terms-of-service.html';
    window.location.href = url;
}

// =============================================
// FIX 5: CSS مضمّن - أضف هذا في <style> في HTML
// لإصلاح CLS نهائياً
// =============================================
const criticalStyles = document.createElement('style');
criticalStyles.textContent = `
    /* === إصلاح CLS الرئيسي === */

    /* حجز مساحة ثابتة للـ featured article قبل تحميل JS */
    #featured-article {
        min-height: 400px; /* منع القفز عند التحميل */
        position: relative;
    }

    /* حجز مساحة ثابتة لكل بطاقة */
    .news-card {
        display: flex;
        flex-direction: column;
    }

    /* FIX CLS: aspect-ratio يمنع القفز عند تحميل الصور */
    .news-card-image {
        aspect-ratio: 16 / 10;
        overflow: hidden;
        background: #1a1a2e; /* skeleton color */
        position: relative;
    }

    .news-card-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
        /* منع layout shift أثناء التحميل */
        position: absolute;
        top: 0;
        left: 0;
    }

    .featured-image {
        aspect-ratio: 16 / 9;
        overflow: hidden;
        background: #1a1a2e;
        position: relative;
    }

    .featured-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    /* FIX: استخدام <a> بدل onclick في البطاقات */
    .news-card-link {
        text-decoration: none;
        color: inherit;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    /* === Search Styles === */
    .search-result-item {
        display: flex;
        gap: 15px;
        padding: 15px;
        background: var(--bg-card);
        border-radius: 12px;
        margin-bottom: 12px;
        cursor: pointer;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
        text-decoration: none;
        color: inherit;
    }

    .search-result-item:hover {
        border-color: var(--accent-blue);
        background: rgba(0, 122, 255, 0.05);
        transform: translateX(5px);
    }

    .search-result-content {
        flex: 1;
        min-width: 0;
    }

    .search-result-category {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .search-result-content h4 {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 6px;
        line-height: 1.4;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    .search-result-content p {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: 6px;
        line-height: 1.5;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    .search-result-date {
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    mark {
        background: rgba(0, 122, 255, 0.3);
        color: var(--accent-blue);
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: 600;
    }

    .no-results {
        text-align: center;
        padding: 60px 20px;
        color: var(--text-secondary);
    }

    .no-results i {
        font-size: 3rem;
        margin-bottom: 20px;
        opacity: 0.5;
    }

    .no-results p {
        font-size: 1.1rem;
    }
`;
document.head.appendChild(criticalStyles);

/* =============================================
   FIX 6: أضف هذا الكود في <head> HTML مباشرة
   لتحسين LCP (أهم إصلاح للـ LCP)
   =============================================

<head>
    <!-- Preconnect لتسريع تحميل الصور -->
    <link rel="preconnect" href="https://your-image-domain.com">
    
    <!-- Preload أول صورة (LCP image) - استبدل الرابط باسم الصورة الفعلية -->
    <link rel="preload" as="image" href="PATH_TO_FIRST_ARTICLE_IMAGE" fetchpriority="high">
    
    <!-- Critical CSS inline (لا تحمله من ملف خارجي) -->
    <style>
        /* ضع هنا CSS الأساسي لما يظهر فوق الطية */
        #featured-article { min-height: 400px; }
        .featured-image { aspect-ratio: 16/9; background: #1a1a2e; }
        .news-card-image { aspect-ratio: 16/10; background: #1a1a2e; }
    </style>
</head>

*/
