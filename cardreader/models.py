import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model
from rest_framework_api_key.models import APIKey
from skimage.color.rgb_colors import black


class User(AbstractUser):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class IdCard(Model):
    imageFront = models.FileField(upload_to='cards/')
    imageBack = models.FileField(upload_to='cards/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    sex = models.CharField(
        choices=(('male', 'Male'), ('female', 'Female')),
        max_length=120
    )
    nationality = models.CharField(max_length=120)
    expiryDate = models.DateField(null=True, blank=True)
    birthDate = models.DateField(null=True, blank=True)
    identifier = models.CharField(max_length=120)
    can = models.CharField(max_length=120)
    mothersName = models.CharField(max_length=120)
    birthPlace = models.CharField(max_length=120, null=True, blank=True)

    def delete(self, *args, **kwargs):
        # Delete the image files associated with this card
        if self.imageFront and os.path.isfile(self.imageFront.path):
            os.remove(self.imageFront.path)
        if self.imageBack and os.path.isfile(self.imageBack.path):
            os.remove(self.imageBack.path)
        super().delete(*args, **kwargs)


class StudentCard(Model):
    imageFront = models.FileField(upload_to='cards/')
    imageBack = models.FileField(upload_to='cards/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    cardNumber = models.CharField(max_length=120)
    expiryDate = models.DateField(null=True, blank=True)
    issueDate = models.DateField(null=True, blank=True)
    birthDate = models.DateField(null=True, blank=True)
    OMNUmber = models.CharField(max_length=120)
    school = models.CharField(max_length=120)
    address = models.CharField(max_length=120)
    placeOfBirth = models.CharField(max_length=120, null=True, blank=True)

    def delete(self, *args, **kwargs):
        # Delete the image files associated with this card
        if self.imageFront and os.path.isfile(self.imageFront.path):
            os.remove(self.imageFront.path)
        if self.imageBack and os.path.isfile(self.imageBack.path):
            os.remove(self.imageBack.path)
        super().delete(*args, **kwargs)


class HealthCareCard(Model):
    imageFront = models.FileField(upload_to='cards/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    birthDate = models.DateField(null=True, blank=True)
    issueDate = models.DateField(null=True, blank=True)
    cardNumber = models.CharField(max_length=120)

    def delete(self, *args, **kwargs):
        # Delete the image files associated with this card
        if self.imageFront and os.path.isfile(self.imageFront.path):
            os.remove(self.imageFront.path)
        super().delete(*args, **kwargs)



class Group(models.Model):
    users = models.ManyToManyField(User)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    name = models.CharField(max_length=120)
    createdAt = models.DateTimeField(auto_now_add=True)
    idCards = models.ManyToManyField(IdCard, blank=True)
    healthCareCards = models.ManyToManyField(HealthCareCard, blank=True)
    studentCards = models.ManyToManyField(StudentCard, blank=True)

class Invitation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations_received')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')),
        default='pending'
    )



class Company(models.Model):
    name = models.CharField(max_length=120)
    vatNumber = models.CharField(max_length=120)
    contactEmail = models.CharField(max_length=120)
    apiKey = models.OneToOneField(APIKey, on_delete=models.CASCADE, null=True, blank=True)
    owedMoney = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)



