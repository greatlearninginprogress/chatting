from django.contrib import admin
from .models import UserContact, Friend, Message, Group, GroupMessage, Comment,Post
# Register your models here.


admin.site.register(UserContact)
admin.site.register([Friend, Message, Group, GroupMessage, Comment,Post])