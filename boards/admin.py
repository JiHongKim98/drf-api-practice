from django.contrib import admin

from .models import CommentModel, PostModel

admin.site.register(PostModel)
admin.site.register(CommentModel)
