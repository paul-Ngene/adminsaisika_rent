from django.shortcuts import render, redirect # type: ignore
from django.http import HttpResponse # type: ignore
# from .forms import UserForm
from django.contrib.auth.models import User, auth

import json
from django.contrib import messages
from django.db import transaction, DatabaseError
from .forms import UserRegistrationForm
from .models import User_info


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)
from datetime import timedelta, date
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from .models import Device, User_info
from django.db.models import Q

from itertools import chain

User = get_user_model()

# Add a view that deletes all devices not assigned to any device and who hasnt patronised us in a long while
# Create your views here.
def main(request):
    pass

def index(request):
    return render(request, 'new sasika site.html')

@login_required(login_url='login')
def userInfo(request, pk):
    # users = User_info.objects.get(id = pk)
    users = User_info.objects.select_related('user').prefetch_related('user__devices')
    user = get_object_or_404(users, id=pk) 
    context = {
        'users': user,
    }
    return render(request, 'user-info.html', context)

@login_required(login_url='login')
def userList(request):
    # user = User.objects.all()
    # device = Device.objects.all()
    # users = User_info.objects.select_related('user').all()
    # # for user in users:
    # #     device.append(Device.objects.get(current_user=user))

    # # devicelist = list(chain(*device))
    
    # context = {
    #     'users': user,
    #     'device': device,
    #     'user_info': users,
    # }

    # device_context = {
    #     'devicelist': devicelist,
    #}
    if request.method == "POST":
        user_search = request.POST.get("user_search")

        # 1. Look up the device by Name or Serial Number
        users = User_info.objects.select_related('user').prefetch_related('user__devices').filter(
            Q(phone=user_search)
        ).filter()

        if not users.exists():
            messages.error(request, f" '{user_search}' not found.")
           
    else:

        users = User_info.objects.select_related('user').prefetch_related('user__devices')

    context = {
        'users': users,
    }

    return render(request, 'user display1.html', context)

@login_required(login_url='login')
def deviceList(request):
    devices = Device.objects.all()


    today = date.today()

    due_devices = Device.objects.filter(
        due_date__lt=today,
        status="ACTIVE"
    )
    context = {
        "devices": devices,
        "due_devices": due_devices,
    }
    return render(request, 'device display1.html', context)

@login_required(login_url='login')
def assign_device_with_id(request,pk):
    users = User_info.objects.select_related('user').prefetch_related('user__devices')
    user = get_object_or_404(users, id=pk)

    devices = Device.objects.filter(status="AVAILABLE")

    if request.method == "POST":
        device_id = request.POST.get("device_id")
        device = get_object_or_404(Device, id=device_id)

        device.current_user = user.user
        device.status = "ACTIVE"
        device.assigned_at = timezone.now()
        device.due_date = timezone.now() + timedelta(hours=24)
        device.save()

        messages.success(request, "Device assigned successfully")
        return redirect(request.META.get('HTTP_REFERER'))
    context = {
        'users': user,
        'devices': devices,
        'now': timezone.now(),  # needed for due check
    }

    return render(request, 'assign_device_with_id.html', context)
    # users = User_info.objects.get(id = pk)
    # users = User_info.objects.select_related('user').prefetch_related('user__devices')
    # user = get_object_or_404(users, id=pk)
    
    # device = Device.objects.filter(status="AVAILABLE")

    # assign device
    # device.current_user = user.user
    # device.status = "ACTIVE"
    #  For days
    # device.assigned_date = date.today()
    # device.due_date = date.today() + timedelta(days=1)  # 30 days plan but i set it to 1
    # device.assigned_at = timezone.now()
    # device.due_date = timezone.now() + timedelta(hours=24)  # 24 hours
    # device.save()

    # messages.success(request, "Device assigned successfully")
    #return redirect("users")
    # context = {
    #     'users': user,
    # }
    # return render(request, 'assign_device_with_id.html', context) 

@login_required(login_url='login')
def assign_device(request):
    users = User.objects.all()
    devices = Device.objects.filter(status="AVAILABLE")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        device_id = request.POST.get("device_id")

        user = get_object_or_404(User, id=user_id)
        device = get_object_or_404(Device, id=device_id)

        # assign device
        device.current_user = user
        device.status = "ACTIVE"
        #  For days
        # device.assigned_date = date.today()
        # device.due_date = date.today() + timedelta(days=1)  # 30 days plan but i set it to 1
        device.assigned_at = timezone.now()
        device.due_date = timezone.now() + timedelta(hours=24)  # 24 hours
        device.save()

        messages.success(request, "Device assigned successfully")
        return redirect("users")

    context = {
        "users": users,
        "devices": devices,
    }

    return render(request, "assign_device.html", context)

@login_required(login_url='login')
def rent_device_flow(request):
    if request.method == "POST":
        device_search = request.POST.get("device_search")
        user_search = request.POST.get("user_search")

        # 1. Look up the device by Name or Serial Number
        device = Device.objects.filter(
            Q(serial_number=device_search) | Q(name__icontains=device_search)
        ).first()

        if not device:
            messages.error(request, f"Device matching '{device_search}' not found.")
            return render(request, 'rent_device_flow.html', {"device_search": device_search, "user_search": user_search})

        if device.status != "AVAILABLE":
            messages.error(request, f"Device '{device.name}' is currently {device.status} and cannot be rented.")
            return render(request, 'rent_device_flow.html', {"device_search": device_search, "user_search": user_search})

        # 2. Look up the user using Phone or NIN from the User_info profile
        user_info = User_info.objects.filter(
            Q(phone=user_search) | Q(nin=user_search)
        ).select_related('user').first()

        # If user does not exist in the system, redirect to the registration page
        if not user_info:
            messages.info(request, f"No user found with Phone/NIN: '{user_search}'. Please register them first.")
            return redirect('register1')

        # 3. Process the Rental Assignment
        device.current_user = user_info.user
        device.status = "ACTIVE"
        device.assigned_at = timezone.now()
        device.due_date = timezone.now() + timedelta(hours=24) # 24-hour rental window
        device.save()

        messages.success(request, f"Successfully rented '{device.name}' to {user_info.user.username}!")
        return redirect('users')

    return render(request, 'rent_device_flow.html')

@login_required(login_url='login')
def return_device(request, pk):
    device = get_object_or_404(Device, id=pk)
    device.status = "AVAILABLE"
    device.current_user = None
    device.assigned_at = None
    device.due_date = None
    device.save()

    messages.success(request, "Device returned successfully")
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
def update_device(request, pk):
    pass

@login_required(login_url='login')
def add_device(request):
    if request.method == "POST":
        name = request.POST.get("name")
        serial_number = request.POST.get("serial_number")
        device_model = request.POST.get("device_model")

        # prevent duplicate serial number
        if Device.objects.filter(serial_number=serial_number).exists():
            messages.error(request, "Device with this serial number already exists")
            return redirect("add_device")

        Device.objects.create(
            name=name,
            serial_number=serial_number,
            device_model=device_model,
            status="AVAILABLE"
        )

        messages.success(request, "Device added to stock successfully")
        return redirect("devices")

    return render(request, "add_device.html")

@login_required(login_url='login')
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                User_info.objects.create(user=user)
                # users = User_info.objects.select_related('user').prefetch_related('user__devices')
                # user = get_object_or_404(users, id=pk) 
                #log user in and redirect to settings page
                # user_login = auth.authenticate(username=username, password=password)
                # auth.login(request, user_login)
                return redirect('users')

                #create a Profile object for the new user
                # user_model = User.objects.get(username=username)
                # new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                # new_profile.save()
                # return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('register')
        
    else:
        return render(request, 'register saisika.html')
    # return render(request, 'register saisika.html')


def login(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        getUser = User.objects.get(email=email)
        if not getUser:
            messages.info(request, "User not found")
            return redirect('login')
        username = getUser.username

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_staff:
            
            auth.login(request, user)
            return redirect('rent_device_flow')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')

    else:
        return render(request, 'login saisika.html')

@login_required(login_url='login')  
def logout(request):
    auth.logout(request)
    return redirect('login')



@login_required(login_url='login') 
def register1(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        # added try except and transaction atomic so as to make sure user is created together with user_info
        if form.is_valid():
            try:
                # Everything inside this block is treated as an atomic operation
                with transaction.atomic():
                # if form.is_valid():
                    # 1. Create and save primary User
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password'])
                    user.save()

                    # 2. Create User_info instance linked to the user
                    User_info.objects.create(
                        user=user,
                        username1=user.username,
                        phone=form.cleaned_data.get('phone'),
                        nin=form.cleaned_data.get('nin'),
                        gender=form.cleaned_data.get('gender'),
                        birthdate=str(form.cleaned_data.get('birthdate')),
                        profile_image=form.cleaned_data.get('profile_image'),
                        role=User_info.Role.CUSTOMER
                    )

                messages.success(request, 'Account created successfully! You can now log in.')
                return redirect('rent_device_flow') # 
            except Exception as e:
                # If anything goes wrong inside the block, transaction rolls back automatically
                messages.error(request, f"An error occurred during registration: {e}")
    else:
        form = UserRegistrationForm()

    return render(request, 'register1.html', {'form': form})
# from django.core.paginator import Paginator

# devices_list = user.user.devices.all()

# # Search
# query = request.GET.get("q")
# if query:
#     devices_list = devices_list.filter(name__icontains=query)

# # Pagination
# paginator = Paginator(devices_list, 5)  # 5 per page
# page = request.GET.get("page")
# devices = paginator.get_page(page)