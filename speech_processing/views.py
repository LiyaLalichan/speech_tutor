from django.shortcuts import render
from django.http import JsonResponse
import speech_recognition as sr
import pronouncing
from gtts import gTTS
import os



from .models import ExpectedSpeech

# ✅ View to display words for practice
def practice_words(request):
    words = ExpectedSpeech.objects.all()
    return render(request, 'speech_processing/practice.html', {'words': words})


# ✅ Speech Recognition and Pronunciation Checking
def recognize_word(request, word):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        spoken_text = recognizer.recognize_google(audio).lower()
        print("Recognized Speech:", spoken_text)

        expected_phonemes = pronouncing.phones_for_word(word.lower())
        spoken_phonemes = pronouncing.phones_for_word(spoken_text.split()[0])

        audio_url = generate_audio(word)  # Generate correct pronunciation audio

        response_data = {
            "expected_word": word,
            "spoken_word": spoken_text,
            "audio_url": audio_url
        }

        if not expected_phonemes or not spoken_phonemes:
            response_data["message"] = "Could not analyze pronunciation."
        elif expected_phonemes[0] == spoken_phonemes[0]:
            response_data["message"] = f"✅ Expected: {word}\n✅ You said: {spoken_text}"
        else:
            response_data["message"] = f"✅ Expected: {word}\n❌ You said: {spoken_text}\n🔊 Correct Pronunciation Audio Plays"

        return JsonResponse(response_data)

    except sr.UnknownValueError:
        return JsonResponse({"message": "Sorry, I couldn't understand that."})
    except sr.RequestError:
        return JsonResponse({"message": "Speech Recognition service is unavailable."})


# ✅ Generate and Return Correct Pronunciation Audio
def generate_audio(request, word):
    """Generate correct pronunciation audio and return its URL."""
    audio_dir = os.path.join("static", "audio")
    os.makedirs(audio_dir, exist_ok=True)  # ✅ Ensure the directory exists

    audio_path = os.path.join(audio_dir, f"{word}.mp3")

    # ✅ Generate audio only if it does not exist
    if not os.path.exists(audio_path):
        tts = gTTS(word, lang='en')
        tts.save(audio_path)

    return JsonResponse({"audio_url": f"/static/audio/{word}.mp3"})  # ✅ Return correct URL
