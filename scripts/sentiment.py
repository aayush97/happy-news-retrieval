from transformers import pipeline, AutoTokenizer
from itertools import chain
tokenizer = AutoTokenizer.from_pretrained(
    "finiteautomata/bertweet-base-sentiment-analysis", model_max_length=128)
sentiment_analysis = pipeline(
    model="finiteautomata/bertweet-base-sentiment-analysis", return_all_scores=False)


def get_goodness_score(data):
    scores = sentiment_analysis(data, padding=True, truncation=True)
    scores_positive = [score['score'] if score['label'] ==
                       'POS' else 1-score['score'] for score in scores]
    return scores_positive


if __name__ == "__main__":
    print(get_goodness_score(["I love this app", "I hate this app"]))
