from django.db import models


class Room(models.Model):

    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=100)
    description = models.TextField()

    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    available_rooms = models.PositiveIntegerField(default=1)
    max_guests = models.PositiveBigIntegerField(default=2)

    image = models.ImageField(
        upload_to='rooms/',
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Booking(models.Model):

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)

    check_in = models.DateField()
    check_out = models.DateField()

    number_of_guests = models.PositiveIntegerField(default=1)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def number_of_nights(self):
        return (self.check_out - self.check_in).days

    def __str__(self):
        return f"{self.guest_name} - {self.room.name}"