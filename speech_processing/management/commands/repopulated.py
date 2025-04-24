from django.core.management.base import BaseCommand
from speech_processing.models import Category, ExpectedSpeech, Language

class Command(BaseCommand):
    help = 'Delete existing words and populate the database with predefined categories and formatted words'

    def handle(self, *args, **options):
        # First, delete all existing ExpectedSpeech entries
        deleted_count = ExpectedSpeech.objects.all().delete()[0]
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} existing words'))
        
        # Define languages
        languages = {
            'en': 'English',
            'fr': 'French',
            'hi': 'Hindi',
            'ml': 'Malayalam'
        }

        # Common utility/travel words for all languages
        common_words = {
            'en': {
                "when": "when",
                "where": "where",
                "how": "how",
                "police": "police",
                "bus station": "bus station",
                "taxi": "taxi",
                "water": "water",
                "hotel": "hotel",
                "sandwich": "sandwich",
                "petrol": "petrol",
                "church": "church",
                "library": "library",
                "school": "school",
                "park": "park",
                "office": "office",
                "party": "party",
                "weekend": "weekend",
                "dress": "dress",
                "basket": "basket"
            },
            'fr': {
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
            },
            'hi': {
                "when": "कब",
                "where": "कहां",
                "how": "कैसे",
                "police": "पुलिस",
                "bus station": "बस स्टेशन",
                "taxi": "टैक्सी",
                "water": "पानी",
                "hotel": "होटल",
                "sandwich": "सैंडविच",
                "petrol": "पेट्रोल",
                "church": "चर्च",
                "library": "पुस्तकालय",
                "school": "स्कूल",
                "park": "पार्क",
                "office": "कार्यालय",
                "party": "पार्टी",
                "weekend": "सप्ताहांत",
                "dress": "पोशाक",
                "basket": "टोकरी"
            },
            'ml': {
                "when": "എപ്പോൾ",
                "where": "എവിടെ",
                "how": "എങ്ങനെ",
                "police": "പോലീസ്",
                "bus station": "ബസ് സ്റ്റേഷൻ",
                "taxi": "ടാക്സി",
                "water": "വെള്ളം",
                "hotel": "ഹോട്ടൽ",
                "sandwich": "സാൻഡ്‌വിച്ച്",
                "petrol": "പെട്രോൾ",
                "church": "പള്ളി",
                "library": "ലൈബ്രറി",
                "school": "സ്കൂൾ",
                "park": "പാർക്ക്",
                "office": "ഓഫീസ്",
                "party": "പാർട്ടി",
                "weekend": "വാരാന്ത്യം",
                "dress": "വസ്ത്രം",
                "basket": "കുട്ട"
            }
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
                {"name": "Salutations", "words_with_translations": [
                    {"text": "Bonjour", "translation": "Hello"},
                    {"text": "Salut", "translation": "Hi"},
                    {"text": "Bonsoir", "translation": "Good evening"},
                    {"text": "Bonne nuit", "translation": "Good night"},
                    {"text": "À bientôt", "translation": "See you later"}
                ]},
                {"name": "Mots Positifs", "words_with_translations": [
                    {"text": "Joyeux", "translation": "Joyful"},
                    {"text": "Heureux", "translation": "Happy"},
                    {"text": "Confiant", "translation": "Confident"},
                    {"text": "Incroyable", "translation": "Amazing"},
                    {"text": "Encourageant", "translation": "Encouraging"}
                ]},
                {"name": "Nature & Météo", "words_with_translations": [
                    {"text": "Pluie", "translation": "Rain"},
                    {"text": "Orage", "translation": "Thunderstorm"},
                    {"text": "Soleil", "translation": "Sunshine"},
                    {"text": "Brise", "translation": "Breeze"},
                    {"text": "Ouragan", "translation": "Hurricane"}
                ]},
                {"name": "Technologie", "words_with_translations": [
                    {"text": "Algorithme", "translation": "Algorithm"},
                    {"text": "Cybersécurité", "translation": "Cybersecurity"},
                    {"text": "Intelligence Artificielle", "translation": "AI"},
                    {"text": "Cloud", "translation": "Cloud Computing"},
                    {"text": "Blockchain", "translation": "Blockchain"}
                ]},
                {"name": "Nourriture & Boissons", "words_with_translations": [
                    {"text": "Pizza", "translation": "Pizza"},
                    {"text": "Burger", "translation": "Burger"},
                    {"text": "Café", "translation": "Coffee"},
                    {"text": "Pâtes", "translation": "Pasta"},
                    {"text": "Glace", "translation": "Ice Cream"}
                ]},
                {"name": "Couleurs", "words_with_translations": [
                    {"text": "Rouge", "translation": "Red"},
                    {"text": "Bleu", "translation": "Blue"},
                    {"text": "Vert", "translation": "Green"},
                    {"text": "Jaune", "translation": "Yellow"},
                    {"text": "Violet", "translation": "Purple"}
                ]},
                {"name": "Animaux", "words_with_translations": [
                    {"text": "Chien", "translation": "Dog"},
                    {"text": "Chat", "translation": "Cat"},
                    {"text": "Éléphant", "translation": "Elephant"},
                    {"text": "Tigre", "translation": "Tiger"},
                    {"text": "Lion", "translation": "Lion"}
                ]},
            ],
            'hi': [
                {"name": "सामान्य अभिवादन", "words_with_translations": [
                    {"text": "नमस्ते", "translation": "Hello"},
                    {"text": "हैलो", "translation": "Hi"},
                    {"text": "शुभ प्रभात", "translation": "Good morning"},
                    {"text": "शुभ रात्रि", "translation": "Good night"},
                    {"text": "फिर मिलेंगे", "translation": "See you later"}
                ]},
                {"name": "सकारात्मक शब्द", "words_with_translations": [
                    {"text": "आनंदित", "translation": "Joyful"},
                    {"text": "खुश", "translation": "Happy"},
                    {"text": "आशावान", "translation": "Confident"},
                    {"text": "प्रेरणादायक", "translation": "Encouraging"},
                    {"text": "अद्भुत", "translation": "Amazing"}
                ]},
                {"name": "प्रकृति और मौसम", "words_with_translations": [
                    {"text": "बारिश", "translation": "Rain"},
                    {"text": "तूफान", "translation": "Thunderstorm"},
                    {"text": "सूरज", "translation": "Sunshine"},
                    {"text": "हवा", "translation": "Breeze"},
                    {"text": "आंधी", "translation": "Hurricane"}
                ]},
                {"name": "तकनीकी शब्द", "words_with_translations": [
                    {"text": "एल्गोरिदम", "translation": "Algorithm"},
                    {"text": "साइबर सुरक्षा", "translation": "Cybersecurity"},
                    {"text": "कृत्रिम बुद्धिमत्ता", "translation": "AI"},
                    {"text": "क्लाउड", "translation": "Cloud Computing"},
                    {"text": "ब्लॉकचेन", "translation": "Blockchain"}
                ]},
                {"name": "भोजन और पेय", "words_with_translations": [
                    {"text": "पिज़्ज़ा", "translation": "Pizza"},
                    {"text": "बर्गर", "translation": "Burger"},
                    {"text": "चाय", "translation": "Tea"},
                    {"text": "पास्ता", "translation": "Pasta"},
                    {"text": "आइसक्रीम", "translation": "Ice Cream"}
                ]},
                {"name": "रंग", "words_with_translations": [
                    {"text": "लाल", "translation": "Red"},
                    {"text": "नीला", "translation": "Blue"},
                    {"text": "हरा", "translation": "Green"},
                    {"text": "पीला", "translation": "Yellow"},
                    {"text": "बैंगनी", "translation": "Purple"}
                ]},
                {"name": "जानवर", "words_with_translations": [
                    {"text": "कुत्ता", "translation": "Dog"},
                    {"text": "बिल्ली", "translation": "Cat"},
                    {"text": "हाथी", "translation": "Elephant"},
                    {"text": "शेर", "translation": "Lion"},
                    {"text": "बाघ", "translation": "Tiger"}
                ]},
            ],
            'ml': [
                {"name": "സാമാന്യ ആശംസകൾ", "words_with_translations": [
                    {"text": "നമസ്കാരം", "translation": "Hello"},
                    {"text": "ഹലോ", "translation": "Hi"},
                    {"text": "സുപ്രഭാതം", "translation": "Good morning"},
                    {"text": "ശുഭ രാത്രി", "translation": "Good night"},
                    {"text": "പിന്നെ കാണാം", "translation": "See you later"}
                ]},
                {"name": "സാന്ദ്രതയുള്ള വാക്കുകൾ", "words_with_translations": [
                    {"text": "സന്തോഷം", "translation": "Joyful"},
                    {"text": "സുഖം", "translation": "Happy"},
                    {"text": "വിശ്വാസം", "translation": "Confident"},
                    {"text": "അത്ഭുതം", "translation": "Amazing"},
                    {"text": "പ്രേരിപ്പിക്കുന്ന", "translation": "Encouraging"}
                ]},
                {"name": "പ്രകൃതി & കാലാവസ്ഥ", "words_with_translations": [
                    {"text": "മഴ", "translation": "Rain"},
                    {"text": "ഇടിമിന്നൽ", "translation": "Thunderstorm"},
                    {"text": "സൂര്യൻ", "translation": "Sunshine"},
                    {"text": "കാറ്റ്", "translation": "Breeze"},
                    {"text": "ചുഴലിക്കാറ്റ്", "translation": "Hurricane"}
                ]},
                {"name": "സാങ്കേതിക പദങ്ങൾ", "words_with_translations": [
                    {"text": "അൽഗോരിതം", "translation": "Algorithm"},
                    {"text": "സൈബർസെക്യൂരിറ്റി", "translation": "Cybersecurity"},
                    {"text": "AI", "translation": "AI"},
                    {"text": "ക്ലൗഡ് കമ്പ്യൂട്ടിംഗ്", "translation": "Cloud Computing"},
                    {"text": "ബ്ലോക്ക്ചെയിൻ", "translation": "Blockchain"}
                ]},
                {"name": "ഭക്ഷണം & പാനീയം", "words_with_translations": [
                    {"text": "പിസ്സ", "translation": "Pizza"},
                    {"text": "ബർഗർ", "translation": "Burger"},
                    {"text": "ചായ", "translation": "Tea"},
                    {"text": "പാസ്ത", "translation": "Pasta"},
                    {"text": "ഐസ് ക്രീം", "translation": "Ice Cream"}
                ]},
                {"name": "നിറങ്ങൾ", "words_with_translations": [
                    {"text": "ചുവപ്പ്", "translation": "Red"},
                    {"text": "നീല", "translation": "Blue"},
                    {"text": "പച്ച", "translation": "Green"},
                    {"text": "മഞ്ഞ", "translation": "Yellow"},
                    {"text": "ജാമുന", "translation": "Purple"}
                ]},
                {"name": "മൃഗങ്ങൾ", "words_with_translations": [
                    {"text": "നായ", "translation": "Dog"},
                    {"text": "പൂച്ച", "translation": "Cat"},
                    {"text": "ആന", "translation": "Elephant"},
                    {"text": "പുലി", "translation": "Tiger"},
                    {"text": "സിംഹം", "translation": "Lion"}
                ]},
            ]
        }

        for lang_code, lang_name in languages.items():
            language, _ = Language.objects.get_or_create(code=lang_code, defaults={'name': lang_name, 'is_active': True})

            # First create the common words category (with order=0 to make it appear first)
            common_category, _ = Category.objects.get_or_create(
                name="Common Words" if lang_code == 'en' else 
                     "Mots Courants" if lang_code == 'fr' else
                     "सामान्य शब्द" if lang_code == 'hi' else
                     "സാധാരണ വാക്കുകൾ",  # Malayalam
                language=language,
                defaults={"order": 0}  # Set to 0 to make it appear first
            )
            
            words_in_lang = common_words[lang_code]
            
            # For English, just add the words directly
            if lang_code == 'en':
                for j, (_, word_text) in enumerate(words_in_lang.items()):
                    word = ExpectedSpeech.objects.create(
                        text=word_text,
                        category=common_category,
                        order=j
                    )
                    self.stdout.write(self.style.SUCCESS(f'Added common word: {word.text} ({lang_name})'))
            # For non-English, store the word and translation separately
            else:
                for j, (english, translated) in enumerate(words_in_lang.items()):
                    word = ExpectedSpeech.objects.create(
                        text=translated,  # Just the translated word without duplication
                        translation=english,  # Store the English translation
                        category=common_category,
                        order=j
                    )
                    self.stdout.write(self.style.SUCCESS(f'Added common word: {word.text}({word.translation}) ({lang_name})'))
            
            # Then process the regular categories with order starting from 1
            for i, category_data in enumerate(categories_data[lang_code]):
                category, created = Category.objects.get_or_create(
                    name=category_data["name"],
                    language=language,
                    defaults={"order": i + 1}  # Add +1 to start after Common Words
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created category: {category.name} ({lang_name})'))
                else:
                    self.stdout.write(self.style.WARNING(f'Category already exists: {category.name} ({lang_name})'))

                # Handle English words without translations
                if lang_code == 'en':
                    words = category_data["words"]
                    for j, word_text in enumerate(words):
                        word = ExpectedSpeech.objects.create(
                            text=word_text,
                            category=category,
                            order=j
                        )
                        self.stdout.write(self.style.SUCCESS(f'Added word: {word.text} ({lang_name})'))
                # Handle non-English words with translations
                else:
                    words_with_translations = category_data["words_with_translations"]
                    for j, word_data in enumerate(words_with_translations):
                        word = ExpectedSpeech.objects.create(
                            text=word_data['text'],  # Just the word in the target language
                            translation=word_data['translation'],  # Store the English translation
                            category=category,
                            order=j
                        )
                        self.stdout.write(self.style.SUCCESS(f'Added word: {word.text}({word.translation}) ({lang_name})'))
            
        self.stdout.write(self.style.SUCCESS('✅ Database population completed successfully'))