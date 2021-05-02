from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *
from .forms import UserCreationForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'is_terms_accepted', 'is_staff',  'is_superuser',
                    'created_at', 'modified_at', 'is_active')
    list_filter = ('is_superuser', 'is_terms_accepted', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'password')}),
        ('Personal info', {'fields': ('is_terms_accepted', 'is_active')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'is_staff', 'is_superuser', 'password1', 'password2')}),
        ('Personal info', {'fields': ('is_terms_accepted', 'is_active')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('user_permissions',)}),
    )

    search_fields = ('email',)
    ordering = ('email', 'created_at', 'modified_at')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Order)
