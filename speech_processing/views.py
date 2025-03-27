from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_GET

import speech_recognition as sr
import pronouncing
from gtts import gTTS
import os
import logging
import uuid

from .models import ExpectedSpeech, Category, Language, SpeechRecord

# Configure logging
logger = logging.getLogger(__name__)

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
def recognize_word(request, word):
    """
    Advanced speech recognition with detailed error handling and logging
    """
    language_code = request.GET.get('language', 'en-US')
    request_id = str(uuid.uuid4())  # Unique identifier for tracking
    
    logger.info(f"[{request_id}] Speech Recognition Started - Word: {word}, Language: {language_code}")
    
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.5

    try:
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
    
    # Normalize inputs
    expected = expected.lower().strip()
    spoken = spoken.lower().strip()
    
    # Calculate similarity ratio
    similarity = SequenceMatcher(None, expected, spoken).ratio()
    return round(similarity * 100, 2)


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
                'category': word_details.category.name if word_details.category else None,
                'pronunciation_hints': word_details.pronunciation_hints or '',
                'difficulty_level': word_details.difficulty_level or 'medium'
            })
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