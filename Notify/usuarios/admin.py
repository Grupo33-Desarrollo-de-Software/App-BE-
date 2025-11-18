from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


class UsuarioAdmin(BaseUserAdmin):
    """Custom admin for Usuario model that properly handles password hashing"""

    # Campos para ver los usuarios en la lista
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")

    # Campos para editar un usuario
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email", "bio", "foto")},
        ),
        (
            "Notifications",
            {"fields": ("notifPorMail", "notifRecomendaciones", "notifGenerales")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Campos para agregar un nuevo usuario
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "email",
                    "first_name",
                    "last_name",
                    "notifPorMail",
                    "notifRecomendaciones",
                    "notifGenerales",
                ),
            },
        ),
    )


admin.site.register(Usuario, UsuarioAdmin)
