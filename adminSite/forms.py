from django import forms
from django.contrib.auth import get_user_model
from .models import User_info

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    # Standard User fields
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    # Extra User_info fields with Bootstrap styling
    nin = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIN Number'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    birthdate = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    def clean_nin(self):
            nin = self.cleaned_data.get('nin')
            if User_info.objects.filter(nin=nin).exists():
                raise forms.ValidationError("A profile with this NIN already exists.")
            return nin

    def clean_phone(self):
            phone = self.cleaned_data.get('phone')
            if phone and User_info.objects.filter(phone=phone).exists():
                raise forms.ValidationError("A profile with this phone number already exists.")
            return phone



    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data