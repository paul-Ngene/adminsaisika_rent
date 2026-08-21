import uuid
from django.db import models # type: ignore
from django.contrib.auth.hashers import make_password , check_password # type: ignore
from django.contrib.auth.models import AbstractUser # type: ignore
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

#using built_in django auth
User = get_user_model()

class User_info(models.Model):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        CUSTOMER = "CUSTOMER", "Customer"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    username1 = models.CharField(max_length=150, unique=True, blank=True, null=True)

    # email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)

    nin = models.CharField(max_length=20, unique=True,  blank=True, null=True)

    gender = models.CharField(max_length=20, blank=True)

    birthdate = models.CharField(max_length=30, blank=True)

    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)


    def __str__(self):
        return self.user.username

class Device(models.Model):

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        ACTIVE = "ACTIVE", "Active"
        LOCKED = "LOCKED", "Locked"
        DISABLED = "DISABLED", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)

    serial_number = models.CharField(max_length=255, unique=True)

    device_model = models.CharField(max_length=255)

    #firmware_version = models.CharField( max_length=100)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)

    current_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="devices")

    # For days
    # assigned_date = models.DateField(null=True, blank=True)

    # due_date = models.DateField(null=True, blank=True)


    # for Hours
    assigned_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.serial_number}"

# class Payment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="payments")

#     amount = models.DecimalField( max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

#     payment_date = models.DateTimeField(auto_now_add=True)

#     reference = models.CharField( max_length=100,unique=True,null=True,blank=True)

#     description = models.CharField(max_length=255,blank=True)

#     def __str__(self):
#         return f"{self.user} - ₦{self.amount}"