
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_GET
<<<<<<< HEAD
import hashlib
from .models import Language 
import speech_recognition as sr
import pronouncing
from gtts import gTTS
from urllib.parse import unquote, unquote_plus
from googletrans import Translator  # You'll need to install this package
import nltk
from nltk.corpus import wordnet

=======

import speech_recognition as sr
import pronouncing
from gtts import gTTS
>>>>>>> 87bc3c2225dfc195908054f0811ab69d497c0cd8
import os
import logging
import uuid

from .models import ExpectedSpeech, Category, Language, SpeechRecord

# Configure logging
logger = logging.getLogger(__name__)

<<<<<<< HEAD
def get_word_meaning(request):
    """Fetch word meaning from WordNet with language support and return translated word"""
    text = request.GET.get('text', '').strip()
    language_code = request.GET.get('language', 'en').lower()
    original_text = text  # Store the original text
    
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
                translation = translator.translate(text, src=language_code, dest='en')
                translated_text = translation.text
                logger.info(f"Translated '{text}' from {language_code} to English: {translated_text}")
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
                }, status=500)
        
        # Step 2: Get the meaning of the word (after translation if necessary)
        synonyms = wordnet.synsets(translated_text.lower())  # Use lower() to handle case insensitivity
        
        if synonyms:
            meaning = synonyms[0].definition()
            examples = synonyms[0].examples()
            
            # Step 3: For non-English languages, translate the meaning back to original language
            translated_meaning = meaning
            translated_examples = examples
            
            if language_code != 'en':
                try:
                    translator = Translator()
                    meaning_translation = translator.translate(meaning, src='en', dest=language_code)
                    translated_meaning = meaning_translation.text
                    
                    translated_examples = []
                    for example in examples:
                        example_translation = translator.translate(example, src='en', dest=language_code)
                        translated_examples.append(example_translation.text)
                except Exception as e:
                    logger.error(f"Meaning translation error: {e}")
                    # Keep original English meaning if translation fails
                    translated_meaning = meaning + " (translation failed)"
                    translated_examples = examples
            
            return JsonResponse({
                "original_word": original_text,
                "translated_word": translated_text if language_code != 'en' else original_text,
                "meaning": translated_meaning,
                "examples": translated_examples if translated_examples else [],
                "original_meaning": meaning,  # Include original English meaning
                "language": language_code,
                "translated": language_code != 'en'
            })
        else:
            # No meaning found in WordNet
            no_meaning_message = "Meaning not found in dictionary."
            
            # Try to translate this message for non-English interfaces
            if language_code != 'en':
                try:
                    translator = Translator()
                    translation = translator.translate(no_meaning_message, src='en', dest=language_code)
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
    

def get_language_name(language_code):
    """Helper function to get language name from code"""
    language_names = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'zh-cn': 'Chinese',
        'ja': 'Japanese',
        # Add more languages as needed
    }
    return language_names.get(language_code, language_code)

=======
>>>>>>> 87bc3c2225dfc195908054f0811ab69d497c0cd8
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

<<<<<<< HEAD


logger = logging.getLogger(__name__)
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

    # Ensure the language format is correct for gTTS
    supported_languages = ["en", "fr", "hi", "es", "de", "zh-cn", "zh-tw"]
    
    if language_code not in supported_languages:
        logger.warning(f"Unsupported language '{language_code}', defaulting to English.")
        language_code = "en"

    # Define correct language mapping for gTTS
    lang_map = {
        "zh-cn": "zh-CN",
        "zh-tw": "zh-TW",
    }
    lang = lang_map.get(language_code, language_code)  # Use mapped language if available

    # Create a directory for the language
    audio_dir = os.path.join(settings.BASE_DIR, "static", "audio", language_code)
    os.makedirs(audio_dir, exist_ok=True)

    # Generate a unique filename using a hash
    text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:10]
    audio_filename = f"{text_hash}_{language_code}.mp3"
    audio_path = os.path.join(audio_dir, audio_filename)
    audio_url = f"{settings.STATIC_URL}audio/{language_code}/{audio_filename}"

    # Generate new audio if it does not exist
    if not os.path.exists(audio_path):
        try:
            logger.info(f"Generating TTS for '{text}' in '{language_code}'")
            tts = gTTS(text=text, lang=lang)
            tts.save(audio_path)
            logger.info(f"Saved TTS file at {audio_path}")
        except Exception as e:
            logger.error(f"TTS generation failed for '{text}' in '{language_code}': {e}")
            return JsonResponse({"error": "Failed to generate audio"}, status=500)

    return JsonResponse({"audio_url": audio_url, "text": text, "language": language_code})

@login_required
def recognize_word(request, text):
    """
    Speech recognition with pronunciation checking and word meaning retrieval.
    """
    text = unquote_plus(text).strip()  # Correctly decode URL-encoded spaces and characters
    language_code = request.GET.get('language', 'en-US').lower()

    request_id = str(uuid.uuid4())

    logger.info(f"[{request_id}] Speech Recognition Started - Text: {text}, Language: {language_code}")

=======
@login_required
def recognize_word(request, word):
    """
    Advanced speech recognition with detailed error handling and logging
    """
    language_code = request.GET.get('language', 'en-US')
    request_id = str(uuid.uuid4())  # Unique identifier for tracking
    
    logger.info(f"[{request_id}] Speech Recognition Started - Word: {word}, Language: {language_code}")
    
>>>>>>> 87bc3c2225dfc195908054f0811ab69d497c0cd8
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.5

    try:
<<<<<<< HEAD
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info(f"[{request_id}] Listening for text: {text}")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

        spoken_text = recognizer.recognize_google(audio, language=language_code).strip().lower()
        logger.info(f"[{request_id}] Recognized Speech: {spoken_text}")

        language = Language.objects.filter(code=language_code).first()
        expected_speech = ExpectedSpeech.objects.filter(text__iexact=text, language=language).first()

        audio_url = generate_tts_audio(text, language_code)
        meaning = get_word_meaning(text)  

        response_data = {
            "expected_text": text,
            "spoken_text": spoken_text,
            "audio_url": audio_url,
            "language": language_code,
            "similarity_score": calculate_similarity(text, spoken_text),
            "meaning": meaning
        }

        if spoken_text == text.lower():
            response_data.update({
                "message": f"✅ Correct pronunciation in {language_code}!",
                "status": "success",
                "accuracy": 100
            })
            if expected_speech:
                SpeechRecord.create_record(text=spoken_text, expected_speech=expected_speech, language=expected_speech.language)
        else:
            response_data.update({
                "message": f"❌ Expected: {text}, You said: {spoken_text}",
                "status": "error",
                "accuracy": response_data['similarity_score']
            })

        logger.info(f"[{request_id}] Recognition Completed - Status: {response_data['status']}")
        return JsonResponse(response_data)

    except sr.UnknownValueError:
        return JsonResponse({"message": "❌ Could not understand speech.", "status": "error", "language": language_code}, status=400)
    except sr.RequestError:
        return JsonResponse({"message": "⚠️ Speech recognition service unavailable.", "status": "error", "language": language_code}, status=503)
    except OSError:
        return JsonResponse({"message": "⚠️ Microphone not detected or unavailable.", "status": "error", "language": language_code}, status=500)
    except Exception as e:
        logger.critical(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        return JsonResponse({"message": f"❌ An unexpected error occurred: {str(e)}", "status": "error", "language": language_code}, status=500)

def generate_tts_audio(text, language_code='en'):
    """
    Generate text-to-speech audio with fallback mechanism
    Returns the URL path to the audio file
    """
    try:
        # Ensure audio directory exists
        audio_dir = os.path.join(settings.BASE_DIR, "static", "audio", language_code)
        os.makedirs(audio_dir, exist_ok=True)

        # Create safe filename - handle special characters that might appear in non-English text
        safe_text = ''.join(e if e.isalnum() else '_' for e in text)
        safe_text = safe_text[:50]  # Limit filename length
        audio_filename = f"{safe_text}_{language_code}.mp3"
        audio_path = os.path.join(audio_dir, audio_filename)
        audio_url = f"/static/audio/{language_code}/{audio_filename}"

        # Check if file already exists to avoid regeneration
        if not os.path.exists(audio_path):
            # Primary TTS generation attempt
            try:
                # For some languages, gTTS needs specific handling
                if language_code in ['zh-cn', 'zh-tw']:
                    # Handle Chinese variants explicitly
                    lang = 'zh-CN' if language_code == 'zh-cn' else 'zh-TW'
                    tts = gTTS(text, lang=lang)
                else:
                    # Standard language code handling
                    tts = gTTS(text, lang=language_code)
                
                # Save the audio file
                tts.save(audio_path)
                logger.info(f"Generated audio for '{text}' in {language_code}")
                
            except Exception as e:
                logger.warning(f"TTS Error for {language_code}: {e}. Falling back to English.")
                
                # Create English fallback
                en_audio_dir = os.path.join(settings.BASE_DIR, "static", "audio", "en")
                os.makedirs(en_audio_dir, exist_ok=True)
                
                en_audio_filename = f"{safe_text}_en.mp3"
                en_audio_path = os.path.join(en_audio_dir, en_audio_filename)
                audio_url = f"/static/audio/en/{en_audio_filename}"
                
                # Generate English version
                tts = gTTS(text, lang='en')
                tts.save(en_audio_path)
                logger.info(f"Generated fallback English audio for '{text}'")

        return audio_url
    
    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        return None
def calculate_similarity(expected, spoken):
    """
    Calculate pronunciation similarity using Levenshtein distance
    """
    from difflib import SequenceMatcher
    
=======
        # Attempt to get microphone input
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            logger.info(f"[{request_id}] Listening for word: {word}")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)

        try:
            # Perform speech recognition
            spoken_text = recognizer.recognize_google(
                audio, 
                language=language_code,
                show_all=False
            ).strip().lower()
            
            logger.info(f"[{request_id}] Recognized Speech: {spoken_text}")

            # Retrieve language and expected speech
            try:
                language = Language.objects.get(code=language_code)
                expected_speech = ExpectedSpeech.objects.filter(
                    word__iexact=word, 
                    language=language
                ).first()
            except (Language.DoesNotExist, ExpectedSpeech.DoesNotExist):
                logger.warning(f"[{request_id}] Language or Expected Speech not found")
                expected_speech = None

            # Generate audio for playback
            audio_url = generate_audio(word, language_code)

            # Prepare response data
            response_data = {
                "expected_word": word,
                "spoken_word": spoken_text,
                "audio_url": audio_url,
                "language": language_code,
                "similarity_score": calculate_similarity(word, spoken_text)
            }

            # Check pronunciation accuracy
            if spoken_text == word.lower():
                response_data.update({
                    "message": f"✅ Correct pronunciation in {language_code}!",
                    "status": "success",
                    "accuracy": 100
                })
                
                # Create speech record if expected speech exists
                if expected_speech:
                    SpeechRecord.create_record(
                        text=spoken_text, 
                        expected_speech=expected_speech, 
                        language=expected_speech.language
                    )
            else:
                response_data.update({
                    "message": f"❌ Expected: {word}, You said: {spoken_text}",
                    "status": "error",
                    "accuracy": response_data['similarity_score']
                })

            logger.info(f"[{request_id}] Recognition Completed - Status: {response_data['status']}")
            return JsonResponse(response_data)

        except sr.UnknownValueError:
            logger.warning(f"[{request_id}] Speech not understood")
            return JsonResponse({
                "message": "❌ Could not understand speech. Please try again.",
                "status": "error",
                "language": language_code
            }, status=400)
        
        except sr.RequestError as e:
            logger.error(f"[{request_id}] Speech recognition service error: {e}")
            return JsonResponse({
                "message": "⚠️ Speech recognition service unavailable.",
                "status": "error",
                "language": language_code
            }, status=503)

    except Exception as e:
        logger.critical(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        return JsonResponse({
            "message": f"❌ An unexpected error occurred: {str(e)}",
            "status": "error",
            "language": language_code
        }, status=500)

def generate_audio(word, language_code='en'):
    """
    Generate text-to-speech audio with fallback mechanism
    """
    try:
        language = Language.objects.get(code=language_code)
    except Language.DoesNotExist:
        language = Language.get_default_language()
        language_code = 'en'

    # Ensure audio directory exists
    audio_dir = os.path.join(settings.BASE_DIR, "static", "audio", language_code)
    os.makedirs(audio_dir, exist_ok=True)

    # Create safe filename
    safe_word = ''.join(e for e in word if e.isalnum())
    audio_filename = f"{safe_word}_{language_code}.mp3"
    audio_path = os.path.join(audio_dir, audio_filename)

    # Fallback TTS generation
    try:
        tts = gTTS(word, lang=language_code)
        tts.save(audio_path)
    except Exception as e:
        logger.warning(f"TTS Error for {language_code}: {e}. Falling back to English.")
        tts = gTTS(word, lang='en')
        audio_path = os.path.join(audio_dir, f"{safe_word}_en.mp3")
        tts.save(audio_path)

    return f"/static/audio/{language_code}/{audio_filename}"

def calculate_similarity(expected, spoken):
    """
    Calculate pronunciation similarity using Levenshtein distance
    """
    from difflib import SequenceMatcher
    
>>>>>>> 87bc3c2225dfc195908054f0811ab69d497c0cd8
    # Normalize inputs
    expected = expected.lower().strip()
    spoken = spoken.lower().strip()
    
    # Calculate similarity ratio
    similarity = SequenceMatcher(None, expected, spoken).ratio()
    return round(similarity * 100, 2)


<<<<<<< HEAD
def get_word_details(request, text):
    """
    Retrieve detailed information about a specific word, including meaning from WordNet.
    """
    text = unquote(text).strip().lower()  # Decode Unicode & convert to lowercase
    language_code = request.GET.get('language', 'en')
    
    # Ensure NLTK data is downloaded
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
        
    try:
        word_details = ExpectedSpeech.objects.filter(
            text__iexact=text, 
            language__code=language_code
        ).first()
        
        # For non-English languages, translate to English first for WordNet lookup
        lookup_text = text
        original_translation = None
        
        if language_code.lower() != "en":
            try:
                translator = Translator()
                translation = translator.translate(text, src=language_code, dest='en')
                lookup_text = translation.text.lower()
                original_translation = {
                    'from': text,
                    'to': lookup_text,
                    'language_from': language_code,
                    'language_to': 'en'
                }
                logger.info(f"Translated for lookup: '{text}' -> '{lookup_text}'")
            except Exception as e:
                logger.error(f"Translation for lookup failed: {e}")
                # Continue with original text as fallback
        
        # Get meanings in English first (NLTK WordNet only supports English)
        synsets = wordnet.synsets(lookup_text)
        meanings = []
        
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
        
        # For non-English languages, translate the meanings back to the target language
        if language_code.lower() != "en" and meanings and meanings[0].get("definition") != "❌ Meaning not found in dictionary.":
            try:
                translator = Translator()
                translated_meanings = []
                
                # Map language codes to googletrans format if needed
                target_lang = language_code.lower()
                if len(target_lang) > 2:  # If it's a longer code like 'eng', 'fra', etc.
                    lang_map = {'eng': 'en', 'fra': 'fr', 'hin': 'hi', 'spa': 'es', 'deu': 'de'}
                    target_lang = lang_map.get(target_lang, target_lang[:2])
                
                for meaning in meanings:
                    # Keep track of original English definition
                    original_definition = meaning.get('definition', '')
                    
                    # Translate definition
                    translated_def = translator.translate(
                        original_definition, 
                        src='en', 
                        dest=target_lang
                    ).text
                    
                    # Translate examples if any
                    translated_examples = []
                    original_examples = meaning.get('examples', [])
                    
                    for example in original_examples:
                        translated_example = translator.translate(
                            example, 
                            src='en', 
                            dest=target_lang
                        ).text
                        translated_examples.append(translated_example)
                    
                    translated_meanings.append({
                        'definition': translated_def,
                        'original_definition': original_definition,  # Keep original for reference
                        'pos': meaning.get('pos', ''),  # Keep part of speech in English
                        'examples': translated_examples,
                        'original_examples': original_examples  # Keep original examples
                    })
                
                # Replace English meanings with translated ones
                meanings = translated_meanings
            except Exception as e:
                logger.error(f"Translation error for {text} in {language_code}: {e}")
                # Add a note about translation failure but keep English meanings
                meanings.append({
                    "definition": f"⚠️ Translation to {language_code} failed. Showing English meanings.",
                    "pos": "Note",
                    "error": str(e)
                })
        
        response_data = {
            'word': text,
            'language': language_code,
            'meanings': meanings
        }
        
        if original_translation:
            response_data['translation_info'] = original_translation
            
        if word_details:
            response_data.update({
=======
def get_word_details(request, word):
    """
    Retrieve detailed information about a specific word
    """
    language_code = request.GET.get('language', 'en')
    
    try:
        word_details = ExpectedSpeech.objects.filter(
            word__iexact=word, 
            language__code=language_code
        ).first()
        
        if word_details:
            return JsonResponse({
                'word': word_details.word,
                'language': word_details.language.code,
>>>>>>> 87bc3c2225dfc195908054f0811ab69d497c0cd8
                'category': word_details.category.name if word_details.category else None,
                'pronunciation_hints': word_details.pronunciation_hints or '',
                'difficulty_level': word_details.difficulty_level or 'medium'
            })
<<<<<<< HEAD
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Word details retrieval error: {e}", exc_info=True)
        return JsonResponse({'error': str(e), 'language': language_code}, status=400)
=======
        else:
            return JsonResponse({
                'error': 'Word not found',
                'language': language_code
            }, status=404)
    
    except Exception as e:
        logger.error(f"Word details retrieval error: {e}")
        return JsonResponse({
            'error': str(e),
            'language': language_code
        }, status=400)
>>>>>>> 87bc3c2225dfc195908054f0811ab69d497c0cd8
