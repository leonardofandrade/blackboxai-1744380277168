from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category

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

@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user)
    categories = Category.objects.all()
    return render(request, 'dashboard.html', {'transactions': transactions, 'categories': categories})

@login_required
def add_transaction(request):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        transaction_type = request.POST.get('transaction_type')
        
        category = Category.objects.get(id=category_id)
        Transaction.objects.create(
            user=request.user,
            category=category,
            amount=amount,
            date=date,
            transaction_type=transaction_type
        )
        return redirect('dashboard')
    
    categories = Category.objects.all()
    return render(request, 'add_transaction.html', {'categories': categories})

@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        transaction_type = request.POST.get('transaction_type')
        
        category = Category.objects.get(id=category_id)
        transaction.category = category
        transaction.amount = amount
        transaction.date = date
        transaction.transaction_type = transaction_type
        transaction.save()
        
        return redirect('dashboard')
    
    categories = Category.objects.all()
    return render(request, 'edit_transaction.html', {'transaction': transaction, 'categories': categories})

@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'transaction': transaction})
