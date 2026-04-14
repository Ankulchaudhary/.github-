import os
import requests
import google.generativeai as genai

# 1. API Keys (GitHub Secrets se uthayi jayengi)
NEWS_API_KEY = os.getenv("")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    return response.get('articles', [])[:3] # Top 3 news

def analyze_news(title, desc):
    prompt = f"""
    Tum ek expert news analyst ho. Is news ko analyze karo:
    Title: {title}
    Description: {desc}
    
    Mujhe niche diye gaye format mein Hindi mein response do:
    HEADLINE: (Attractive Headline)
    SUMMARY: (Short news summary)
    INSIGHT: (Iska aam aadmi par impact aur future analysis)
    """
    response = model.generate_content(prompt)
    return response.text

def update_html(news_data):
    # HTML ka template jisme news insert hogi
    html_content = f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AbroadNews</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <header class="bg-white shadow p-4 text-center">
            <h1 class="text-2xl font-bold text-indigo-600">abroad-news</h1>
            <p class="text-sm text-gray-500">Last Updated: Just Now</p>
        </header>
        <main class="container mx-auto p-4 space-y-6">
    """
    
    for item in news_data:
        # Gemini ke response ko parse karna (Simple split method)
        lines = item.split('\n')
        html_content += f"""
            <article class="bg-white p-6 rounded-xl shadow-md border-l-4 border-indigo-500">
                <h2 class="text-xl font-bold mb-2">{lines[0].replace('HEADLINE:', '')}</h2>
                <p class="text-gray-600 mb-4">{lines[1].replace('SUMMARY:', '')}</p>
                <div class="bg-indigo-50 p-4 rounded-lg italic text-indigo-800 text-sm">
                    <strong>AI Insight:</strong> {lines[2].replace('INSIGHT:', '')}
                </div>
            </article>
        """
    
    html_content += """
        </main>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# Main Execution
raw_news = get_news()
analyzed_news_list = []

for article in raw_news:
    analysis = analyze_news(article['title'], article.get('description', 'No description available'))
    analyzed_news_list.append(analysis)

if analyzed_news_list:
    update_html(analyzed_news_list)
    print("Website updated successfully!")
