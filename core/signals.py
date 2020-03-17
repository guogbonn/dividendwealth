
from django.dispatch import receiver
from django.core.signals import post_save
from .models import User_Profile
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        user_created,created=UserProfile.objects.get_or_create(user=kwargs.get('instance'))
        user_created.save()
