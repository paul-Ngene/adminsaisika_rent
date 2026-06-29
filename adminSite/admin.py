from django.contrib import admin # type: ignore
from .models import User_info, Device

admin.site.register(User_info)

admin.site.register(Device)
