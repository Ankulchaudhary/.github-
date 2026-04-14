import os
import requests
from google import genai
from datetime import datetime

# 1. API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# New SDK Setup
client = genai.Client(api_key=GEMINI_API_KEY)

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url)
        articles = r.json().get('articles', [])
        return [a for a in articles if a.get('title') and a.get('description')][:3]
    except:
        return []

def analyze_with_gemini(title, desc):
    prompt = f"Analyze this news in Hindi. Format: HEADLINE: [Title], SUMMARY: [News], INSIGHT: [Analysis]. News: {title} - {desc}"
    try:
        # Naye SDK ka naya tareeka
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def update_html(news_list):
    now = datetime.now().strftime('%d %b %Y | %I:%M %p')
    html_content = f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Abroad News</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <header class="bg-blue-800 text-white p-6 text-center shadow-lg">
            <h1 class="text-3xl font-bold uppercase">ABROAD NEWS</h1>
            <p class="text-xs opacity-80 mt-2">AI UPDATE: {now}</p>
        </header>
        <main class="container mx-auto p-4 max-w-2xl space-y-6 mt-4">
    """
    for news in news_list:
        if not news: continue
        # Parsing logic
        h = news.split("HEADLINE:")[1].split("SUMMARY:")[0].strip() if "HEADLINE:" in news else "Breaking News"
        s = news.split("SUMMARY:")[1].split("INSIGHT:")[0].strip() if "SUMMARY:" in news else "Processing..."
        i = news.split("INSIGHT:")[1].strip() if "INSIGHT:" in news else "AI Insight pending."
        
        html_content += f"""
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-8 border-blue-600">
                <h2 class="text-xl font-bold mb-2 text-gray-800">{h}</h2>
                <p class="text-gray-600 mb-4">{s}</p>
                <p class="text-sm italic text-blue-700 bg-blue-50 p-2 rounded">Insight: {i}</p>
            </div>
        """
    html_content += "</main></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# EXECUTION
news_data = get_news()
if news_data:
    final_results = []
    for art in news_data:
        res = analyze_with_gemini(art['title'], art['description'])
        if res: final_results.append(res)
    
    if final_results:
        update_html(final_results)
        print("SUCCESS: Website updated with New SDK!")
        
