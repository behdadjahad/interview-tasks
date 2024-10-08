from django.urls import path, include

urlpatterns = [
    path("inventory/", include(("inventory.urls", "inventory"))),
]
