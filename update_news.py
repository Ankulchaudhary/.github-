import os
import requests
from google import genai
from datetime import datetime

# 1. API Keys (GitHub Secrets)
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini 2.0 Client Setup
client = genai.Client(api_key=GEMINI_API_KEY)

def get_news():
    # Global news fetch kar rahe hain
    url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if data.get('status') != 'ok':
            print(f"News API Error: {data.get('message')}")
            return []
        articles = data.get('articles', [])
        # Quota bachaane ke liye sirf top 2 news le rahe hain
        return [a for a in articles if a.get('title') and a.get('description')][:2]
    except Exception as e:
        print(f"News Fetching Error: {e}")
        return []

def analyze_with_gemini(title, desc):
    # Gemini 2.0 Flash - Sabse fast aur latest
    prompt = f"Analyze this news in Hindi. Format: HEADLINE: [Title], SUMMARY: [News], INSIGHT: [Analysis]. News: {title} - {desc}"
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini Analysis Error: {e}")
        return None

def update_html(news_list):
    now = datetime.now().strftime('%d %b %Y | %I:%M %p')
    html_content = f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Abroad News - AI Portal</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap');
            body {{ font-family: 'Noto Sans Devanagari', sans-serif; }}
        </style>
    </head>
    <body class="bg-slate-50 text-slate-900">
        <header class="bg-indigo-900 text-white p-10 text-center shadow-2xl">
            <h1 class="text-5xl font-black tracking-tighter uppercase">ABROAD NEWS</h1>
            <p class="text-indigo-200 mt-4 font-mono text-sm underline">LAST AI UPDATE: {now}</p>
        </header>
        <main class="container mx-auto p-6 max-w-3xl space-y-10 mt-8">
    """
    
    for news in news_list:
        if not news: continue
        try:
            h = news.split("HEADLINE:")[1].split("SUMMARY:")[0].strip()
            s = news.split("SUMMARY:")[1].split("INSIGHT:")[0].strip()
            i = news.split("INSIGHT:")[1].strip()
        except:
            h, s, i = "Breaking Update", news[:150], "Analysis in progress..."
        
        html_content += f"""
            <article class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-200 hover:shadow-xl transition-all duration-300">
                <h2 class="text-2xl font-bold text-indigo-950 mb-4 leading-tight">{h}</h2>
                <p class="text-slate-600 mb-6 leading-relaxed text-lg">{s}</p>
                <div class="bg-indigo-50 p-5 rounded-2xl text-indigo-900 text-sm border-l-4 border-indigo-600 italic">
                    <strong>💡 AI Insight:</strong> {i}
                </div>
            </article>
        """
    
    html_content += """
        </main>
        <footer class="text-center p-12 text-slate-400 text-xs tracking-widest uppercase">
            &copy; 2026 Abroad News | Powered by Gemini 2.0 Flash
        </footer>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

# Main Execution
print("Step 1: Fetching News...")
raw_data = get_news()
if raw_data:
    print(f"Step 2: Found {len(raw_data)} articles. Sending to Gemini...")
    final_results = []
    for art in raw_data:
        analysis = analyze_with_gemini(art['title'], art['description'])
        if analysis:
            final_results.append(analysis)
    
    if final_results:
        update_html(final_results)
        print("Step 3: SUCCESS! Website updated.")
    else:
        print("Error: Gemini Quota Full or Analysis failed.")
else:
    print("Error: No news fetched.")
    
