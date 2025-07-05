from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Citizen, Department, Complaint, ComplaintLog, Feedback


class CitizenRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    contact_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'pattern': '[0-9]{10}', 'title': 'Enter 10 digit phone number'})
    )
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    gender = forms.ChoiceField(choices=Citizen.GENDER_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            citizen = Citizen.objects.create(
                user=user,
                contact_number=self.cleaned_data['contact_number'],
                address=self.cleaned_data['address'],
                gender=self.cleaned_data['gender']
            )
        return user


class DepartmentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = Department
        fields = ['name', 'contact_person', 'contact_number', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        department = super().save(commit=False)

        if commit:
            # Create user account for department
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password1']
            )
            department.user = user
            department.save()
        return department


# class ComplaintForm(forms.ModelForm):
#     class Meta:
#         model = Complaint
#         fields = ['description']
#         widgets = {
#             'description': forms.Textarea(attrs={
#                 'rows': 5,
#                 'placeholder': 'Describe your complaint in detail...',
#                 'class': 'form-control'
#             })
#         }


# class ComplaintForm(forms.ModelForm):
#     images = forms.ImageField(
#         required=False,
#         widget=forms.ClearableFileInput(attrs={
#             'multiple': True,
#             'accept': 'image/*',
#             'class': 'form-control'
#         }),
#         help_text='Upload up to 5 images (max 5MB each)'
#     )
#
#     class Meta:
#         model = Complaint
#         fields = ['description', 'images']
#         widgets = {
#             'description': forms.Textarea(attrs={
#                 'rows': 5,
#                 'placeholder': 'Describe your complaint in detail...',
#                 'class': 'form-control'
#             })
#         }
#
#     def clean_images(self):
#         images = self.files.getlist('images')
#         if len(images) > 5:
#             raise forms.ValidationError('You can upload maximum 5 images.')
#
#         for image in images:
#             if image.size > 5 * 1024 * 1024:  # 5MB
#                 raise forms.ValidationError(f'Image {image.name} exceeds 5MB limit.')
#
#         return images


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['description', 'images']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe your complaint in detail...',
                'class': 'form-control'
            }),
            'images': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            })
        }

    def clean_images(self):
        image = self.cleaned_data.get('images')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Image size cannot exceed 5MB.')
        return image
class ComplaintLogForm(forms.ModelForm):
    class Meta:
        model = ComplaintLog
        fields = ['status', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        }
