from django.forms import ModelForm
from django import forms
from .models import Contract, PetCareLog # Added PetCareLog


class ContractForm(ModelForm):
    class Meta:
        model = Contract
        fields = ['start_date', 'end_date', 'pet', 'mamma_pet', 'price', 'client']
        widgets = {
            'start_date': forms.DateInput(
                format='%m/%d/%Y',
                attrs={'class': 'datepicker', 'placeholder': 'MM/DD/YYYY'}
            ),
            'end_date': forms.DateInput(
                format='%m/%d/%Y',
                attrs={'class': 'datepicker', 'placeholder': 'MM/DD/YYYY'}
            ),
        }


class PetCareLogForm(forms.ModelForm):
    class Meta:
        model = PetCareLog
        fields = ['notes', 'photo'] # contract and date will be set in the view
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any notes about today?'}),
        }
        labels = {
            'notes': 'Daily Notes',
            'photo': 'Upload Photo'
        }