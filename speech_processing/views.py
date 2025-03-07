from django.shortcuts import render
from django.http import JsonResponse
import speech_recognition as sr
import pronouncing
from gtts import gTTS
import os

# Add this line to import both models
from .models import ExpectedSpeech, Category



# ✅ Display Words for Practice
# views.py
def practice_words(request):
    # Get all categories with their words
    categories = Category.objects.all().prefetch_related('words')
    
    # Also get any uncategorized words (if any exist in your database)
    uncategorized_words = ExpectedSpeech.objects.filter(category__isnull=True)
    
    return render(request, 'speech_processing/practice.html', {
        'categories': categories,
        'uncategorized_words': uncategorized_words
    })

def recognize_word(request, word):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        spoken_text = recognizer.recognize_google(audio, language="en-US").strip().lower()
        print("Recognized Speech:", spoken_text)

        if not spoken_text:
            return JsonResponse({"message": "❌ No speech detected. Try speaking clearly into the microphone."})

        expected_word = word.strip().lower()
        audio_url = generate_audio(word)  # 🔊 Correct pronunciation audio

        response_data = {
            "expected_word": word,
            "spoken_word": spoken_text,
            "audio_url": audio_url
        }

        # ✅ Step 1: Ensure we send ONLY one response
        if expected_word == spoken_text:
            response_data["message"] = f"✅ Expected: {word}<br>✅ You said: {spoken_text}"
        else:
            response_data["message"] = f"✅ Expected: {word}<br>❌ You said: {spoken_text}<br>🔊 Correct Pronunciation Plays"

        # ✅ Return only one response
        return JsonResponse(response_data)

    except sr.UnknownValueError:
        return JsonResponse({"message": "❌ Could not understand. Please speak clearly."})
    except sr.RequestError:
        return JsonResponse({"message": "⚠️ Speech Recognition service unavailable."})

# ✅ Generate & Return Correct Pronunciation Audio
from django.conf import settings
def generate_audio(word):
    """Generate and return correct pronunciation audio file URL."""
    
    audio_dir = os.path.join(settings.BASE_DIR, "static", "audio")

    os.makedirs(audio_dir, exist_ok=True)  # ✅ Ensure directory exists

    audio_path = os.path.join(audio_dir, f"{word}.mp3")

    tts = gTTS(word, lang='en')
    tts.save(audio_path)  # ✅ Always generate the latest pronunciation

    return f"/static/audio/{word}.mp3"  # ✅ Return audio file path

# ✅ Django View to Serve Audio URL
def get_audio(request, word):
    """Return the correct pronunciation audio file URL."""
    audio_url = generate_audio(word)  # ✅ Ensure audio file is generated
    return JsonResponse({"audio_url": audio_url})

# ✅ Play the correct pronunciation audio
def play_audio(request, word):
    audio_url = f"/static/audio/{word}.mp3"
    return JsonResponse({"audio_url": audio_url})  # ✅ Return URL for the audio file
