// ProTech Article JavaScript

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    loadRelatedArticles();
    initializeSearch();
    initializeShareButtons();
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

// Load Related Articles
function loadRelatedArticles() {
    const container = document.getElementById('related-articles');
    if (!container || !articles || articles.length === 0) return;
    
    // Get current article category from page
    const categoryBadge = document.querySelector('.category-badge');
    const currentCategory = categoryBadge ? categoryBadge.textContent.toLowerCase().trim() : null;
    
    // Get current article title
    const currentTitle = document.querySelector('.article-title')?.textContent;
    
    // Filter related articles
    let relatedArticles = articles.filter(article => {
        // Don't show current article
        if (currentTitle && article.title === currentTitle) return false;
        
        // Prefer same category
        if (currentCategory && article.cat === currentCategory) return true;
        
        return true;
    });
    
    // Shuffle and take 3
    relatedArticles = shuffleArray(relatedArticles).slice(0, 3);
    
    container.innerHTML = relatedArticles.map(article => `
        <div class="related-card" onclick="window.location.href='${article.url}'">
            <img src="${article.img}" alt="${article.title}" loading="lazy">
            <div class="related-card-content">
                <h3>${article.title}</h3>
                <p>${article.desc.substring(0, 100)}...</p>
            </div>
        </div>
    `).join('');
}

// Shuffle array
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
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
            <div class="search-result-item" onclick="window.location.href='../${article.url}'">
                <img src="${article.img}" alt="${article.title}">
                <div class="search-result-content">
                    <span class="search-result-category cat-${article.cat}">${article.cat.toUpperCase()}</span>
                    <h4>${highlightText(article.title, query)}</h4>
                    <p>${highlightText(article.desc.substring(0, 100) + '...', query)}</p>
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

// Share Functions
function initializeShareButtons() {
    // Get current page info
    window.currentPageUrl = window.location.href;
    window.currentPageTitle = document.querySelector('.article-title')?.textContent || 'ProTech Article';
}

function shareOnTwitter() {
    const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(window.currentPageTitle)}&url=${encodeURIComponent(window.currentPageUrl)}`;
    window.open(url, '_blank', 'width=550,height=420');
}

function shareOnFacebook() {
    const url = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.currentPageUrl)}`;
    window.open(url, '_blank', 'width=550,height=420');
}

function shareOnLinkedIn() {
    const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.currentPageUrl)}`;
    window.open(url, '_blank', 'width=550,height=420');
}

function copyLink() {
    navigator.clipboard.writeText(window.currentPageUrl).then(function() {
        const button = event.target.closest('.share-btn');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        
        setTimeout(() => {
            button.innerHTML = originalText;
        }, 2000);
    }).catch(function(err) {
        alert('Failed to copy link');
    });
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
    }
    
    mark {
        background: rgba(0, 122, 255, 0.3);
        color: var(--accent-blue);
        padding: 2px 4px;
        border-radius: 3px;
    }
`;
document.head.appendChild(searchStyles);
