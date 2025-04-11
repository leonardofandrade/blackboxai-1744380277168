from django.urls import path
from .views import register, login_view, logout_view, dashboard, add_transaction, edit_transaction, delete_transaction

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add_transaction/', add_transaction, name='add_transaction'),
    path('edit_transaction/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    path('delete_transaction/<int:transaction_id>/', delete_transaction, name='delete_transaction'),
]
