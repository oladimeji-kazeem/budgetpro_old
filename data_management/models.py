from django.db import models
from django.conf import settings

class UploadHistory(models.Model):
    file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )
    record_count = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='Completed')
    
    class Meta:
        verbose_name = "Upload History"
        verbose_name_plural = "Upload History"
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.file_name} by {self.uploaded_by}"