import os
import requests
import google.generativeai as genai
from datetime import datetime

# 1. API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Setup with Error Handling for Model Names
genai.configure(api_key=GEMINI_API_KEY)

def get_model():
    # Hum sabse pehle 1.5-flash try karenge, phir pro
    for m in ["gemini-1.5-flash", "gemini-pro", "models/gemini-1.5-flash"]:
        try:
            model = genai.GenerativeModel(m)
            # Chhota sa test run
            model.generate_content("test")
            print(f"Using model: {m}")
            return model
        except:
            continue
    return None

model = get_model()

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get('articles', [])
        return [a for a in articles if a.get('title') and a.get('description')][:3]
    except:
        return []

def analyze_news(title, desc):
    if not model:
        print("No working Gemini model found!")
        return None
    
    prompt = f"Analyze this news in Hindi. Format: HEADLINE: [Title], SUMMARY: [News], INSIGHT: [Analysis]. News: {title} - {desc}"
    try:
        response = model.generate_content(prompt)
        return response.text if response else None
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
    <body class="bg-slate-100">
        <header class="bg-blue-900 text-white p-6 text-center shadow-lg">
            <h1 class="text-3xl font-bold">ABROAD NEWS</h1>
            <p class="text-sm opacity-75">AI Update: {now}</p>
        </header>
        <main class="container mx-auto p-4 max-w-2xl space-y-6">
    """
    for news in news_list:
        lines = [l.strip() for l in news.split('\n') if l.strip()]
        h, s, i = "News", "Update...", "Analysis..."
        for line in lines:
            if "HEADLINE:" in line: h = line.replace("HEADLINE:", "")
            if "SUMMARY:" in line: s = line.replace("SUMMARY:", "")
            if "INSIGHT:" in line: i = line.replace("INSIGHT:", "")
        
        html_content += f"""
            <div class="bg-white p-6 rounded-2xl shadow-sm border-l-4 border-blue-600">
                <h2 class="text-xl font-bold mb-2">{h}</h2>
                <p class="text-gray-600 mb-4">{s}</p>
                <p class="text-sm italic text-blue-800">Insight: {i}</p>
            </div>
        """
    html_content += "</main></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# Final Execution
news_data = get_news()
if news_data:
    final_list = []
    for art in news_data:
        res = analyze_news(art['title'], art['description'])
        if res: final_list.append(res)
    
    if final_list:
        update_html(final_list)
        print("Success: Website Updated!")
        
