from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import Place, Booking

TEMPLATE_DIR = 'bookingsystemapp/templates/'

def home(request):
    places = Place.objects.all(available=True)
    return render(request, 'home.html', {'places': places})

def details(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    success = False
    errors = []

    if request.method == "POST":
        user_name = request.POST.get("user_name")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        if not user_name:
            errors.append("Вкажіть ваше ім'я.")
        if not start_time or not end_time:
            errors.append("Вкажіть дату та час початку і кінця бронювання.")

        if not errors:
            try:
                start_dt = timezone.datetime.fromisoformat(start_time)
                end_dt = timezone.datetime.fromisoformat(end_time)
                if start_dt >= end_dt:
                    errors.append("Час початку повинен бути раніше часу закінчення.")
                elif start_dt < timezone.now():
                    errors.append("Час початку не може бути в минулому.")
            except ValueError:
                errors.append("Невірний формат дати/часу.")

        if not errors:
            Booking.objects.create(
                place=place,
                user=None, # поки що не реалізовано авторизацію
                start_time=start_dt,
                end_time=end_dt,
                status='pending'
            )
            success = True

    return render(request, "details.html", {
        "place": place,
        "success": success,
        "errors": errors,
    })
