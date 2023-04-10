from sentiment import get_goodness_score
import pandas as pd

df_good = pd.read_csv("data/good_tweets.csv")
df_bad = pd.read_csv("data/davidson_hate_tweets_labeled.csv")

df_good_sample = df_good.sample(1000)

goodness_scores_good = get_goodness_score(df_good_sample['Tweet'].tolist())
# goodness_scores_bad = get_goodness_score(df_bad['tweet'].tolist()[:1000])
df_good_sample['label']  = ["POS" if score > 0.5 else "NEG" for score in goodness_scores_good]
df_good_sample['score'] = goodness_scores_good
df_good_sample.to_csv("data/good_tweets_sentiment.csv", index=False)

accuracy_good = sum([1 if score > 0.5 else 0 for score in goodness_scores_good])/len(goodness_scores_good)
# # accuracy_bad = sum([1 if score < 0.5 else 0 for score in goodness_scores_bad])/len(goodness_scores_bad)

# print("Good tweets average score:", sum(goodness_scores_good)/len(goodness_scores_good))
# print("Bad tweets average score:", sum(goodness_scores_bad)/len(goodness_scores_bad))
print("Good tweets accuracy:", accuracy_good)
# print("Bad tweets accuracy:", accuracy_bad)