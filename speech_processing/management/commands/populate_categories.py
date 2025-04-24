from django.core.management.base import BaseCommand
from speech_processing.models import Category, ExpectedSpeech, Language  

class Command(BaseCommand):
    help = 'Populate the database with predefined categories and words'

    def handle(self, *args, **options):
        # Define languages
        languages = {
            'en': 'English',
            'fr': 'French',
            'hi': 'Hindi',
            'ml': 'Malayalam'
        }

        categories_data = {
            'en': [
                {"name": "Common Greetings", "words": ["Hello", "Hi", "Good morning", "Good night", "See you later"]},
                {"name": "Positive Words", "words": ["Joyful", "Happy", "Confident", "Amazing", "Encouraging"]},
                {"name": "Nature & Weather", "words": ["Rain", "Thunderstorm", "Sunshine", "Breeze", "Hurricane"]},
                {"name": "Technology Terms", "words": ["Algorithm", "Cybersecurity", "AI", "Cloud Computing", "Blockchain"]},
                {"name": "Food & Drinks", "words": ["Pizza", "Burger", "Coffee", "Pasta", "Ice Cream"]},
                {"name": "Colors", "words": ["Red", "Blue", "Green", "Yellow", "Purple"]},
                {"name": "Animals", "words": ["Dog", "Cat", "Elephant", "Tiger", "Lion"]},
            ],
            'fr': [
                {"name": "Salutations", "words": ["Bonjour", "Salut", "Bonsoir", "Bonne nuit", "À bientôt"]},
                {"name": "Mots Positifs", "words": ["Joyeux", "Heureux", "Confiant", "Incroyable", "Encourageant"]},
                {"name": "Nature & Météo", "words": ["Pluie", "Orage", "Soleil", "Brise", "Ouragan"]},
                {"name": "Technologie", "words": ["Algorithme", "Cybersécurité", "Intelligence Artificielle", "Cloud", "Blockchain"]},
                {"name": "Nourriture & Boissons", "words": ["Pizza", "Burger", "Café", "Pâtes", "Glace"]},
                {"name": "Couleurs", "words": ["Rouge", "Bleu", "Vert", "Jaune", "Violet"]},
                {"name": "Animaux", "words": ["Chien", "Chat", "Éléphant", "Tigre", "Lion"]},
            ],
            'hi': [
                {"name": "सामान्य अभिवादन", "words": ["नमस्ते", "हैलो", "शुभ प्रभात", "शुभ रात्रि", "फिर मिलेंगे"]},
                {"name": "सकारात्मक शब्द", "words": ["आनंदित", "खुश", "आशावान", "प्रेरणादायक", "अद्भुत"]},
                {"name": "प्रकृति और मौसम", "words": ["बारिश", "तूफान", "सूरज", "हवा", "आंधी"]},
                {"name": "तकनीकी शब्द", "words": ["एल्गोरिदम", "साइबर सुरक्षा", "कृत्रिम बुद्धिमत्ता", "क्लाउड", "ब्लॉकचेन"]},
                {"name": "भोजन और पेय", "words": ["पिज़्ज़ा", "बर्गर", "चाय", "पास्ता", "आइसक्रीम"]},
                {"name": "रंग", "words": ["लाल", "नीला", "हरा", "पीला", "बैंगनी"]},
                {"name": "जानवर", "words": ["कुत्ता", "बिल्ली", "हाथी", "शेर", "बाघ"]},
            ],
            'ml': [
                {"name": "സാമാന്യ ആശംസകൾ", "words": ["നമസ്കാരം", "ഹലോ", "സുപ്രഭാതം", "ശുഭ രാത്രി", "പിന്നെ കാണാം"]},
                {"name": "സാന്ദ്രതയുള്ള വാക്കുകൾ", "words": ["സന്തോഷം", "സുഖം", "വിശ്വാസം", "അത്ഭുതം", "പ്രേരിപ്പിക്കുന്ന"]},
                {"name": "പ്രകൃതി & കാലാവസ്ഥ", "words": ["മഴ", "ഇടിമിന്നൽ", "സൂര്യൻ", "കാറ്റ്", "ചുഴലിക്കാറ്റ്"]},
                {"name": "സാങ്കേതിക പദങ്ങൾ", "words": ["അൽഗോരിതം", "സൈബർസെക്യൂരിറ്റി", "AI", "ക്ലൗഡ് കമ്പ്യൂട്ടിംഗ്", "ബ്ലോക്ക്ചെയിൻ"]},
                {"name": "ഭക്ഷണം & പാനീയം", "words": ["പിസ്സ", "ബർഗർ", "ചായ", "പാസ്ത", "ഐസ് ക്രീം"]},
                {"name": "നിറങ്ങൾ", "words": ["ചുവപ്പ്", "നീല", "പച്ച", "മഞ്ഞ", "ജാമുന"]},
                {"name": "മൃഗങ്ങൾ", "words": ["നായ", "പൂച്ച", "ആന", "പുലി", "സിംഹം"]},
            ]
        }

        for lang_code, lang_name in languages.items():
            language, _ = Language.objects.get_or_create(code=lang_code, defaults={'name': lang_name, 'is_active': True})

            for i, category_data in enumerate(categories_data[lang_code]):
                category, created = Category.objects.get_or_create(
                    name=category_data["name"],
                    language=language,  
                    defaults={"order": i}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created category: {category.name} ({lang_name})'))
                else:
                    self.stdout.write(self.style.WARNING(f'Category already exists: {category.name} ({lang_name})'))

                for j, word_text in enumerate(category_data["words"]):
                    word, created = ExpectedSpeech.objects.get_or_create(
                        text=word_text,
                        category=category,  
                        defaults={"order": j}
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Added word: {word.text} ({lang_name})'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Word already exists: {word.text} ({lang_name})'))

        self.stdout.write(self.style.SUCCESS('✅ Database population completed successfully'))
from speech_processing.models import ExpectedSpeech, Language, Category

# Get the French language instance
french = Language.objects.get(code='fr')

# (Optional) Get or create a category to assign to the words
category, _ = Category.objects.get_or_create(name='Common Words', language=french)

# Dictionary of English words with French translations
french_words = {
    "when": "quand",
    "where": "où",
    "how": "comment",
    "police": "police",
    "bus station": "gare routière",
    "taxi": "taxi",
    "water": "eau",
    "hotel": "hôtel",
    "sandwich": "sandwich",
    "petrol": "essence",
    "church": "église",
    "library": "bibliothèque",
    "school": "école",
    "park": "parc",
    "office": "bureau",
    "party": "fête",
    "weekend": "week-end",
    "dress": "robe",
    "basket": "panier"
}

# Insert new ExpectedSpeech records
for english_word, french_word in french_words.items():
    ExpectedSpeech.objects.create(
        text=french_word,                # French goes to 'text'
        translation=english_word,        # English goes to 'translation'
        language=french,
        category=category
    )

print("New words with French translations added.")
