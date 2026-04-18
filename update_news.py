import os
import requests
import time
from google import genai
from datetime import datetime

# 1. API Keys
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup Client
client = genai.Client(api_key=GEMINI_API_KEY)

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url)
        articles = r.json().get('articles', [])
        # Sirf 2 news taki quota bache
        return [a for a in articles if a.get('title') and a.get('description')][:2]
    except:
        return []

def analyze_with_gemini(title, desc):
    prompt = f"Analyze this news in Hindi. HEADLINE: [Title], SUMMARY: [News], INSIGHT: [Analysis]. News: {title} - {desc}"
    
    # Retry Logic: Agar fail ho toh 10 second ruk kar dubara try karega
    for attempt in range(2):
        try:
            # 1.5-flash use kar rahe hain kyunki iska free limit better hai
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(10) # 10 second ka gap
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
    <body class="bg-slate-50">
        <header class="bg-indigo-900 text-white p-10 text-center shadow-lg">
            <h1 class="text-4xl font-bold">ABROAD NEWS</h1>
            <p class="mt-2 opacity-75">AI Update: {now}</p>
        </header>
        <main class="container mx-auto p-6 max-w-2xl space-y-6">
    """
    for news in news_list:
        if not news: continue
        try:
            h = news.split("HEADLINE:")[1].split("SUMMARY:")[0].strip()
            s = news.split("SUMMARY:")[1].split("INSIGHT:")[0].strip()
            i = news.split("INSIGHT:")[1].strip()
            
            html_content += f"""
            <div class="bg-white p-6 rounded-3xl shadow-sm border-l-8 border-indigo-600">
                <h2 class="text-xl font-bold mb-2">{h}</h2>
                <p class="text-gray-600 mb-4">{s}</p>
                <div class="text-sm bg-indigo-50 p-3 rounded-lg text-indigo-800 italic">Insight: {i}</div>
            </div>
            """
        except: continue
        
    html_content += "</main></body></html>"
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# Run
news_data = get_news()
if news_data:
    results = []
    for art in news_data:
        res = analyze_with_gemini(art['title'], art['description'])
        if res:
            results.append(res)
            time.sleep(5) # Har news ke baad 5 second ka wait (Quota bachaane ke liye)
    
    if results:
        update_html(results)
        print("SUCCESS: Site Updated!")
    else:
        print("GEMINI STILL BUSY: Quota reset ka intezar karein.")
        
