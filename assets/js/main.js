// ProTech News - Optimized JavaScript
// Performance improvements and lazy loading

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeMobileMenu();
    initializeSearch();
    initializeKeyboardShortcuts();
    loadHomeFeed();
});

// Mobile Menu Toggle
function initializeMobileMenu() {
    const mobileMenu = document.getElementById('mobile-menu');
    const navList = document.querySelector('.nav-list');
    
    if (mobileMenu) {
        mobileMenu.addEventListener('click', function() {
            this.classList.toggle('active');
            navList.classList.toggle('active');
        });
    }
    
    // Close menu on outside click
    document.addEventListener('click', function(event) {
        const nav = document.querySelector('nav');
        if (!nav.contains(event.target) && navList.classList.contains('active')) {
            navList.classList.remove('active');
            mobileMenu.classList.remove('active');
        }
    });
}

// Search Modal
function initializeSearch() {
    const searchBtn = document.querySelector('.search-btn');
    const searchModal = document.getElementById('searchModal');
    const searchInput = document.getElementById('searchInputModal');
    
    if (searchBtn && searchModal) {
        searchBtn.addEventListener('click', toggleSearchModal);
        searchInput.addEventListener('input', liveSearchModal);
    }
}

function toggleSearchModal() {
    const modal = document.getElementById('searchModal');
    modal.style.display = modal.style.display === 'block' ? 'none' : 'block';
    if (modal.style.display === 'block') {
        document.getElementById('searchInputModal').focus();
    }
}

function liveSearchModal() {
    const query = document.getElementById('searchInputModal').value.toLowerCase();
    const resultsDiv = document.getElementById('searchResultsModal');
    
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '<div class="no-results"><i class="fas fa-search"></i><p>Start typing to search...</p></div>';
        return;
    }
    
    const filtered = articles.filter(a => 
        a.title.toLowerCase().includes(query) || 
        a.desc.toLowerCase().includes(query) ||
        a.cat.toLowerCase().includes(query)
    );
    
    if (filtered.length === 0) {
        resultsDiv.innerHTML = '<div class="no-results"><i class="fas fa-sad-tear"></i><p>No results found for "' + query + '"</p></div>';
        return;
    }
    
    resultsDiv.innerHTML = '';
    filtered.slice(0, 10).forEach(article => {
        const imgSrc = article.img || 'https://via.placeholder.com/400x300/0a0b10/007aff?text=ProTech';
        resultsDiv.innerHTML += `
            <div class="search-result-item" onclick="window.location.href='${article.url || article.slug + '.html'}'">
                <img src="${imgSrc}" alt="${article.title}" class="search-result-img" loading="lazy">
                <div class="search-result-content">
                    <span class="feed-cat" style="position: relative; top: 0; left: 0; margin-bottom: 10px;">${article.cat}</span>
                    <h4>${article.title}</h4>
                    <p>${article.desc.substring(0, 150)}...</p>
                </div>
            </div>
        `;
    });
}

// Keyboard Shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // ESC to close modal
        if (e.key === 'Escape') {
            const modal = document.getElementById('searchModal');
            if (modal && modal.style.display === 'block') {
                toggleSearchModal();
            }
        }
        
        // Ctrl+K or Cmd+K to open search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            toggleSearchModal();
        }
    });
}

// Load Home Feed
function loadHomeFeed() {
    const container = document.getElementById('feed-container');
    if (!container) return;
    
    const sortedArticles = articles.sort((a, b) => b.id - a.id);
    renderArticles(sortedArticles, container);
}

// Render Articles with Lazy Loading
function renderArticles(articlesList, container) {
    container.innerHTML = '';
    
    articlesList.forEach(article => {
        const imgSrc = article.img || 'https://via.placeholder.com/400x300/0a0b10/007aff?text=ProTech';
        const articleUrl = article.url || article.slug + '.html';
        
        const card = document.createElement('div');
        card.className = 'feed-card';
        card.onclick = () => window.location.href = articleUrl;
        
        card.innerHTML = `
            <img src="${imgSrc}" alt="${article.title}" class="feed-img" loading="lazy">
            <div class="feed-content">
                <span class="feed-cat">${article.cat}</span>
                <h3>${article.title}</h3>
                <p>${article.desc.substring(0, 120)}...</p>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// Quick Search Tags
function setQuickSearch(term) {
    toggleSearchModal();
    document.getElementById('searchInputModal').value = term;
    liveSearchModal();
}

// Filter by Category
function filterByCategory(category) {
    const container = document.getElementById('feed-container');
    const filtered = articles.filter(a => a.cat.toLowerCase() === category.toLowerCase());
    renderArticles(filtered, container);
}

// Close Menu Helper
function closeMenu() {
    document.querySelector('.nav-list').classList.remove('active');
    document.getElementById('mobile-menu').classList.remove('active');
}

// Legal Modal
function showLegal(type) {
    const content = {
        privacy: {
            title: '🔒 Privacy Policy',
            text: 'At ProTech, we prioritize your privacy. We use cookies and similar technologies to analyze site traffic, personalize content, and serve relevant advertisements through partners like Google AdSense. By continuing to use our site, you consent to our data collection practices as outlined in this policy.'
        },
        terms: {
            title: '📜 Terms of Service',
            text: 'Welcome to ProTech. By using our website, you agree to comply with these terms. All content, including tech leaks and reviews, is for informational purposes only. Unauthorized reproduction of our original material is strictly prohibited.'
        }
    };
    
    const modal = document.createElement('div');
    modal.id = 'legal-modal-overlay';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(10, 11, 16, 0.97);
        backdrop-filter: blur(15px);
        z-index: 100000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 25px;
        animation: fadeIn 0.3s ease;
    `;
    modal.innerHTML = `
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 50px;
            border-radius: 25px;
            max-width: 600px;
            width: 100%;
            border: 2px solid rgba(0, 122, 255, 0.3);
            box-shadow: 0 25px 70px rgba(0, 0, 0, 0.6);
            animation: slideUp 0.4s ease;
        ">
            <h2 style="
                background: linear-gradient(135deg, #007aff 0%, #00d4ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 2rem;
                margin: 0 0 30px 0;
                font-weight: 900;
            ">${content[type].title}</h2>
            <p style="
                line-height: 1.9;
                color: #94a3b8;
                margin-bottom: 35px;
                font-size: 1.05rem;
            ">${content[type].text}</p>
            <button onclick="document.getElementById('legal-modal-overlay').remove()" style="
                background: linear-gradient(135deg, #007aff 0%, #00d4ff 100%);
                color: white;
                border: none;
                padding: 18px 35px;
                border-radius: 12px;
                cursor: pointer;
                width: 100%;
                font-weight: 700;
                font-size: 1.05rem;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                transition: all 0.3s ease;
                box-shadow: 0 8px 25px rgba(0, 122, 255, 0.4);
            ">Got it!</button>
        </div>
    `;
    document.body.appendChild(modal);
}
