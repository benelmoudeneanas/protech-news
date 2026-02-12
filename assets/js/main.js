// ProTech Main JavaScript

// Global variables
let currentFilter = 'all';
let displayedArticles = 12;
const articlesPerPage = 12;

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

// Load Featured Article (first article)
function loadFeaturedArticle() {
    const container = document.getElementById('featured-article');
    if (!container || !articles || articles.length === 0) return;
    
    const article = articles[0];
    
    container.innerHTML = `
        <div class="featured-image">
            <img src="${article.img}" alt="${article.title}" loading="lazy">
        </div>
        <div class="featured-content">
            <div class="featured-meta">
                <span class="featured-badge">${article.cat.toUpperCase()}</span>
                <span class="featured-date">
                    <i class="fas fa-calendar"></i>
                    ${formatDate(article.date)}
                </span>
            </div>
            <h3>${article.title}</h3>
            <p>${article.desc}</p>
            <a href="${article.url}" class="read-more">
                <span>Read Full Story</span>
                <i class="fas fa-arrow-right"></i>
            </a>
        </div>
    `;
    
    container.onclick = () => window.location.href = article.url;
}

// Load Articles
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
    
    container.innerHTML = articlesToShow.map(article => `
        <div class="news-card" onclick="window.location.href='${article.url}'">
            <div class="news-card-image">
                <img src="${article.img}" alt="${article.title}" loading="lazy">
            </div>
            <div class="news-card-content">
                <div class="news-card-meta">
                    <span class="news-card-category cat-${article.cat}">${article.cat.toUpperCase()}</span>
                    <span class="news-card-date">${formatDate(article.date)}</span>
                </div>
                <h3>${article.title}</h3>
                <p>${article.desc}</p>
            </div>
        </div>
    `).join('');
    
    // Update load more button
    updateLoadMoreButton(filteredArticles.length);
}

// Filter Articles
function filterArticles(category) {
    displayedArticles = articlesPerPage;
    loadArticles(category);
    
    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Scroll to articles
    document.getElementById('news-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Filter by category (from hero tags)
function filterByCategory(category) {
    displayedArticles = articlesPerPage;
    loadArticles(category);
    
    // Scroll to articles
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
    
    if (displayedArticles >= totalArticles - 1) { // -1 because first is featured
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
    
    // Update UI
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

// Initialize Search
function initializeSearch() {
    const searchInput = document.getElementById('searchInputModal');
    const searchResults = document.getElementById('searchResultsModal');
    
    if (!searchInput || !searchResults) return;
    
    searchInput.addEventListener('input', function() {
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
            <div class="search-result-item" onclick="window.location.href='${article.url}'">
                <img src="${article.img}" alt="${article.title}">
                <div class="search-result-content">
                    <span class="search-result-category cat-${article.cat}">${article.cat.toUpperCase()}</span>
                    <h4>${highlightText(article.title, query)}</h4>
                    <p>${highlightText(article.desc.substring(0, 100) + '...', query)}</p>
                    <span class="search-result-date">${formatDate(article.date)}</span>
                </div>
            </div>
        `).join('');
    });
    
    // Close modal on Escape key
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
    const regex = new RegExp(`(${query})`, 'gi');
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
    const content = type === 'privacy' 
        ? 'Privacy Policy content will be added here.'
        : 'Terms of Service content will be added here.';
    
    alert(content);
}

// Add styles for search results
const searchStyles = document.createElement('style');
searchStyles.textContent = `
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
    }
    
    .search-result-item:hover {
        border-color: var(--accent-blue);
        background: rgba(0, 122, 255, 0.05);
        transform: translateX(5px);
    }
    
    .search-result-item img {
        width: 80px;
        height: 80px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    .search-result-content {
        flex: 1;
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
    }
    
    .search-result-content p {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: 6px;
        line-height: 1.5;
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
    }
`;
document.head.appendChild(searchStyles);
