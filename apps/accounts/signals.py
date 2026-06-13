from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for new users."""
    if created and not instance.username:
        instance.username = instance.email
        instance.save(update_fields=["username"])
