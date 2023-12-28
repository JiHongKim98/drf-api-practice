from django.db import models
from accounts.models import User


# 게시판 모델
class PostModel(models.Model):
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "post")

    title = models.CharField(max_length=255)
    contents = models.TextField()
    created_date = models.DateTimeField("작성일", auto_now_add=True, null=False)
    updated_date = models.DateTimeField("마지막 수정일", auto_now=True, null=False)
    
    def __str__(self) -> str:
        return self.title
    
    class Meta:
        ordering = ['-id']


# 댓글 모델
class CommentModel(models.Model):
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "comment")
    post = models.ForeignKey(PostModel, on_delete= models.CASCADE, related_name= "comment")

    contents = models.TextField(null= False)
    created_date = models.DateTimeField("작성일", auto_now_add=True, null=False)
    updated_date = models.DateTimeField("마지막 수정일", auto_now=True, null=False)

    def __str__(self) -> str:
        return f"{self.owner} 님의 댓글"
    
    class Meta:
        ordering = ['-id']

