from django.db import models

class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Place(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=1)
    available = models.BooleanField(default=True)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='places/')

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Очікування'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Бронювання {self.place.name} від {self.start_time} до {self.end_time} для {self.user.username}"
    
