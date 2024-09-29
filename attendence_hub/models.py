from django.db import models
from django.contrib.auth.models import User  # Use Django's built-in User model

# Model for defining different shifts
class Shift(models.Model):
    DAY_CHOICES = [
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    shift_day = models.CharField(max_length=10, choices=DAY_CHOICES, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.shift_day} ({self.start_time} - {self.end_time})"

    class Meta:
        ordering = ['start_time']
        verbose_name_plural = "Shifts"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mac_address = models.CharField(max_length=17, null=True, blank=True)


    sunday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='sunday_users')
    monday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='monday_users')
    tuesday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='tuesday_users')
    wednesday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='wednesday_users')
    thursday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='thursday_users')
    friday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='friday_users')
    saturday_shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name='saturday_users')

    def __str__(self):
        return self.user.username


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('P', 'Present'),
        ('L', 'Late'),
        ('A', 'Absent'),
        ('E', 'Early Leave'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    intime = models.DateTimeField()
    outtime = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    break_start = models.DateTimeField(null=True, blank=True)
    break_end = models.DateTimeField(null=True, blank=True)
    present_or_late_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.intime.date()}"

    class Meta:
        ordering = ['-intime']
        verbose_name_plural = "Attendance Records"
