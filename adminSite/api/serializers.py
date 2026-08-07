from rest_framework import serializers
from adminSite.models import Device

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['name', 'serial_number', 'device_model',]