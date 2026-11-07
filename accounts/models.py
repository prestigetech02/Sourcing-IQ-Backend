from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.



class User(AbstractUser):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('procurement', 'Procurement Officer'),
        ('finance', 'Finance Officer'),
        ('supplier', 'Supplier'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='procurement'
    )

    def __str__(self):
        return self.username
