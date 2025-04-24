from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_GET

import hashlib
from .models import Language 
import speech_recognition as sr
import pronouncing
from gtts import gTTS
from urllib.parse import unquote, unquote_plus
from googletrans import Translator, LANGUAGES  # Import LANGUAGES dictionary
import nltk
from nltk.corpus import wordnet

import os
import logging
import uuid
import time

from .models import ExpectedSpeech, Category, Language, SpeechRecord

# Configure logging
logger = logging.getLogger(__name__)

def get_word_meaning(request):
    """Fetch simplified word meaning from WordNet with language support and return translated word"""
    text = request.GET.get('text', '').strip()
    language_code = request.GET.get('language', 'en').lower()
    original_text = text  # Store the original text
    
    # Normalize language code for googletrans
    lang_code_normalized = normalize_language_code(language_code, 'googletrans')
    
    # Ensure NLTK data is downloaded
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    
    try:
        translated_text = text
        # Step 1: If the word is not in English, translate it
        if language_code != 'en':  
            try:
                translator = Translator()
                # Add a retry mechanism for translation services
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        translation = translator.translate(text, src=lang_code_normalized, dest='en')
                        translated_text = translation.text
                        logger.info(f"Translated '{text}' from {language_code} to English: {translated_text}")
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(1)  # Wait before retrying
                            continue
                        raise e
            except Exception as e:
                logger.error(f"Translation error for '{text}': {e}")
                return JsonResponse({
                    "original_word": original_text,
                    "translated_word": "",
                    "meaning": "Translation failed. Could not process word.",
                    "examples": [],
                    "language": language_code,
                    "translated": False,
                    "error": str(e)
                })
        
        # Step 2: Get the meaning of the word (after translation if necessary)
        synonyms = wordnet.synsets(translated_text.lower())  # Use lower() to handle case insensitivity
        
        if synonyms:
            # Get just the first definition and example for simplicity
            meaning = synonyms[0].definition()
            examples = [synonyms[0].examples()[0]] if synonyms[0].examples() else []
            pos = synonyms[0].pos()
            
            # Convert part of speech code to full name
            pos_dict = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 's': 'Adjective', 'r': 'Adverb'}
            part_of_speech = pos_dict.get(pos, '')
            
            # Step 3: For non-English languages, translate the meaning back to original language
            translated_meaning = meaning
            translated_examples = examples
            
            if language_code != 'en':
                try:
                    translator = Translator()
                    # Add a retry mechanism for translation services
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            meaning_translation = translator.translate(meaning, src='en', dest=lang_code_normalized)
                            translated_meaning = meaning_translation.text
                            
                            translated_examples = []
                            for example in examples:
                                example_translation = translator.translate(example, src='en', dest=lang_code_normalized)
                                translated_examples.append(example_translation.text)
                            break
                        except Exception as e:
                            if attempt < max_retries - 1:
                                time.sleep(1)  # Wait before retrying
                                continue
                            raise e
                except Exception as e:
                    logger.error(f"Meaning translation error: {e}")
                    # Keep original English meaning if translation fails
                    translated_meaning = meaning
                    translated_examples = examples
            
            # Create a simplified response with only one meaning and example
            return JsonResponse({
                "original_word": original_text,
                "translated_word": translated_text if language_code != 'en' else original_text,
                "meaning": translated_meaning,
                "part_of_speech": part_of_speech,
                "examples": translated_examples[:1],  # Just take the first example
                "language": language_code,
                "translated": language_code != 'en',
                "english_meaning": meaning  # Include the English meaning for non-English words
            })
        else:
            # No meaning found in WordNet
            no_meaning_message = "Meaning not found in dictionary."
            
            # Try to translate this message for non-English interfaces
            if language_code != 'en':
                try:
                    translator = Translator()
                    translation = translator.translate(no_meaning_message, src='en', dest=lang_code_normalized)
                    no_meaning_message = translation.text
                except:
                    pass  # Keep English message if translation fails
                    
            return JsonResponse({
                "original_word": original_text,
                "translated_word": translated_text if language_code != 'en' else original_text,
                "meaning": no_meaning_message,
                "examples": [],
                "language": language_code,
                "translated": language_code != 'en'
            })
    
    except Exception as e:
        logger.error(f"Error getting meaning for '{text}': {e}")
        return JsonResponse({
            "error": "Could not retrieve meaning",
            "details": str(e)
        }, status=500)
    
def normalize_language_code(code, target_library='googletrans'):
    """
    Normalize language codes between different libraries
    - googletrans: uses ISO 639-1 (2-letter) codes like 'en', 'es', 'fr'
    - gTTS: mostly uses ISO 639-1 but has special cases like 'zh-CN'
    - speech_recognition: uses BCP-47 like 'en-US', 'es-ES'
    """
    # Strip region code if present (e.g., 'en-US' -> 'en')
    base_code = code.split('-')[0].lower() if '-' in code else code.lower()
    
    # Special case mappings
    special_cases = {
        'googletrans': {
            'zh-cn': 'zh-CN',
            'zh-tw': 'zh-TW',
            'zh': 'zh-CN',  # Default Chinese to Simplified
        },
        'gtts': {
            'zh-cn': 'zh-CN',
            'zh-tw': 'zh-TW',
            'zh': 'zh-CN',  # Default Chinese to Simplified
        },
        'speech_recognition': {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'zh': 'zh-CN',
            'zh-cn': 'zh-CN',
            'zh-tw': 'zh-TW',
            'ja': 'ja-JP',
        }
    }
    
    # Check if the code is in special cases for the target library
    if target_library in special_cases and code in special_cases[target_library]:
        return special_cases[target_library][code]
    
    # For googletrans, ensure the code is in their supported languages
    if target_library == 'googletrans':
        if base_code in LANGUAGES:
            return base_code
        else:
            # Default to English if not supported
            logger.warning(f"Language code '{code}' not supported by googletrans, using 'en'")
            return 'en'
    
    # For gTTS, return the code as is (it handles most codes correctly)
    if target_library == 'gtts':
        return code
    
    # For speech recognition, add region code if missing
    if target_library == 'speech_recognition':
        if '-' not in code:
            # Try to find in special cases first
            if code in special_cases['speech_recognition']:
                return special_cases['speech_recognition'][code]
            # Otherwise, default to adding US region for English or same region for others
            if code == 'en':
                return 'en-US'
            else:
                # Make an educated guess - use uppercase of the same code as region
                return f"{code}-{code.upper()}"
    
    # If no specific handling, return the original code
    return code

def get_language_name(language_code):
    """Helper function to get language name from code"""
    language_names = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'ja': 'Japanese',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'pt': 'Portuguese',
        'it': 'Italian',
        'ko': 'Korean',
        # Add more languages as needed
    }
    return language_names.get(language_code, language_code)

@login_required
def practice_words(request):
    """
    Render the pronunciation practice page with language and category selections
    """
    language_code = request.GET.get('language', 'en')
    
    try:
        selected_language = Language.objects.get(code=language_code)
    except Language.DoesNotExist:
        selected_language = Language.get_default_language()
    
    # Optimize category retrieval
    categories = (
        Category.objects
        .filter(language=selected_language)
        .exclude(name='Uncategorized')
        .prefetch_related('words')
        .select_related('language')
    )
    
    languages = Language.objects.filter(is_active=True)
    
    return render(request, 'speech_processing/practice.html', {
        'categories': categories,
        'languages': languages,
        'current_language': selected_language
    })

@login_required
def generate_audio(request):
    """
    Generate text-to-speech (TTS) audio for a word in multiple languages.
    Returns the URL of the generated audio file.
    """
    text = request.GET.get('text', '').strip()
    language_code = request.GET.get('language', 'en').lower()

    if not text:
        logger.warning("No text provided for TTS generation.")
        return JsonResponse({"error": "No text provided"}, status=400)

    # Normalize language code for gTTS
    gtts_lang = normalize_language_code(language_code, 'gtts')
    
    # Get list of gTTS supported languages
    try:
        from gtts.lang import tts_langs
        supported_languages = tts_langs()
    except:
        # Fallback list if dynamic retrieval fails
        supported_languages = {
            "en", "fr", "es", "de", "it", "ja", "ko", "pt", "ru", "zh-CN", "zh-TW", "ar", "hi"
        }
    
    if gtts_lang not in supported_languages and language_code not in supported_languages:
        logger.warning(f"Unsupported language '{language_code}', defaulting to English.")
        gtts_lang = "en"

    # Create a directory for the language
    audio_dir = os.path.join(settings.BASE_DIR, "static", "audio", language_code)
    os.makedirs(audio_dir, exist_ok=True)

    # Generate a unique filename using a hash to avoid encoding issues
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
    audio_filename = f"{text_hash}_{language_code}.mp3"
    audio_path = os.path.join(audio_dir, audio_filename)
    audio_url = f"{settings.STATIC_URL}audio/{language_code}/{audio_filename}"

    # Generate new audio if it does not exist
    if not os.path.exists(audio_path):
        try:
            logger.info(f"Generating TTS for '{text}' in '{language_code}' (gTTS format: {gtts_lang})")
            
            # Use slow=False for normal speaking rate
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(audio_path)
            logger.info(f"Saved TTS file at {audio_path}")
        except Exception as e:
            logger.error(f"TTS generation failed for '{text}' in '{language_code}': {e}")
            
            # Try fallback to English if original language fails
            if language_code != 'en':
                try:
                    logger.info(f"Attempting English fallback for '{text}'")
                    fallback_dir = os.path.join(settings.BASE_DIR, "static", "audio", "en")
                    os.makedirs(fallback_dir, exist_ok=True)
                    
                    fallback_filename = f"{text_hash}_en.mp3"
                    fallback_path = os.path.join(fallback_dir, fallback_filename)
                    fallback_url = f"{settings.STATIC_URL}audio/en/{fallback_filename}"
                    
                    tts = gTTS(text=text, lang='en')
                    tts.save(fallback_path)
                    
                    return JsonResponse({
                        "audio_url": fallback_url, 
                        "text": text, 
                        "language": "en",
                        "original_language": language_code,
                        "fallback": True
                    })
                    
                except Exception as inner_e:
                    logger.error(f"English fallback TTS also failed: {inner_e}")
                    
            return JsonResponse({"error": "Failed to generate audio"}, status=500)

    return JsonResponse({"audio_url": audio_url, "text": text, "language": language_code})

@login_required
def recognize_word(request, text):
    """
    Speech recognition with pronunciation checking and word meaning retrieval.
    """
    text = unquote_plus(text).strip()  # Correctly decode URL-encoded spaces and characters
    language_code = request.GET.get('language', 'en-US').lower()
    
    # Normalize language code for speech recognition
    sr_lang = normalize_language_code(language_code, 'speech_recognition')

    request_id = str(uuid.uuid4())

    logger.info(f"[{request_id}] Speech Recognition Started - Text: {text}, Language: {language_code}, SR Format: {sr_lang}")

    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8  # Slightly increased for non-English speakers

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info(f"[{request_id}] Listening for text: {text}")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

        # Try to recognize using Google's service
        try:
            spoken_text = recognizer.recognize_google(audio, language=sr_lang).strip().lower()
            logger.info(f"[{request_id}] Recognized Speech: {spoken_text}")
        except sr.UnknownValueError:
            # If recognition fails, retry with different language format
            alt_lang = language_code.split('-')[0] if '-' in language_code else language_code
            try:
                spoken_text = recognizer.recognize_google(audio, language=alt_lang).strip().lower()
                logger.info(f"[{request_id}] Recognized Speech with alternate format: {spoken_text}")
            except:
                raise sr.UnknownValueError("Speech could not be recognized in any format")

        language = Language.objects.filter(code=language_code).first()
        if not language and '-' in language_code:
            # Try to find language with base code
            language = Language.objects.filter(code=language_code.split('-')[0]).first()
            
        expected_speech = ExpectedSpeech.objects.filter(text__iexact=text, language=language).first()

        # Generate audio URL
        audio_response = generate_audio(request._request if hasattr(request, '_request') else request)
        audio_data = {}
        if hasattr(audio_response, 'content'):
            import json
            audio_data = json.loads(audio_response.content)
        audio_url = audio_data.get('audio_url', '')

        # Get word meaning
        meaning = "Meaning retrieval not available"
        try:
            # Create a mock request object with the necessary parameters
            from types import SimpleNamespace
            mock_request = SimpleNamespace()
            mock_request.GET = SimpleNamespace()
            mock_request.GET.get = lambda key, default: text if key == 'text' else language_code if key == 'language' else default
            
            meaning_response = get_word_meaning(mock_request)
            if hasattr(meaning_response, 'content'):
                import json
                meaning_data = json.loads(meaning_response.content)
                meaning = meaning_data.get('meaning', 'No meaning available')
        except Exception as e:
            logger.error(f"[{request_id}] Failed to get word meaning: {e}")
            meaning = "Error retrieving meaning"

        # Calculate similarity
        similarity = calculate_similarity(text, spoken_text)

        response_data = {
            "expected_text": text,
            "spoken_text": spoken_text,
            "audio_url": audio_url,
            "language": language_code,
            "similarity_score": similarity,
            "meaning": meaning
        }

        # Determine success based on similarity threshold (more lenient for non-English)
        threshold = 75 if language_code.startswith('en') else 65
        if similarity >= threshold:
            response_data.update({
                "message": f"✅ Good pronunciation in {get_language_name(language_code)}!",
                "status": "success",
                "accuracy": similarity
            })
            if expected_speech and language:
                SpeechRecord.create_record(text=spoken_text, expected_speech=expected_speech, language=language)
        else:
            response_data.update({
                "message": f"❌ Expected: {text}, You said: {spoken_text}",
                "status": "error",
                "accuracy": similarity
            })

        logger.info(f"[{request_id}] Recognition Completed - Status: {response_data['status']}")
        return JsonResponse(response_data)

    except sr.UnknownValueError:
        return JsonResponse({"message": "❌ Could not understand speech.", "status": "error", "language": language_code}, status=400)
    except sr.RequestError as e:
        return JsonResponse({"message": f"⚠️ Speech recognition service unavailable: {str(e)}", "status": "error", "language": language_code}, status=503)
    except OSError as e:
        return JsonResponse({"message": f"⚠️ Microphone not detected or unavailable: {str(e)}", "status": "error", "language": language_code}, status=500)
    except Exception as e:
        logger.critical(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        return JsonResponse({"message": f"❌ An unexpected error occurred: {str(e)}", "status": "error", "language": language_code}, status=500)

def generate_tts_audio(text, language_code='en'):
    """
    Generate text-to-speech audio with fallback mechanism
    Returns the URL path to the audio file
    """
    try:
        # Normalize language code for gTTS
        gtts_lang = normalize_language_code(language_code, 'gtts')
        
        # Ensure audio directory exists
        audio_dir = os.path.join(settings.BASE_DIR, "static", "audio", language_code)
        os.makedirs(audio_dir, exist_ok=True)

        # Create hash-based filename instead of using the text directly
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        audio_filename = f"{text_hash}_{language_code}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        audio_url = f"/static/audio/{language_code}/{audio_filename}"

        # Check if file already exists to avoid regeneration
        if not os.path.exists(audio_path):
            # Primary TTS generation attempt
            try:
                # Use the normalized language code for gTTS
                tts = gTTS(text=text, lang=gtts_lang, slow=False)
                
                # Save the audio file
                tts.save(audio_path)
                logger.info(f"Generated audio for '{text}' in {language_code} (gTTS format: {gtts_lang})")
                
            except Exception as e:
                logger.warning(f"TTS Error for {language_code}: {e}. Falling back to English.")
                
                # Create English fallback
                en_audio_dir = os.path.join(settings.BASE_DIR, "static", "audio", "en")
                os.makedirs(en_audio_dir, exist_ok=True)
                
                en_audio_filename = f"{text_hash}_en.mp3"
                en_audio_path = os.path.join(en_audio_dir, en_audio_filename)
                audio_url = f"/static/audio/en/{en_audio_filename}"
                
                # Generate English version
                tts = gTTS(text=text, lang='en')
                tts.save(en_audio_path)
                logger.info(f"Generated fallback English audio for '{text}'")

        return audio_url
    
    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        return None

def calculate_similarity(expected, spoken):
    """
    Calculate pronunciation similarity using SequenceMatcher
    """
    from difflib import SequenceMatcher
    
    # Normalize inputs
    expected = expected.lower().strip()
    spoken = spoken.lower().strip()
    
    # Calculate similarity ratio
    similarity = SequenceMatcher(None, expected, spoken).ratio()
    return round(similarity * 100, 2)

def get_word_details(request, text):
    """
    Retrieve detailed information about a specific word, including meaning from WordNet.
    """
    text = unquote(text).strip().lower()  # Decode Unicode & convert to lowercase
    language_code = request.GET.get('language', 'en')
    
    # Normalize language code for googletrans
    lang_code_normalized = normalize_language_code(language_code, 'googletrans')
    
    try:
        word_details = ExpectedSpeech.objects.filter(
            text__iexact=text, 
            language__code=language_code
        ).first()
        
        # Get meanings in English first (NLTK WordNet only supports English)
        synsets = wordnet.synsets(text)
        meanings = []
        
        # If not in English and no synsets found, try translating to English first
        if not synsets and language_code != 'en':
            try:
                translator = Translator()
                translation = translator.translate(text, src=lang_code_normalized, dest='en')
                english_text = translation.text.lower()
                synsets = wordnet.synsets(english_text)
                
                # If we found meanings after translation, note this
                if synsets:
                    logger.info(f"Found meanings for '{text}' after translating to '{english_text}'")
                    meanings.append({
                        "note": f"Meanings for translation: '{english_text}'",
                        "pos": "Info"
                    })
            except Exception as e:
                logger.error(f"Translation error before WordNet lookup: {e}")
        
        if synsets:
            pos_dict = {'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 's': 'Adjective', 'r': 'Adverb'}
            for syn in synsets[:5]:  
                meanings.append({
                    'definition': syn.definition(),
                    'pos': pos_dict.get(syn.pos(), syn.pos()),
                    'examples': syn.examples()[:2] if syn.examples() else []
                })
        else:
            meanings.append({"definition": "❌ Meaning not found in dictionary."})
        
        # For non-English languages, translate the meanings
        if language_code.lower() != "en" and meanings and 'definition' in meanings[0] and meanings[0]["definition"] != "❌ Meaning not found in dictionary.":
            try:
                translator = Translator()
                translated_meanings = []
                
                # Add retry mechanism
                max_retries = 3
                for meaning in meanings:
                    # Skip notes
                    if 'note' in meaning:
                        translated_meanings.append(meaning)
                        continue
                        
                    for attempt in range(max_retries):
                        try:
                            # Translate definition
                            translated_def = translator.translate(
                                meaning['definition'], 
                                src='en', 
                                dest=lang_code_normalized
                            ).text
                            
                            # Translate examples if any
                            translated_examples = []
                            for example in meaning.get('examples', []):
                                translated_example = translator.translate(
                                    example, 
                                    src='en', 
                                    dest=lang_code_normalized
                                ).text
                                translated_examples.append(translated_example)
                            
                            translated_meanings.append({
                                'definition': translated_def,
                                'pos': meaning.get('pos', ''),  # Keep part of speech in English
                                'examples': translated_examples
                            })
                            break  # Break retry loop on success
                        except Exception as e:
                            if attempt < max_retries - 1:
                                time.sleep(1)  # Wait before retrying
                                continue
                            logger.error(f"Translation error on attempt {attempt+1}: {e}")
                            # On final attempt failure, add the English version
                            translated_meanings.append(meaning)
                            translated_meanings.append({
                                "definition": f"⚠️ Translation to {language_code} failed.",
                                "pos": "Note"
                            })
                
                # Replace English meanings with translated ones if we have translations
                if translated_meanings:
                    meanings = translated_meanings
            except Exception as e:
                logger.error(f"Translation error for {text} in {language_code}: {e}")
                # Add a note about translation failure but keep English meanings
                meanings.append({
                    "definition": f"⚠️ Translation to {language_code} failed. Showing English meanings.",
                    "pos": "Note"
                })
        
        response_data = {
            'word': text,
            'language': language_code,
            'meanings': meanings
        }
        
        if word_details:
            response_data.update({
                'category': word_details.category.name if word_details.category else None,
                'pronunciation_hints': word_details.pronunciation_hints or '',
                'difficulty_level': word_details.difficulty_level or 'medium'
            })
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Word details retrieval error: {e}")
        return JsonResponse({'error': str(e), 'language': language_code}, status=400)