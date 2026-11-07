from django import forms
from .models import Booking, Room


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = [
            'guest_name',
            'guest_email',
            'guest_phone',
            'check_in',
            'check_out',
            'number_of_guests',
        ]

        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room
        fields = [
            'name',
            'room_type',
            'description',
            'price_per_night',
            'available_rooms',
            'max_guests',
            'image',
            'is_available',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the room and its facilities...'
            }),
        }