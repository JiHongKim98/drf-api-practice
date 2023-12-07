from django.db import models
from accounts.models import User


# 게시판 모델
class PostModel(models.Model):
    # FK (User 모델과의 관계 설정)
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name= "post_owner")

    title = models.CharField(max_length=255)
    contents = models.TextField()
    created_date = models.DateTimeField("작성일", auto_now_add=True, null=False)
    updated_date = models.DateTimeField("마지막 수정일", auto_now=True, null=False)
    
    def __str__(self) -> str:
        return self.title
    
    class Meta:
        # 역순으로 정렬
        ordering = ['-id']
