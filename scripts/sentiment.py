from transformers import pipeline

def get_goodness_score(data):
    sentiment_analysis = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
    scores = sentiment_analysis(data)
    scores_positive = [score['score'] if score['label'] == 'POS' else 1-score['score'] for score in scores]
    return scores_positive

if __name__ == "__main__":
    print(get_goodness_score(["I love this app", "I hate this app"]))