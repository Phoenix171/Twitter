from nltk.corpus import stopwords
from django.shortcuts import render
from tweepy import OAuthHandler, API, Cursor
import tweepy as tweepy
from .models import Topic, Tweet
from .forms import TopicForm
from .serializers import TweetSerializer, TopicSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser
import re
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob

nltk.download('stopwords')
stop = stopwords.words('english')

api_key = "wOvdtRA6dk1jV7Py93gsZJWgQ"
api_key_secret = "dBlpmjSNzSqEUscFZFGl4ttQju8chlfhXLE1zKHH9xRJ4JzBw8"
access_key = "1486357430653308930-SuODORFypcLd7XyAwx8jU97sbcmYx2"
access_token_secret = "e1PHgDb2fZKUL7kuh67R4LBltJBw24z2ubgGuBQ4CNCDx"
search_words = "#OMICRON"
date_since = "2022-01-01"
# search_words = "OMICRON"


def fetch_and_save_tweets_from_api(search, pk):
    print("Entered function")
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_key, access_token_secret)
    api = tweepy.API(auth)
    tweets = tweepy.Cursor(api.search_30_day,
                           label="develop",
                           query=search)
    count = 0
    topic = Topic.objects.get(id=pk)
    for tweet in tweets.items(100):
        tweet_id = tweet.id
        status = api.get_status(tweet_id, tweet_mode='extended')
        raw_text = status.full_text.lower()
        text = re.sub(
            r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", raw_text)

        final_text = " ".join(
            [word for word in text.split() if word not in (stop)])
        # Processing Text Data

        polarity_index = TextBlob(final_text).sentiment.polarity
        # 1 if A else 2 if B else 3
        polarity = "NEUTRAL" if polarity_index == 0 else "POSITIVE" if polarity_index > 0 else "NEGATIVE"
        polarity_index = round(polarity_index, 4)
        Tweet.objects.create(
            topic=topic, author=tweet.user.name, text=final_text, creation_date=tweet.created_at, polarity=polarity, polarity_index=polarity_index)

    print(count)
    print(type(tweets))


@api_view(['GET', 'POST'])
def home(request):
    if request.method == "POST":
        filled_form = TopicForm(request.POST)
        if filled_form.is_valid():
            text = filled_form.cleaned_data['topic_text']
            try:
                topic = Topic.objects.get(topic_text=text)
                return render(request, 'detail.html', {'topic': topic})
            except Topic.DoesNotExist:
                new_topic = TopicSerializer(data=request.data)
                if new_topic.is_valid():
                    print("Topic model saved")
                    new_topic.save()
                topic = Topic.objects.get(topic_text=text)
                print(type(topic), topic)
                fetch_and_save_tweets_from_api(text, topic.id)
                # tweets = Topic.tweets.get(topic=topic)
            return render(request, 'detail.html', {'topic': topic})
    if request.method == "GET":
        form = TopicForm()
        return render(request, 'home.html', {'form': form})


def analyze(request, pk):
    # topic = Topic.objects.get(id=pk).tweets.order_by('-polarity_index')
    total_count = Topic.objects.get(
        id=pk).tweets.all().count()
    positive_tweets = Topic.objects.get(
        id=pk).tweets.all().filter(polarity="POSITIVE")
    positive_count = positive_tweets.count()
    negative_tweets = Topic.objects.get(
        id=pk).tweets.all().filter(polarity="NEGATIVE")
    negative_count = negative_tweets.count()
    neutral_tweets = Topic.objects.get(
        id=pk).tweets.all().filter(polarity="NEUTRAL")
    neutral_count = neutral_tweets.count()
    positive_count_perc = round((positive_count/total_count)*100, 2)
    negative_count_perc = round((negative_count/total_count)*100, 2)
    neutral_count_perc = round((neutral_count/total_count)*100, 2)
    return render(request, 'analyze.html', {'positive_tweets': positive_tweets,
                                            "negative_tweets": negative_tweets,
                                            "neutral_tweets": neutral_tweets,
                                            'positive_count': positive_count,
                                            'negative_count': negative_count,
                                            'neutral_count': neutral_count,
                                            'total_count': total_count,
                                            'positive_count_perc': positive_count_perc,
                                            'negative_count_perc': negative_count_perc,
                                            'neutral_count_perc': neutral_count_perc
                                            })
