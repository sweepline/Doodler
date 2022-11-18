import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Doodle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=190)
    data = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=timezone.now)

    def owner_link(self):
        return reverse("owner", kwargs={"doodle": self.id}) + f"?secretOwnerPassword={self.data.get('owner_password')}"
