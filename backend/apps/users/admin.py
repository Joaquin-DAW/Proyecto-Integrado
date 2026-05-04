from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profesor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'is_active', 'must_change_password')
    list_filter = ('role', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Rol y permisos', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'must_change_password')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    filter_horizontal = ()


class TieneCuentaFilter(admin.SimpleListFilter):
    title = '¿Tiene cuenta?'
    parameter_name = 'tiene_cuenta'

    def lookups(self, request, model_admin):
        return [('si', 'Sí'), ('no', 'No')]

    def queryset(self, request, queryset):
        if self.value() == 'si':
            return queryset.filter(user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(user__isnull=True)


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user', 'tiene_cuenta')
    search_fields = ('nombre',)
    list_filter = (TieneCuentaFilter,)

    def tiene_cuenta(self, obj):
        return obj.user is not None
    tiene_cuenta.boolean = True
    tiene_cuenta.short_description = '¿Tiene cuenta?'
