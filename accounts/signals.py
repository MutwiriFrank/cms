from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from .models import Customer


def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='customer')
        instance.groups.add(group)  # adding user to customer group
        Customer.objects.create(
            user=instance,
            name=instance.username
        )
        print("profile created")


post_save.connect(create_customer_profile, sender=User)
