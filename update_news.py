import os
import requests
import google.generativeai as genai
from datetime import datetime

# 1. API Keys (GitHub Secrets se uthayi jayengi)
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    articles = response.get('articles', [])
    # Sirf wahi news lein jinka description ho
    return [a for a in articles if a.get('description')][:3]

def analyze_news(title, desc):
    prompt = f"""
    Tum ek expert news analyst ho. Is news ko analyze karo:
    Title: {title}
    Description: {desc}
    
    Format (Strictly follow this):
    HEADLINE: [Hindi Headline]
    SUMMARY: [Short Hindi Summary]
    INSIGHT: [Hindi Analysis]
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return None

def update_html(news_list):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html_content = f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Abroad News - AI Portal</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50">
        <header class="bg-indigo-600 text-white shadow-lg p-6 text-center">
            <h1 class="text-3xl font-bold uppercase tracking-widest">Abroad News</h1>
            <p class="text-sm opacity-80 mt-2">AI Powered News Update | {now}</p>
        </header>
        <main class="container mx-auto p-4 max-w-4xl space-y-6">
    """
    
    for news in news_list:
        if not news: continue
        # Saaf tareeke se data nikalna
        lines = [l.strip() for l in news.split('\n') if l.strip()]
        h = "Nayi Khabar"
        s = "Puri jankari jald update hogi."
        i = "Analysis pending."
        
        for line in lines:
            if "HEADLINE:" in line: h = line.replace("HEADLINE:", "")
            if "SUMMARY:" in line: s = line.replace("SUMMARY:", "")
            if "INSIGHT:" in line: i = line.replace("INSIGHT:", "")

        html_content += f"""
            <article class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition">
                <h2 class="text-xl font-extrabold text-gray-800 mb-3">{h}</h2>
                <p class="text-gray-600 leading-relaxed mb-4">{s}</p>
                <div class="bg-indigo-50 p-4 rounded-xl text-indigo-900 text-sm border-l-4 border-indigo-600">
                    <strong>💡 AI Insight:</strong> {i}
                </div>
            </article>
        """
    
    html_content += """
        </main>
        <footer class="text-center p-8 text-gray-400 text-xs">
            &copy; 2026 Abroad News - Powered by Gemini AI
        </footer>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# Main Execution
raw_articles = get_news()
if not raw_articles:
    print("No news found! Check your NEWS_API_KEY.")
else:
    processed_news = []
    for art in raw_articles:
        analysis = analyze_news(art['title'], art['description'])
        if analysis: processed_news.append(analysis)
    
    if processed_news:
        update_html(processed_news)
        print("Success: Website updated!")
        
