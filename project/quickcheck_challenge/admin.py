from django.contrib import admin

from .models import User, Job, Story, Comment, Poll, Pollopt

# Register your models here.
admin.site.register(User)
admin.site.register(Job)
admin.site.register(Story)
admin.site.register(Comment)
admin.site.register(Poll)
admin.site.register(Pollopt)