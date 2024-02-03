from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking
from datetime import date
from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet



def room_list(request):
    rooms = Room.objects.all()
    today = date.today()
    for room in rooms:
        bookings = Booking.objects.filter(room=room, checkout_date__gte=today)
        if bookings.exists():
            room.is_available = False
            room.booking = bookings.first()
        else:
            room.is_available = True
            room.booking = None
    return render(request, 'room_list.html', {'rooms': rooms, 'today': today})



def book_room(request, room_id):
    if request.method == 'POST':
        room = Room.objects.get(id=room_id)
        checkin_date = request.POST.get('checkin_date')
        checkout_date = request.POST.get('checkout_date')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        aadhar = request.POST.get('aadhar')
        price = request.POST.get('price')

        booking = Booking.objects.create(
            room=room,
            name=name,
            address=address,
            phone=phone,
            aadhar=aadhar,
            price=price,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )

        room.is_available = False
        room.save()
        return redirect('room_list')
    else:
        room = Room.objects.get(id=room_id)
        return render(request, 'book_room.html', {'room': room})

def edit_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    if request.method == 'POST':
        booking.checkin_date = request.POST.get('checkin_date')
        booking.checkout_date = request.POST.get('checkout_date')
        booking.name = request.POST.get('name')
        booking.address = request.POST.get('address')
        booking.phone = request.POST.get('phone')
        booking.aadhar = request.POST.get('aadhar')
        booking.price = request.POST.get('price')

        booking.save()
        return redirect('room_list')
    else:
        return render(request, 'edit_booking.html', {'booking': booking})

def delete_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    room = booking.room
    room.is_available = True
    room.save()
    booking.delete()
    return redirect('room_list')



def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    price = booking.price
    gst = price * Decimal('0.18')
    total_price = price + gst

    return render(request, 'booking_detail.html', {'booking': booking, 'price': price, 'gst': gst, 'total_price': total_price})


def booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'booking_list.html', {'bookings': bookings})

def generate_pdf(request):
    bookings = Booking.objects.all()  # You may need to filter bookings as per your requirements
    buffer = BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define data for the table
    data = [['Name', 'Address', 'Phone', 'Aadhar', 'Price', 'gst', 'total_price']]

    for booking in bookings:
        price = booking.price
        gst = price * Decimal('0.18')
        total_price = price + gst

        data.append([
            booking.name,
            booking.address,
            booking.phone,
            booking.aadhar,
            price,
            gst,
            total_price
            
        ])

    # Create the table
    table = Table(data)

    # Add style to table
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)

    # Create the HTTP response with PDF mime type
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="booking_list.pdf"'

    return response

def generate_bill(request, booking_id):
    # Retrieve booking object
    booking = get_object_or_404(Booking, id=booking_id)

    # Calculate GST and total price
    price = booking.price
    gst = price * Decimal('0.18')
    total_price = price + gst

    # Create a buffer for the PDF
    buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles for the document
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    # Add title to the bill
    elements.append(Paragraph("Booking Bill", styles["Title"]))
    elements.append(Paragraph("<br/><br/>", normal_style))  # Add some space

    # Create data for the table
    data = [
        ["Booking ID", str(booking.id)],
        ["Name", booking.name],
        ["Address", booking.address],
        ["Phone", booking.phone],
        ["Aadhar", booking.aadhar],
        ["Price", str(price)],
        ["GST", str(gst)],
        ["Total Price", str(total_price)],
        ["Check-in Date", str(booking.checkin_date)],
        ["Check-out Date", str(booking.checkout_date)],
    ]

    # Create the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Build the PDF
    doc.build(elements)

    # Return the buffer content as HTTP response
    pdf = buffer.getvalue()
    buffer.close()

    # Create HTTP response with PDF content
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking_bill_{booking.id}.pdf"'
    return response
