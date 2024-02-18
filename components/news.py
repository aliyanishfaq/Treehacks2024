from gnews import GNews
import whisper

def news(topic):
    google_news = GNews()
    news_data = google_news.get_news('Pakistan')
    headlines = [article['title'] for article in news_data]
    for headline in headlines:
        print(headline)