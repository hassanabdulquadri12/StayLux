from django.contrib import admin
from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'room_type',
        'price_per_night',
        'available_rooms',
        'max_guests',
        'is_available',
    )

    list_filter = ('room_type', 'is_available')
    search_fields = ('name', 'room_type')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'guest_name',
        'room',
        'check_in',
        'check_out',
        'number_of_guests',
        'total_price',
        'status',
        'created_at',
    )
    list_editable = ('status',)
    list_filter = ('check_in', 'check_out', 'created_at')
    search_fields = ('guest_name', 'guest_email', 'guest_phone')
    readonly_fields = ('total_price', 'created_at')
    ordering = ('-created_at',)