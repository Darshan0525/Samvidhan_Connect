# forms.py
from django import forms
from .models import AppointmentSlot,LawyerProfile, ClientProfile

class AppointmentSlotForm(forms.ModelForm):
    class Meta:
        model = AppointmentSlot
        fields = ['specialization', 'date', 'start_time', 'end_time', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adding CSS classes to form fields in a loop
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
        # Adding a placeholder specifically for the specialization field
        self.fields['specialization'].widget.attrs['placeholder'] = 'Type specialization here'

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')

        # Ensure start time is before end time
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Start time must be before end time.")

        return cleaned_data

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = None  # Will dynamically set the model in the view
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add CSS classes to dynamically rendered fields (e.g., for any form field in profile)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class LawyerProfileForm(forms.ModelForm):
    class Meta:
        model = LawyerProfile
        fields = ['description', 'speciality', 'profile_picture', 'experience_years', 'availability']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to fields
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['speciality'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
        self.fields['experience_years'].widget.attrs.update({'class': 'form-control'})
        self.fields['availability'].widget.attrs.update({'class': 'form-control'})

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['date_of_birth', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 

        # Add CSS classes to fields
        self.fields['date_of_birth'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
