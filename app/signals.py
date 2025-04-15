from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from social_django.models import UserSocialAuth
@receiver(post_save,sender=CustomUser)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        ProfileUser.objects.create(user=instance)
