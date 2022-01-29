from django.db import models

# Create your models here.


class Topic(models.Model):
    topic_text = models.CharField(max_length=50)

    def __str__(self):
        return self.topic_text


class Tweet(models.Model):
    topic = models.ForeignKey(
        Topic, on_delete=models.SET_NULL, null=True, related_name='tweets')
    author = models.CharField(max_length=50)
    text = models.CharField(max_length=500)
    creation_date = models.DateTimeField()
    polarity = models.CharField(max_length=12, default="")
    polarity_index = models.DecimalField(
        decimal_places=4, max_digits=10, default=0.00)
