from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Order


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'address', 'city', 'postal_code', 'country']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Main St, Apt 4B'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mumbai'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '400001'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'India'}),
        }


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(5, '5 Stars ★★★★★'), (4, '4 Stars ★★★★☆'), (3, '3 Stars ★★★☆☆'), (2, '2 Stars ★★☆☆☆'), (1, '1 Star ★☆☆☆☆')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience with this product...'})
    )

