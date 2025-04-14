from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Category Management
    path('categories/', views.add_category, name='manage_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),

    # Account Management
    path('accounts/', views.add_account, name='manage_accounts'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/<int:account_id>/edit/', views.edit_account, name='edit_account'),
    path('accounts/<int:account_id>/delete/', views.delete_account, name='delete_account'),
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),

    # Budget Management
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/create/', views.budget_create, name='budget_create'),
    path('budgets/<int:budget_id>/edit/', views.budget_edit, name='budget_edit'),

    # Bill Management
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/create/', views.bill_create, name='bill_create'),
    path('bills/<int:bill_id>/edit/', views.bill_edit, name='bill_edit'),
    path('bills/<int:bill_id>/pay/', views.bill_pay, name='bill_pay'),

    # Investment Management
    path('investments/', views.investment_list, name='investment_list'),
    path('investments/create/', views.investment_create, name='investment_create'),
    path('investments/<int:investment_id>/edit/', views.investment_edit, name='investment_edit'),

    # Transaction Management
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:transaction_id>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<int:transaction_id>/delete/', views.delete_transaction, name='delete_transaction'),
    path('transactions/<int:transaction_id>/reconcile/', views.reconcile_transaction, name='reconcile_transaction'),
    path('transactions/<int:transaction_id>/liquidate/', views.liquidate_transaction, name='liquidate_transaction'),
    path('transactions/recurring/', views.recurring_transactions, name='recurring_transactions'),
]
