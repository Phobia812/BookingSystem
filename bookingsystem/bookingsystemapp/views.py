from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, time
from django.utils.dateparse import parse_date
from django.utils.timezone import localdate
from .models import Place, Booking, Type, City

def home(request):
    popular_destinations = City.objects.filter(is_popular=True)[:6]
    return render(request, 'home.html', {'popular_destinations': popular_destinations})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def profile(request):
    if not request.user.is_authenticated:
        return HttpResponse("Ви не авторизовані.")
    
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'profile.html', {'bookings': bookings})

def logout(request):
    if request.user.is_authenticated:
        from django.contrib.auth import logout as auth_logout
        auth_logout(request)
        
    return redirect('home')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def search(request):
    location = request.GET.get('location', '').strip()
    checkin_str = request.GET.get('checkin')
    checkout_str = request.GET.get('checkout')
    guests = request.GET.get('guests')

    checkin = parse_date(checkin_str) if checkin_str else None
    checkout = parse_date(checkout_str) if checkout_str else None

    results = Place.objects.none()
    query = {'location': location}

    if location:
        cities = City.objects.filter(name__icontains=location)
        if cities.exists():
            results = Place.objects.filter(
                city__in=cities,
                available=True
            )
            if guests:
                results = results.filter(capacity__gte=guests)

            if checkin and checkout:
                from datetime import datetime, time
                from django.utils.timezone import make_aware

                start_dt = make_aware(datetime.combine(checkin, time.min))
                end_dt = make_aware(datetime.combine(checkout, time.max))

                results = results.exclude(
                    booking__start_time__lt=end_dt,
                    booking__end_time__gt=start_dt,
                    booking__status__in=['pending', 'confirmed']
                )

    return render(request, 'search_results.html', {
        'results': results.distinct(),
        'query': query,
        'checkin': checkin_str,
        'checkout': checkout_str,
        'guests': guests
    })



def city_search(request, slug):
    checkin_str = request.GET.get('checkin')
    checkout_str = request.GET.get('checkout')
    guests = request.GET.get('guests')

    checkin = parse_date(checkin_str) if checkin_str else None
    checkout = parse_date(checkout_str) if checkout_str else None

    city = get_object_or_404(City, slug=slug)
    results = Place.objects.filter(city=city, available=True)

    if guests:
        results = results.filter(capacity__gte=guests)

    if checkin and checkout:
        results = results.exclude(
            booking__start_time__lt=checkout,
            booking__end_time__gt=checkin
        )

    return render(request, 'search_results.html', {
        'results': results.distinct(),
        'query': {'location': city.name},
        'checkin': checkin_str,
        'checkout': checkout_str,
        'guests': guests
    })

def details(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    success = False
    errors = []

    if request.method == "POST":
        if not request.user.is_authenticated:
            errors.append("Ви не авторизовані. Будь ласка, увійдіть.")
        else:
            start_date_str = request.POST.get("start_date")
            end_date_str = request.POST.get("end_date")

            if not start_date_str or not end_date_str:
                errors.append("Вкажіть дату початку і кінця бронювання.")

            if not errors:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                except ValueError:
                    errors.append("Невірний формат дати.")

            if not errors:
                if end_date < start_date:
                    errors.append("Дата кінця не може бути раніше дати початку.")
                if start_date < timezone.localdate():
                    errors.append("Дата початку не може бути в минулому.")

            if not errors:
                start_dt = timezone.make_aware(datetime.combine(start_date, time(hour=12, minute=0)))
                end_dt = timezone.make_aware(datetime.combine(end_date, time(hour=12, minute=0)))

                conflict = Booking.objects.filter(
                    place=place,
                    status__in=['pending', 'confirmed'],
                    start_time__lt=end_dt,
                    end_time__gt=start_dt
                ).exists()

                if conflict:
                    errors.append("На обраний період вже існує бронювання. Будь ласка, оберіть інший час.")

            if not errors:
                Booking.objects.create(
                    place=place,
                    user=request.user,
                    start_time=start_dt,
                    end_time=end_dt,
                    status='pending'
                )
                success = True

    today = localdate()

    return render(request, "details.html", {
        "place": place,
        "success": success,
        "errors": errors,
        "today": today.isoformat(),
    })
