from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="qc-index"), 
    path("initial_sync", views.initial_sync, name="qc-initial-sync"),
    path("signup", views.register, name="qc-register"),
    path("login", views.login_view, name="qc-login"),
    path("item/<int:item_id>", views.item, name="qc-item-api"),

    # API routes
    path("index_api", views.index_api, name="qc-index-api"),
    path("create_item", views.create_item, name="qc-create-item"),
    path("item_api/<int:item_id>", views.item_api),
    path("sync", views.sync, name="qc-sync"),
]