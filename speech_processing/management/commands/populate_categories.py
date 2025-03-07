# your_app/management/commands/populate_categories.py
from django.core.management.base import BaseCommand
from speech_processing.models import Category, ExpectedSpeech  # Replace 'your_app' with your actual app name

class Command(BaseCommand):
    help = 'Populate the database with predefined categories and words'

    def handle(self, *args, **options):
        # Define the categories and words
        categories_data = [
            {
                "name": "Common Greetings",
                "words": ["Hello", "Hi", "Good morning", "Good afternoon", "Good evening", 
                         "How are you?", "Nice to meet you", "Take care", "See you later", "Have a great day"]
            },
            {
                "name": "Positive Words",
                "words": ["Joyful", "Cheerful", "Inspiring", "Encouraging", "Hopeful", 
                         "Grateful", "Kindness", "Resilient", "Confident", "Amazing"]
            },
            {
                "name": "Difficult Pronunciations",
                "words": ["Worcestershire", "Anemone", "Colonel", "Phenomenon", "Mischievous", 
                         "Entrepreneur", "Quinoa", "Rural", "Squirrel", "Archaeology"]
            },
            {
                "name": "Nature & Weather",
                "words": ["Rainforest", "Thunderstorm", "Avalanche", "Hurricane", "Bloom", 
                         "Ecosystem", "Drought", "Glacier", "Autumn", "Breeze"]
            },
            {
                "name": "Food & Beverages",
                "words": ["Croissant", "Spaghetti", "Cappuccino", "Sushi", "Guacamole", 
                         "Barbecue", "Omelette", "Smoothie", "Tofu", "Risotto"]
            },
            {
                "name": "Technology Terms",
                "words": ["Algorithm", "Artificial Intelligence", "Bandwidth", "Blockchain", "Cloud Computing", 
                         "Cybersecurity", "Encryption", "Malware", "Quantum Computing", "Virtual Reality"]
            }
        ]

        # Create categories and words
        for i, category_data in enumerate(categories_data):
            category, created = Category.objects.get_or_create(
                name=category_data["name"],
                defaults={"order": i}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))
            
            # Add words to this category
            for j, word_text in enumerate(category_data["words"]):
                word, created = ExpectedSpeech.objects.get_or_create(
                    text=word_text,
                    defaults={"category": category, "order": j}
                )
                
                # If word exists but doesn't have a category, assign it
                if not created and word.category is None:
                    word.category = category
                    word.order = j
                    word.save()
                    self.stdout.write(self.style.WARNING(f'Updated word: {word.text}'))
                elif created:
                    self.stdout.write(self.style.SUCCESS(f'Created word: {word.text}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Word already exists: {word.text}'))
        
        self.stdout.write(self.style.SUCCESS('Database population completed successfully'))
