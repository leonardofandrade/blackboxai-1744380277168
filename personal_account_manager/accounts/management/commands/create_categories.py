from django.core.management.base import BaseCommand
from accounts.models import Category

class Command(BaseCommand):
    help = 'Creates default categories for income and expenses'

    def handle(self, *args, **kwargs):
        # Income categories
        income_categories = [
            'Salary',
            'Freelance',
            'Investments',
            'Rental Income',
            'Other Income'
        ]

        # Expense categories
        expense_categories = [
            'Housing',
            'Transportation',
            'Food',
            'Utilities',
            'Healthcare',
            'Entertainment',
            'Shopping',
            'Education',
            'Other Expenses'
        ]

        for category_name in income_categories + expense_categories:
            Category.objects.get_or_create(name=category_name)

        self.stdout.write(self.style.SUCCESS('Successfully created default categories'))
