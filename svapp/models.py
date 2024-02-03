from django.db import models


class Room(models.Model):
    room_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.room_number


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    phone = models.BigIntegerField(null=True)
    aadhar = models.BigIntegerField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    checkin_datetime = models.DateTimeField(null=True)  
    checkout_datetime = models.DateTimeField(null=True)

   
    def __str__(self):
        return f"Booking for {self.room.room_number}"