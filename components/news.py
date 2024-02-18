from gnews import GNews

def news(topic):
    google_news = GNews()
    news_data = google_news.get_news(topic)
    headlines = [article['title'] for article in news_data]
    for headline in headlines:
        print(headline)