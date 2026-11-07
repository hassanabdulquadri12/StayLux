from django.conf import settings


def hotel_contact(request):
    return {
        'hotel_name': settings.HOTEL_NAME,
        'hotel_phone': settings.HOTEL_PHONE,
        'hotel_whatsapp': settings.HOTEL_WHATSAPP,
        'hotel_email': settings.HOTEL_EMAIL,
        'hotel_address': settings.HOTEL_ADDRESS,
    }