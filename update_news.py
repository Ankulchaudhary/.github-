from google import genai
import os

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY is missing.")
    exit(1)

# Initialize the client
client = genai.Client(api_key=api_key)

def generate_news_summary():
    try:
        # Added 'models/' prefix - this usually solves the 404 error
        response = client.models.generate_content(
            model="models/gemini-1.5-flash", 
            contents="Summarize the top 5 international news stories of today briefly."
        )
        
        with open("latest_news.md", "w", encoding="utf-8") as f:
            f.write("# Daily Abroad News Update\n\n")
            f.write(response.text)
            
        print("Success: latest_news.md has been created!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    generate_news_summary()
    
