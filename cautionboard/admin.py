from django.contrib import admin
from .models import Comment
from .models import Text

admin.site.register(Comment)
admin.site.register(Text)
