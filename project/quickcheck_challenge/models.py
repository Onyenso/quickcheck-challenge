from django.db import models
import datetime 
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    
    about = models.TextField(null=True, blank=True)
    submitted = models.ForeignKey("Base", on_delete=models.CASCADE, null=True)



class Base(models.Model):

    type_choices = [
        ("job", "job"),
        ("story", "story"),
        ("comment", "comment"),
        ("poll", "poll"),
        ("pollopt", "pollopt")
    ]

    # This feild, "HN_id", represents the id of the item from HN API.
    # If HN_id is null for any item, it means the item was not
    # gotten from HN.
    HN_id = models.IntegerField(null=True)
    # got_from_HN will be true if item from got from HN, else false
    got_from_HN = models.BooleanField()
    deleted = models.BooleanField(null=True)
    type = models.CharField(max_length=10, choices=type_choices)

    # Ideally, this "by" field is supposed to be a ForeignKey to
    # User model. But this means there will be an error when we try to
    # save an item from HN and the creator has no account with us.
    # It is also allowed to be null because some items from HN 
    # don't values for the field.
    by = models.CharField(max_length=100, null=True)
    time = models.IntegerField(null=True)
    dead = models.BooleanField(null=True)

    def serialize(self):
        return {
            "id": self.id,
            "HN_id": self.HN_id,
            "got_from_HN": self.got_from_HN,
            "deleted": self.deleted,
            "type": self.type,
            "by": self.by,
            "time": datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S'),
            "dead": self.dead
        }




class Job(Base):

    text = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "HN_id": self.HN_id,
            "got_from_HN": self.got_from_HN,
            "deleted": self.deleted,
            "type": self.type,
            "by": self.by,
            "time": datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S'),
            "dead": self.dead,
            "text": self.text,
            "url": self.url,
            "title": self.title
        }


    


class Story(Base):
    # The total comment count
    descendants = models.IntegerField(null=True)
    # The story's score
    score = models.IntegerField(null=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "HN_id": self.HN_id,
            "got_from_HN": self.got_from_HN,
            "deleted": self.deleted,
            "type": self.type,
            "by": self.by,
            "time": datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S'),
            "dead": self.dead,
            "descendants": self.descendants,
            "score": self.score,
            "title": self.title,
            "url": self.url
        }



class Comment(Base):

    # Parent is the relevant story or parent comment, if it exits
    parent = models.ForeignKey(Base, models.CASCADE, null=True, related_name="item_comment")
    text = models.TextField(null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "HN_id": self.HN_id,
            "got_from_HN": self.got_from_HN,
            "deleted": self.deleted,
            "type": self.type,
            "by": self.by,
            "time": datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S'),
            "dead": self.dead,
            "parent": self.parent,
            "text": self.text
        }




class Poll(Base):

    # The total comment count
    descendants = models.IntegerField(null=True)
    # Total number of votes for pollopt
    score = models.IntegerField(null=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "HN_id": self.HN_id,
            "got_from_HN": self.got_from_HN,
            "deleted": self.deleted,
            "type": self.type,
            "by": self.by,
            "time": datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S'),
            "dead": self.dead,
            "descendants": self.descendants,
            "score": self.score,
            "title": self.title,
            "text": self.text
        }



class Pollopt(Base):

    # The relevant Poll
    parent = models.ForeignKey(Base, on_delete=models.CASCADE, null=True, related_name="+")
    score = models.IntegerField(null=True)

    def serialize(self):
        return {
            "id": self.id,
            "HN_id": self.HN_id,
            "got_from_HN": self.got_from_HN,
            "deleted": self.deleted,
            "type": self.type,
            "by": self.by,
            "time": datetime.datetime.fromtimestamp(self.time).strftime('%Y-%m-%d %H:%M:%S'),
            "dead": self.dead,
            "parent": self.parent,
            "score": self.score
        }

