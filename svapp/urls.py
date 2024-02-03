from django.urls import path
from .views import room_list, book_room, edit_booking, delete_booking, generate_pdf, booking_detail, booking_list, generate_bill, total_revenue

urlpatterns = [
    path('', room_list, name='room_list'),
    path('book-room/<int:room_id>/', book_room, name='book_room'),
    path('edit-booking/<int:booking_id>/', edit_booking, name='edit_booking'),
    path('delete-booking/<int:booking_id>/', delete_booking, name='delete_booking'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('booking_detail/<int:booking_id>/', booking_detail, name='booking_detail'),
    path('booking_list/', booking_list, name='booking_list'),
    path('generate_bill/<int:booking_id>/', generate_bill, name='generate_bill'),
    path('total/', total_revenue, name= 'total_revenue'),

]
