from django.db import models

class Qna(models.Model):
    title = models.CharField(max_length=200)        # 제목
    content = models.TextField()                    # 내용
    display_name = models.CharField(max_length=50)      # 작성자 닉네임
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
