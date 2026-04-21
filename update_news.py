import google.generativeai as genai
import os
import requests

# 1. Setup Gemini API
# This reads the key you saved in GitHub Settings -> Secrets
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    exit(1)

genai.configure(api_key=api_key)

def generate_news_summary():
    try:
        # Using Gemini 1.5 Flash (Fast and efficient)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = "Provide a summary of the top 5 international news stories for today in a professional format."
        
        response = model.generate_content(prompt)
        
        # Save the result to a file
        with open("latest_news.md", "w", encoding="utf-8") as f:
            f.write("# Daily Abroad News Update\n\n")
            f.write(response.text)
            
        print("News successfully updated!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_news_summary()
    
