from django.db import models
from django.conf import settings

class Qna(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_qnas',
        on_delete=models.CASCADE
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_qnas',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    qna = models.ForeignKey(Qna, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    display_name = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,    
        blank=True      
    )
    created_at = models.DateTimeField(auto_now_add=True)

