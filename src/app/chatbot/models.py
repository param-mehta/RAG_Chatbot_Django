from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_id = models.IntegerField()
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    vote = models.BooleanField(default=True)
    issue_type = models.TextField()

    def __str__(self):
        return f'{self.user.username}: {self.message}'