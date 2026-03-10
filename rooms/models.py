from django.db import models
import uuid

class Room(models.Model):
    name = models.CharField(max_length=200)
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    host_name = models.CharField(max_length=100, default='Host')

    def __str__(self):
        return f"{self.name} ({self.code})"
