from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.contrib import messages
from .models import Transaction, Category, Account, Budget, Bill, Investment
from datetime import datetime, timedelta
import json

# Account types available in the system
ACCOUNT_TYPES = [
    ('checking', 'Checking'),
    ('savings', 'Savings'),
    ('credit', 'Credit Card'),
    ('investment', 'Investment'),
    ('other', 'Other')
]

# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# Category Management Views
@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        parent_id = request.POST.get('parent')
        category = Category.objects.create(
            user=request.user,
            name=name,
            parent_id=parent_id
        )
        messages.success(request, 'Category added successfully.')
        return redirect('manage_categories')
    categories = Category.objects.filter(user=request.user)
    return render(request, 'manage_categories.html', {'categories': categories})

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.parent_id = request.POST.get('parent')
        category.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('manage_categories')
    categories = Category.objects.filter(user=request.user)
    return render(request, 'manage_categories.html', {'categories': categories, 'edit_category': category})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('manage_categories')
    return render(request, 'manage_categories.html', {'category': category})

# Account Management Views
@login_required
def add_account(request):
    if request.method == 'POST':
        name = request.POST['name']
        account_type = request.POST['account_type']
        bank_name = request.POST.get('bank_name', '')
        account_number = request.POST.get('account_number', '')
        notes = request.POST.get('notes', '')
        is_active = request.POST.get('is_active') == 'on'
        initial_balance = request.POST.get('balance', 0)

        account = Account.objects.create(
            user=request.user,
            name=name,
            account_type=account_type,
            bank_name=bank_name,
            account_number=account_number,
            notes=notes,
            is_active=is_active,
            balance=initial_balance
        )
        messages.success(request, 'Account added successfully.')
        return redirect('manage_accounts')
    
    return render(request, 'accounts/account_form.html', {
        'accounts': Account.objects.filter(user=request.user),
        'ACCOUNT_TYPES': ACCOUNT_TYPES
    })

@login_required
def edit_account(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user)
    if request.method == 'POST':
        account.name = request.POST['name']
        account.account_type = request.POST['account_type']
        account.bank_name = request.POST.get('bank_name', '')
        account.account_number = request.POST.get('account_number', '')
        account.notes = request.POST.get('notes', '')
        account.is_active = request.POST.get('is_active') == 'on'
        account.save()
        messages.success(request, 'Account updated successfully.')
        return redirect('manage_accounts')
    
    return render(request, 'accounts/account_form.html', {
        'account': account,
        'accounts': Account.objects.filter(user=request.user),
        'ACCOUNT_TYPES': ACCOUNT_TYPES
    })

@login_required
def delete_account(request, account_id):
    account = get_object_or_404(Account, id=account_id, user=request.user)
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Account deleted successfully.')
        return redirect('manage_accounts')
    return render(request, 'accounts/confirm_delete.html', {'account': account})

# Dashboard View
@login_required
def dashboard(request):
    accounts = Account.objects.filter(user=request.user, is_active=True)
    transactions = Transaction.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    # Get filter parameters
    category_id = request.GET.get('category')
    transaction_type = request.GET.get('type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    account_id = request.GET.get('account')

    # Apply filters
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if status:
        transactions = transactions.filter(status=status)
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) |
            Q(category__name__icontains=search) |
            Q(amount__icontains=search)
        )
    if account_id:
        transactions = transactions.filter(account_id=account_id)

    # Calculate totals
    total_income = transactions.filter(transaction_type='income').aggregate(
        total=Sum('amount'))['total'] or 0
    total_expenses = transactions.filter(transaction_type='expense').aggregate(
        total=Sum('amount'))['total'] or 0
    balance = total_income - total_expenses

    # Get upcoming bills
    upcoming_bills = Bill.objects.filter(
        user=request.user,
        is_paid=False,
        due_date__gte=datetime.now().date()
    ).order_by('due_date')[:5]

    # Get investment summary
    investments = Investment.objects.filter(user=request.user)
    total_investment_value = sum(inv.get_total_value() for inv in investments)
    total_gain_loss = sum(inv.get_gain_loss() for inv in investments)

    # Get budget vs actual spending
    budgets = Budget.objects.filter(
        user=request.user,
        start_date__lte=datetime.now().date(),
        end_date__gte=datetime.now().date()
    )
    budget_data = []
    for budget in budgets:
        spent = budget.get_spending()
        budget_data.append({
            'category': budget.category.name,
            'budget': float(budget.amount),
            'spent': float(spent),
            'remaining': float(budget.amount - spent)
        })

    context = {
        'accounts': accounts,
        'transactions': transactions,
        'categories': categories,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'upcoming_bills': upcoming_bills,
        'investments': investments,
        'total_investment_value': total_investment_value,
        'total_gain_loss': total_gain_loss,
        'budget_data': budget_data,
        # Filter values
        'selected_category': category_id,
        'selected_type': transaction_type,
        'selected_status': status,
        'selected_account': account_id,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
    }
    
    return render(request, 'dashboard.html', context)

# Budget Management Views
@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budgets/budget_list.html', {'budgets': budgets})

@login_required
def budget_create(request):
    if request.method == 'POST':
        budget = Budget.objects.create(
            user=request.user,
            category_id=request.POST['category'],
            amount=request.POST['amount'],
            period=request.POST['period'],
            start_date=request.POST['start_date'],
            end_date=request.POST.get('end_date'),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Budget created successfully.')
        return redirect('budget_list')
    categories = Category.objects.filter(user=request.user)
    return render(request, 'budgets/budget_form.html', {'categories': categories})

@login_required
def budget_edit(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    if request.method == 'POST':
        budget.category_id = request.POST['category']
        budget.amount = request.POST['amount']
        budget.period = request.POST['period']
        budget.start_date = request.POST['start_date']
        budget.end_date = request.POST.get('end_date')
        budget.notes = request.POST.get('notes', '')
        budget.save()
        messages.success(request, 'Budget updated successfully.')
        return redirect('budget_list')
    categories = Category.objects.filter(user=request.user)
    return render(request, 'budgets/budget_form.html', {
        'budget': budget,
        'categories': categories
    })

# Bill Management Views
@login_required
def bill_list(request):
    bills = Bill.objects.filter(user=request.user)
    return render(request, 'bills/bill_list.html', {'bills': bills})

@login_required
def bill_create(request):
    if request.method == 'POST':
        bill = Bill.objects.create(
            user=request.user,
            name=request.POST['name'],
            amount=request.POST['amount'],
            due_date=request.POST['due_date'],
            frequency=request.POST['frequency'],
            category_id=request.POST['category'],
            account_id=request.POST.get('account'),
            reminder_days=request.POST.get('reminder_days', 7),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Bill created successfully.')
        return redirect('bill_list')
    categories = Category.objects.filter(user=request.user)
    accounts = Account.objects.filter(user=request.user, is_active=True)
    return render(request, 'bills/bill_form.html', {
        'categories': categories,
        'accounts': accounts
    })

@login_required
def bill_edit(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    if request.method == 'POST':
        bill.name = request.POST['name']
        bill.amount = request.POST['amount']
        bill.due_date = request.POST['due_date']
        bill.frequency = request.POST['frequency']
        bill.category_id = request.POST['category']
        bill.account_id = request.POST.get('account')
        bill.reminder_days = request.POST.get('reminder_days', 7)
        bill.notes = request.POST.get('notes', '')
        bill.save()
        messages.success(request, 'Bill updated successfully.')
        return redirect('bill_list')
    categories = Category.objects.filter(user=request.user)
    accounts = Account.objects.filter(user=request.user, is_active=True)
    return render(request, 'bills/bill_form.html', {
        'bill': bill,
        'categories': categories,
        'accounts': accounts
    })

@login_required
def bill_pay(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, user=request.user)
    if request.method == 'POST':
        bill.is_paid = True
        bill.save()
        
        # Create transaction for the bill payment
        Transaction.objects.create(
            user=request.user,
            account_id=bill.account_id,
            category=bill.category,
            amount=bill.amount,
            date=datetime.now().date(),
            transaction_type='expense',
            description=f'Bill payment: {bill.name}',
            status='completed'
        )
        
        messages.success(request, 'Bill marked as paid.')
        return redirect('bill_list')
    return render(request, 'bills/bill_pay.html', {'bill': bill})

# Investment Management Views
@login_required
def investment_list(request):
    investments = Investment.objects.filter(user=request.user)
    total_value = sum(inv.get_total_value() for inv in investments)
    total_gain_loss = sum(inv.get_gain_loss() for inv in investments)
    return render(request, 'investments/investment_list.html', {
        'investments': investments,
        'total_value': total_value,
        'total_gain_loss': total_gain_loss
    })

@login_required
def investment_create(request):
    if request.method == 'POST':
        investment = Investment.objects.create(
            user=request.user,
            account_id=request.POST['account'],
            name=request.POST['name'],
            symbol=request.POST['symbol'],
            investment_type=request.POST['investment_type'],
            shares=request.POST['shares'],
            purchase_price=request.POST['purchase_price'],
            current_price=request.POST['current_price'],
            purchase_date=request.POST['purchase_date'],
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Investment created successfully.')
        return redirect('investment_list')
    accounts = Account.objects.filter(
        user=request.user,
        account_type='investment',
        is_active=True
    )
    return render(request, 'investments/investment_form.html', {'accounts': accounts})

@login_required
def investment_edit(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id, user=request.user)
    if request.method == 'POST':
        investment.account_id = request.POST['account']
        investment.name = request.POST['name']
        investment.symbol = request.POST['symbol']
        investment.investment_type = request.POST['investment_type']
        investment.shares = request.POST['shares']
        investment.purchase_price = request.POST['purchase_price']
        investment.current_price = request.POST['current_price']
        investment.purchase_date = request.POST['purchase_date']
        investment.notes = request.POST.get('notes', '')
        investment.save()
        messages.success(request, 'Investment updated successfully.')
        return redirect('investment_list')
    accounts = Account.objects.filter(
        user=request.user,
        account_type='investment',
        is_active=True
    )
    return render(request, 'investments/investment_form.html', {
        'investment': investment,
        'accounts': accounts
    })

# Transaction Management Views
@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'transactions/transaction_list.html', {'transactions': transactions})

@login_required
def add_transaction(request):
    if request.method == 'POST':
        account_id = request.POST.get('account')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        transaction_type = request.POST.get('transaction_type')
        description = request.POST.get('description')
        recurrence_type = request.POST.get('recurrence_type')
        recurrence_end_date = request.POST.get('recurrence_end_date')
        
        transaction = Transaction.objects.create(
            user=request.user,
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            transaction_type=transaction_type,
            description=description,
            recurrence_type=recurrence_type,
            recurrence_end_date=datetime.strptime(recurrence_end_date, '%Y-%m-%d').date() if recurrence_end_date else None
        )

        if recurrence_type != 'none' and recurrence_end_date:
            transaction.create_recurring_transactions()

        messages.success(request, 'Transaction added successfully.')
        return redirect('dashboard')
    
    accounts = Account.objects.filter(user=request.user, is_active=True)
    categories = Category.objects.filter(user=request.user)
    return render(request, 'transactions/transaction_form.html', {
        'accounts': accounts,
        'categories': categories
    })

@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        transaction.account_id = request.POST.get('account')
        transaction.category_id = request.POST.get('category')
        transaction.amount = request.POST.get('amount')
        transaction.date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
        transaction.transaction_type = request.POST.get('transaction_type')
        transaction.description = request.POST.get('description')
        transaction.save()
        
        messages.success(request, 'Transaction updated successfully.')
        return redirect('dashboard')
    
    accounts = Account.objects.filter(user=request.user, is_active=True)
    categories = Category.objects.filter(user=request.user)
    return render(request, 'transactions/transaction_form.html', {
        'transaction': transaction,
        'accounts': accounts,
        'categories': categories
    })

@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        # If it's a recurring transaction, ask if want to delete all related transactions
        delete_recurring = request.POST.get('delete_recurring')
        if delete_recurring and transaction.parent_transaction:
            Transaction.objects.filter(parent_transaction=transaction.parent_transaction).delete()
        else:
            transaction.delete()
        messages.success(request, 'Transaction deleted successfully.')
        return redirect('dashboard')
    return render(request, 'transactions/confirm_delete.html', {'transaction': transaction})

@login_required
def reconcile_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        transaction.status = 'reconciled'
        transaction.reconciled_date = datetime.now().date()
        transaction.save()
        messages.success(request, 'Transaction reconciled successfully.')
        return redirect('dashboard')
    return render(request, 'transactions/reconcile.html', {'transaction': transaction})

@login_required
def liquidate_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        transaction.liquidate(notes=notes)
        messages.success(request, 'Transaction liquidated successfully.')
        return redirect('dashboard')
    return render(request, 'transactions/liquidate.html', {'transaction': transaction})

@login_required
def recurring_transactions(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).exclude(
        recurrence_type='none'
    ).order_by('-date')
    return render(request, 'transactions/recurring.html', {'transactions': transactions})
