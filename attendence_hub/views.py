from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import JsonResponse,HttpResponseBadRequest
from .models import *
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import AttendanceRecord, UserProfile
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
import json

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username,password)
        
        user = authenticate(request, username=username, password=password)  #
        
        if user is not None:
            auth_login(request, user) 
            return redirect('active') 
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'login.html')


def logout(request):
    auth_logout(request) 
    return redirect('login') 


@login_required
def active(request):
    current_user = request.user
    today = timezone.now().date()

    # Check if the user has an attendance record for today
    attendance_record = AttendanceRecord.objects.filter(user=current_user, intime__date=today).first()

    # Check if the attendance status is 'P' (Present) or 'L' (Late)
    if attendance_record and attendance_record.status in ['P', 'L']:
        # User is active today, redirect to deactive
        return redirect('deactive')

    # User is not active today, render the active page
    return render(request, 'active.html', {'current_user': current_user})



@login_required
def active_data_save(request):
    if request.method == 'POST': 
        current_user = request.user
        today = timezone.now().date() 
        current_time = timezone.now().time()
        user_profile = UserProfile.objects.get(user=current_user)
        day_of_week = today.strftime('%A')
        print('day_of_week',day_of_week)

        shift = getattr(user_profile, f"{day_of_week.lower()}_shift", None)
        print('shift',shift)

        status = 'A' 
        if shift:
            if current_time > shift.start_time:
                status = 'L' 

        attendance_record, created = AttendanceRecord.objects.get_or_create(
            user=current_user,
            intime__date=today, 
            defaults={
                'intime': timezone.now(), 
                'status': status,
            }
        )
        
        if not created:  
            attendance_record.intime = timezone.now() 
            attendance_record.status = status
            attendance_record.save()

        response_data = {
            'status': 'success',
            'intime': attendance_record.intime.isoformat(),  
            'redirect_url': '/deactive/' 
        }
        return JsonResponse(response_data)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})





@login_required
def deactive(request):
    current_user = request.user

    today = timezone.now().date()
    
    # Query attendance records for today
    attendance_records = AttendanceRecord.objects.filter(user=current_user, intime__date=today)

    # Initialize total break time
    total_break_time = timedelta()

    for record in attendance_records:
        if record.break_start and record.break_end:
            # Calculate break time for this record
            break_time = record.break_end - record.break_start
            total_break_time += break_time

    # Print total break time in console
    hours = total_break_time.seconds // 3600
    minutes = (total_break_time.seconds // 60) % 60
    seconds = total_break_time.seconds % 60  # Get remaining seconds
    print(f"Total break time consumed by {current_user} today: {total_break_time}")



    
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    attendance_records = AttendanceRecord.objects.filter(
        user=current_user,
        intime__date__gte=thirty_days_ago
    )

    total_records = attendance_records.count()
    total_late = attendance_records.filter(status='L').count()
    total_early_leave = attendance_records.filter(status='E').count()

    days_with_attendance = attendance_records.dates('intime', 'day').count()
    attendance_percentage = (days_with_attendance / 30) * 100 if days_with_attendance > 0 else 0

    print(f"Total records: {total_records}, Late: {total_late}, Early Leave: {total_early_leave}")
    print(f"Days with attendance: {days_with_attendance}, Attendance percentage: {attendance_percentage:.2f}%")

    context = {
        'current_user': current_user,
        'total_records': total_records,
        'total_late': total_late,
        'total_early_leave': total_early_leave,
        'days_with_attendance': days_with_attendance,
        'attendance_percentage': round(attendance_percentage, 2),
        'start_date': thirty_days_ago,
        'end_date': timezone.now().date(),
        'hours':hours,
        'minutes':minutes,
        'seconds':seconds
    }

    return render(request, 'deactive.html', context)


@login_required
def deactive_data_save(request):
    if request.method == 'POST': 
        current_user = request.user
        today = timezone.now().date()

        try:
            attendance_record = AttendanceRecord.objects.get(user=current_user, intime__date=today)


            attendance_record.outtime = timezone.now()
            current_out_time = attendance_record.outtime.time() 

            user_profile = UserProfile.objects.get(user=current_user)
            day_of_week = today.strftime('%A') 
            shift = getattr(user_profile, f"{day_of_week.lower()}_shift", None)

            if attendance_record.status == 'P':
                attendance_record.status = 'P'  

            if shift and shift.end_time:
                if current_out_time < shift.end_time:  
                    attendance_record.status = 'E' 

            attendance_record.save()

            response_data = {
                'status': 'success',
                'outtime': attendance_record.outtime.isoformat(),
                'redirect_url': '/deactive/' 
            }
            return JsonResponse(response_data)
        except AttendanceRecord.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No attendance record found for today.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@require_POST
def breakin_data_save(request):
    data = json.loads(request.body)
    break_start = data.get('break_start')
    
    try:
        record, created = AttendanceRecord.objects.get_or_create(
            user=request.user,
            intime__date=timezone.now().date(),
            defaults={'intime': timezone.now(), 'status': 'P'}
        )
        record.break_start = break_start
        record.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def breakout_data_save(request):
    data = json.loads(request.body)
    break_end = data.get('break_end')
    
    try:
        record = AttendanceRecord.objects.get(user=request.user, intime__date=timezone.now().date())
        record.break_end = break_end
        record.save()
        return JsonResponse({'status': 'success'})
    except AttendanceRecord.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No attendance record found for today'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})