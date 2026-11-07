from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q, F, Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

from .models import Room, Booking
from .forms import BookingForm, RoomForm


def home(request):
    rooms = Room.objects.filter(is_available=True)

    guests = request.GET.get('guests')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    if guests:
        try:
            guests = int(guests)

            if guests < 1:
                guests = None
            else:
                rooms = rooms.filter(max_guests__gte=guests)

        except ValueError:
            guests = None

    if check_in and check_out:
        try:
            start = datetime.strptime(check_in, '%Y-%m-%d').date()
            end = datetime.strptime(check_out, '%Y-%m-%d').date()

            if end > start:
                rooms = rooms.annotate(
                    overlapping_bookings=Count(
                        'bookings',
                        filter=Q(
                            bookings__check_in__lt=end,
                            bookings__check_out__gt=start
                        ) & ~Q(bookings__status='Cancelled')
                    )
                ).filter(
                    overlapping_bookings__lt=F('available_rooms')
                )

        except ValueError:
            pass

    return render(request, 'hotels/home.html', {
        'rooms': rooms,
        'guests': guests,
        'check_in': check_in,
        'check_out': check_out,
    })


def book_room(request, room_id):
    room = get_object_or_404(
        Room,
        id=room_id,
        is_available=True
    )

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.room = room

            check_in = booking.check_in
            check_out = booking.check_out
            guests = booking.number_of_guests

            if check_in < timezone.localdate():
                form.add_error(
                    'check_in',
                    'Check-in cannot be in the past.'
                )

            elif check_out <= check_in:
                form.add_error(
                    'check_out',
                    'Check-out must be after check-in.'
                )

            elif guests > room.max_guests:
                form.add_error(
                    'number_of_guests',
                    'This room cannot accommodate that many guests.'
                )

            else:
                overlapping = Booking.objects.filter(
                    room=room,
                    check_in__lt=check_out,
                    check_out__gt=check_in
                ).exclude(status='Cancelled').count()

                if overlapping >= room.available_rooms:
                    form.add_error(
                        None,
                        'Sorry, this room is not available for those dates.'
                    )

                else:
                    nights = (check_out - check_in).days

                    booking.total_price = (
                        room.price_per_night * nights
                    )

                    booking.save()

                    send_mail(
    subject=f'Booking Received - {settings.HOTEL_NAME}',
    message=(
        f'Hello {booking.guest_name},\n\n'
        f'We have received your booking request.\n\n'
        f'Room: {room.name}\n'
        f'Check-in: {booking.check_in}\n'
        f'Check-out: {booking.check_out}\n'
        f'Total price: ₦{booking.total_price}\n\n'
        'Your booking is awaiting hotel approval.\n'
        'No payment has been collected.\n\n'
        f'Thank you for choosing {settings.HOTEL_NAME}.'
    ),
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[booking.guest_email],
    fail_silently=True,
)

                    messages.success(
                        request,
                        'Your booking has been submitted successfully!'
                    )

                    return render(
                        request,
                        'hotels/confirmation.html',
                        {'booking': booking}
                    )

    else:
        form = BookingForm()

    return render(request, 'hotels/booking.html', {
        'form': form,
        'room': room
    })


@staff_member_required(login_url='/admin/login/')
def dashboard(request):

    total_rooms = Room.objects.count()
    rooms = Room.objects.all().order_by('-created_at')

    available_rooms = Room.objects.filter(
        is_available=True
    ).count()

    total_bookings = Booking.objects.count()

    total_revenue = Booking.objects.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    status_filter = request.GET.get('status')

    recent_bookings = Booking.objects.all()

    if status_filter in ['Pending', 'Approved', 'Cancelled']:
        recent_bookings = recent_bookings.filter(
            status=status_filter
        )

    recent_bookings = recent_bookings.order_by(
        '-created_at'
    )[:10]

    return render(request, 'hotels/dashboard.html', {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'status_filter': status_filter,
        'rooms': rooms
    })

@staff_member_required(login_url='/admin/login/')
def update_booking_status(request, booking_id):

    @staff_member_required(login_url='/admin/login/')
    @require_POST
    def update_booking_status(request, booking_id):

     if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)

        new_status = request.POST.get('status')

        if new_status in ['Approved', 'Cancelled', 'Pending']:
            booking.status = new_status
            booking.save()

            messages.success(
                request,
                f'Booking status updated to {new_status}.'
            )

    return redirect('dashboard')

@staff_member_required(login_url='/admin/login/')
def add_room(request):

    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()

            messages.success(request, 'Room added successfully!')
            return redirect('dashboard')

    else:
        form = RoomForm()

    return render(request, 'hotels/room_form.html', {
        'form': form,
        'title': 'Add New Room'
    })


@staff_member_required(login_url='/admin/login/')
def edit_room(request, room_id):

    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = RoomForm(
            request.POST,
            request.FILES,
            instance=room
        )

        if form.is_valid():
            form.save()

            messages.success(request, 'Room updated successfully!')
            return redirect('dashboard')

    else:
        form = RoomForm(instance=room)

    return render(request, 'hotels/room_form.html', {
        'form': form,
        'title': 'Edit Room'
    })


@staff_member_required(login_url='/admin/login/')
def delete_room(request, room_id):

    @staff_member_required(login_url='/admin/login/')
    @require_POST
    def delete_room(request, room_id):

     if request.method == 'POST':
        room = get_object_or_404(Room, id=room_id)

        if room.bookings.exists():
            messages.error(
                request,
                'This room has bookings and cannot be deleted.'
            )
        else:
            room.delete()
            messages.success(request, 'Room deleted successfully!')

    return redirect('dashboard')