#!/usr/bin/env python3
"""
ProTech Article Generator
Automatically generates article HTML files from the template
"""

import os
import re
from datetime import datetime

# Configuration
TEMPLATE_PATH = "templates/article-template.html"
ARTICLES_DIR = "articles"
DATA_JS_PATH = "assets/js/data.js"

def format_date(date_str):
    """Convert date string to formatted date"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def get_category_class(category):
    """Map category to CSS class"""
    category_map = {
        'ios': 'cat-ios',
        'ai': 'cat-ai',
        'leaks': 'cat-leaks',
        'hardware': 'cat-hardware',
        'gaming': 'cat-gaming',
        'tech': 'cat-tech'
    }
    return category_map.get(category.lower(), 'cat-tech')

def generate_article(article_data):
    """
    Generate an article HTML file from template
    
    article_data = {
        'title': 'Article Title',
        'description': 'Article description',
        'keywords': 'keyword1, keyword2',
        'category': 'ios',
        'date': '2026-02-12',
        'image': 'https://...',
        'slug': 'article-slug',  # Optional, will be auto-generated
        'content': 'HTML content here'
    }
    """
    
    # Read template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Generate slug if not provided
    if 'slug' not in article_data or not article_data['slug']:
        article_data['slug'] = slugify(article_data['title'])
    
    # Prepare replacements
    replacements = {
        '{{TITLE}}': article_data['title'],
        '{{DESCRIPTION}}': article_data['description'],
        '{{KEYWORDS}}': article_data.get('keywords', article_data['title']),
        '{{CANONICAL_URL}}': f"https://protech-news.vercel.app/articles/{article_data['slug']}.html",
        '{{IMAGE}}': article_data['image'],
        '{{DATE}}': article_data['date'],
        '{{DATE_FORMATTED}}': format_date(article_data['date']),
        '{{CATEGORY}}': article_data['category'].upper(),
        '{{CATEGORY_CLASS}}': get_category_class(article_data['category']),
        '{{TITLE_SHORT}}': article_data['title'][:50] + '...' if len(article_data['title']) > 50 else article_data['title'],
        '{{CONTENT}}': article_data['content']
    }
    
    # Apply replacements
    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    # Write article file
    output_path = os.path.join(ARTICLES_DIR, f"{article_data['slug']}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Article generated: {output_path}")
    return output_path

def add_to_data_js(article_data):
    """Add article to data.js"""
    
    new_article = f'''  {{
    slug: "{article_data['slug']}",
    title: "{article_data['title']}",
    date: "{article_data['date']}",
    cat: "{article_data['category'].lower()}",
    desc: "{article_data['description']}",
    img: "{article_data['image']}",
    url: "articles/{article_data['slug']}.html"
  }},'''
    
    # Read data.js
    with open(DATA_JS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Insert after "const articles = ["
    insert_pos = content.find('const articles = [') + len('const articles = [')
    new_content = content[:insert_pos] + '\n\n  // ==================== LATEST ====================\n' + new_article + content[insert_pos:]
    
    # Write back
    with open(DATA_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Article added to data.js")

# Example usage
if __name__ == "__main__":
    print("🚀 ProTech Article Generator")
    print("=" * 50)
    
    # Example: Create a new article
    example_article = {
        'title': 'Example Article Title',
        'description': 'This is an example article description that will appear in search results and social media shares.',
        'keywords': 'example, article, tech news',
        'category': 'tech',
        'date': '2026-02-12',
        'image': 'https://via.placeholder.com/1200x630',
        'content': '''
            <h2>Introduction</h2>
            <p>This is the first paragraph of your article. You can write your content here using HTML tags.</p>
            
            <h2>Main Points</h2>
            <p>Add more paragraphs, headings, images, and other HTML elements as needed.</p>
            
            <h3>Subheading Example</h3>
            <p>You can use h3 tags for subheadings.</p>
            
            <blockquote>
                You can also add blockquotes for important statements or quotes.
            </blockquote>
            
            <h2>Conclusion</h2>
            <p>Wrap up your article with a conclusion.</p>
        '''
    }
    
    # Uncomment to generate example article
    # generate_article(example_article)
    # add_to_data_js(example_article)
    
    print("\nTo create a new article, use:")
    print("generate_article(article_data)")
    print("\nSee the example_article dictionary for the required format.")
