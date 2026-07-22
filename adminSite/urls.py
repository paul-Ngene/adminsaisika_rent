from django.urls import path # type: ignore
from . import views

urlpatterns = [
    # path('',views.main, name = 'main'),
    path('index',views.index, name = 'index'),
    path('user-info/<str:pk>',views.userInfo, name = 'user-info'),
    path('devices',views.deviceList, name = 'devices'),
    path('users',views.userList, name = 'users'),
    path('login',views.login, name = 'login'),
    path('logout',views.logout, name = 'logout'),
    path('register',views.register, name = 'register'),
    path('assign-device/', views.assign_device, name='assign_device'),
    path('return_device/<str:pk>', views.return_device, name='return_device'),
    path('update_device/<str:pk>', views.update_device, name='update_device'),
    path('assign-device/<str:pk>', views.assign_device_with_id, name='assign_device_with_id'),
    path('add-device/', views.add_device, name='add_device'),
    path('rent-devices/', views.rent_device_flow, name='rent_device_flow'),
]
