from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

# Create your models here.
class User(models.Model):
    name=models.CharField(max_length=32)
    password=models.CharField(max_length=32)
    privilege=models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    totDown=models.FloatField(default=0)
    totUp=models.FloatField(default=0)

class Topic(models.Model):
    title=models.CharField(max_length=128)
    content=models.TextField()
    time=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='publisher')
    replys=models.ManyToManyField(User,through='Reply',related_name='repliers')

class Reply(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE)
    content=models.TextField()
    time=models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    name=models.CharField(max_length=32)

class Torrent(models.Model):
    name=models.CharField(max_length=128)
    time=models.DateTimeField(auto_now_add=True)
    link=models.CharField(max_length=512)
    count=models.IntegerField(default=0)
    score=models.FloatField(default=0)
    permission=models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(5)])
    size=models.FloatField()
    uploadUser=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='uploader')
    downloadUsers=models.ManyToManyField(User,related_name='downloaders')
    category=models.ManyToManyField(Category)
    rateBy=models.ManyToManyField(User,through='Rate',related_name='rater')
    inTopics=models.ManyToManyField(Topic)

class Rate(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    torrent = models.ForeignKey(Torrent,on_delete=models.CASCADE)
    score=models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    time=models.DateTimeField(auto_now_add=True)
    content=models.TextField()
