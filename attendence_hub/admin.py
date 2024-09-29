from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Shift, UserProfile, AttendanceRecord

# Inline admin descriptor for UserProfile model
# This acts as a bridge between User and UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'
    fk_name = 'user'

# Define a new User admin that includes the UserProfile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    # Display additional fields in the User list view in the Admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_mac_address')
    list_select_related = ('profile',)

    # Function to retrieve MAC address from UserProfile
    def get_mac_address(self, instance):
        return instance.profile.mac_address if hasattr(instance, 'profile') else None
    get_mac_address.short_description = 'MAC Address'

    # Make sure the fields are searchable and sortable
    search_fields = ('username', 'email', 'profile__mac_address')
    ordering = ('username',)

    # When viewing User details, include profile fields
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)

# Register the Shift model with custom display and search functionality
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('shift_day', 'start_time', 'end_time')
    list_filter = ('shift_day',)
    search_fields = ('shift_day', 'start_time', 'end_time')
    ordering = ('start_time',)

# Register the AttendanceRecord model with filtering and search functionality
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'intime', 'outtime', 'status', 'present_or_late_count')
    list_filter = ('status', 'intime', 'outtime')
    search_fields = ('user__username', 'user__email', 'status')
    ordering = ('-intime',)

# Unregister the original User admin and register the customized version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
