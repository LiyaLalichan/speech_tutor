from django.core.management.base import BaseCommand
from speech_processing.models import Language, Category

class Command(BaseCommand):
    help = 'Setup initial languages and categories'

    def handle(self, *args, **kwargs):
        # Create languages
        languages = [
            {'code': 'en', 'name': 'English', 'native_name': 'English'},
            {'code': 'es', 'name': 'Spanish', 'native_name': 'Español'},
            {'code': 'fr', 'name': 'French', 'native_name': 'Français'},
             {'code': 'hi', 'name': 'Hindi', 'native_name': 'हिन्दी'},   # Added Hindi
            {'code': 'ml', 'name': 'Malayalam', 'native_name': 'മലയാളം'}  # Added Malayalam
        ]
            # Add more languages as needed
        

        for lang_data in languages:
            Language.objects.get_or_create(
                code=lang_data['code'], 
                defaults={
                    'name': lang_data['name'], 
                    'native_name': lang_data['native_name'],
                    'is_active': True
                }
            )

       # Create default categories for each language
        for language in Language.objects.all():
            Category.get_or_create_default(language)

        self.stdout.write(self.style.SUCCESS('Successfully setup languages and categories'))