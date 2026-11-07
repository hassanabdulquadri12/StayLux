from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/booking/<int:booking_id>/update/', views.update_booking_status, name='update_booking_status'),
    path('dashboard/rooms/add/', views.add_room, name='add_room'),

path('dashboard/rooms/<int:room_id>/edit/', views.edit_room, name='edit_room'),

path('dashboard/rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),
]