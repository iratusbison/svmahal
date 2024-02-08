import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Booking
from datetime import datetime, timedelta

from django.db.models import Sum


from decimal import Decimal
from reportlab.lib.pagesizes import letter, A4
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from django.utils import timezone

from django.utils.timezone import make_aware


def add_room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')


        # Create a new Room object and save it to the database
        Room.objects.create(
            room_number=room_number,

        )

        # Redirect to the room list page after adding the room
        return redirect('room_list')  # Assuming you have a URL named 'room_list'


    return render(request, 'room_add.html')



def room_list(request):
    rooms = Room.objects.all()
    now = timezone.now()
    for room in rooms:
        bookings = Booking.objects.filter(rooms=room, checkout_datetime__gte=now)
        if bookings.exists():
            room.is_available = False
            room.booking = bookings.first()
        else:
            room.is_available = True
            room.booking = None
    return render(request, 'room_list.html', {'rooms': rooms, 'now': now})




from django.core.exceptions import ValidationError

def book_room(request):
    rooms = Room.objects.all()

    if request.method == 'POST':
        room_ids = request.POST.getlist('rooms')  # Get selected room IDs from the form
        checkin_datetime = request.POST.get('checkin_datetime')
        checkout_datetime = request.POST.get('checkout_datetime')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        aadhar = request.POST.get('aadhar')
        price = request.POST.get('price')

        # Validate if the end date is not earlier than the start date
        if checkout_datetime <= checkin_datetime:
            error_message = 'Invalid date range'
            return render(request, 'book_room.html', {'rooms': rooms, 'error': error_message})

        # Initialize booking_id
        booking_id = None

        # Iterate through selected rooms and perform booking validation
        for room_id in room_ids:
            room = Room.objects.get(id=room_id)

            # Check if the room is already booked for the given date range
            existing_bookings = Booking.objects.filter(rooms=room, checkout_datetime__gte=checkin_datetime, checkin_datetime__lte=checkout_datetime)
            if existing_bookings.exists():
                error_message = f'Room {room.room_number} is already booked for the selected date range'
                return render(request, 'book_room.html', {'rooms': rooms, 'error': error_message})

            # Create a new booking for each selected room
            try:
                booking = Booking.objects.create(
                    name=name,
                    address=address,
                    phone=phone,
                    aadhar=aadhar,
                    price=price,
                    checkin_datetime=checkin_datetime,
                    checkout_datetime=checkout_datetime
                )
                booking.rooms.add(room)  # Add the room to the booking

                # Set the room's availability to False
                room.is_available = False
                room.save()

                # Assign the booking_id
                booking_id = booking.id

            except ValidationError as e:
                error_message = str(e)
                return render(request, 'book_room.html', {'rooms': rooms, 'error': error_message})

        # Redirect to booking_detail with the obtained booking_id
        return redirect('booking_detail', booking_id=booking_id)

    else:
        return render(request, 'book_room.html', {'rooms': rooms})


def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    price = booking.price
    gst = price * Decimal('0.12')
    total_price = price + gst

    return render(request, 'booking_detail.html', {'booking': booking, 'price': price, 'gst': gst, 'total_price': total_price})

def edit_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    if request.method == 'POST':
        booking.checkin_datetime = request.POST.get('checkin_datetime')
        booking.checkout_datetime = request.POST.get('checkout_datetime')
        booking.name = request.POST.get('name')
        booking.address = request.POST.get('address')
        booking.phone = request.POST.get('phone')
        booking.aadhar = request.POST.get('aadhar')
        booking.price = request.POST.get('price')

        booking.save()
        return redirect('booking_detail', booking_id=booking_id)
    else:
        return render(request, 'edit_booking.html', {'booking': booking})


def delete_booking(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    room = booking.room
    room.is_available = True
    room.save()
    booking.delete()
    return redirect('room_list')





from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from io import BytesIO
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware
from .models import Booking
from decimal import Decimal

def generate_pdf(request):
    # Check if a date range is provided in the request
    checkin_datetime = request.GET.get('checkin_datetime', '')
    checkout_datetime = request.GET.get('checkout_datetime', '')

    # Default to the last 30 days if no date range is provided
    if not checkin_datetime or not checkout_datetime:
        checkout_datetime = timezone.now()
        checkin_datetime = checkout_datetime - timedelta(days=30)
    else:
        checkin_datetime = make_aware(datetime.strptime(checkin_datetime, '%Y-%m-%d'))
        checkout_datetime = make_aware(datetime.strptime(checkout_datetime, '%Y-%m-%d'))

    # Filter bookings based on the provided date range
    bookings = Booking.objects.filter(checkin_datetime__range=(checkin_datetime, checkout_datetime))

    buffer = BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    # Add title to the PDF
    title_text = f"Booking List ({checkin_datetime.date()} to {checkout_datetime.date()})"
    elements.append(Paragraph(title_text, styles["Title"]))
    elements.append(Paragraph("<br/><br/>", normal_style))  # Add some space

    # Define data for the table
    data = [['ID','Name', 'Phone', 'Aadhar', 'Price', 'GST', 'Total Price', 'Rooms']]

    total_revenue = Decimal('0.00')

    for booking in bookings:
        # Calculate GST and total price
        price = booking.price
        gst = price * Decimal('0.12')
        total_price = price + gst

        # Collect room details for the booking
        room_details = ", ".join([room.room_number for room in booking.rooms.all()])

        # Append booking details to the data list
        data.append([
            booking.id,
            booking.name,

            booking.phone,
            booking.aadhar,
            price,
            gst,
            total_price,

            room_details,
        ])

        # Increment total revenue
        total_revenue += price

    # Add row for total revenue
    data.append(['', '', '', '', '', '', f'Total Revenue: {total_revenue}', '', '', ''])

    # Create the table
    table = Table(data)

    # Define style for the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    # Apply style to the table
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
    gst = price * Decimal('0.12')
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
    elements.append(Paragraph("SV Mahal", styles["Title"]))
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
        ["Check-in Date", str(booking.checkin_datetime)],
        ["Check-out Date", str(booking.checkout_datetime)],
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

from django.utils.timezone import make_aware

def booking_list(request):
    # Check if a date range is provided in the request
    checkin_datetime = request.GET.get('checkin_datetime', '')
    checkout_datetime = request.GET.get('checkout_datetime', '')

    # Default to the last 30 days if no date range is provided
    if not checkin_datetime or not checkout_datetime:
        checkout_datetime = datetime.now()
        checkin_datetime = checkout_datetime - timedelta(days=30)
    else:
        checkin_datetime = make_aware(datetime.strptime(checkin_datetime, '%Y-%m-%d'))
        checkout_datetime = make_aware(datetime.strptime(checkout_datetime, '%Y-%m-%d'))

    bookings = Booking.objects.filter(checkin_datetime__range=(checkin_datetime, checkout_datetime))

    # Calculate total revenue for the given date range
    total_revenue = bookings.aggregate(Sum('price'))['price__sum']

    # Prepare a list to hold each booking along with its details
    bookings_with_details = []

    for booking in bookings:
        # Calculate GST for the booking
        price = float(booking.price)
        gst = price * 0.12

        # Collect room details for the booking
        room_details = ", ".join([room.room_number for room in booking.rooms.all()])

        # Construct a dictionary with booking details
        booking_details = {
            'booking': booking,
            'checkin_datetime': booking.checkin_datetime,
            'checkout_datetime': booking.checkout_datetime,
            'price': price,
            'gst': gst,
            'total_price': price + gst,
            'rooms': room_details,
        }

        bookings_with_details.append(booking_details)

    return render(request, 'booking_list.html', {
        'bookings': bookings_with_details,
        'checkin_datetime': checkin_datetime,
        'checkout_datetime': checkout_datetime,
        'total_revenue': total_revenue,
    })
