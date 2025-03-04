import speech_recognition as sr
import pronouncing  # For phoneme comparison
from gtts import gTTS  # For generating correct audio
import os
from django.utils.timezone import now
from .models import SpeechRecord, ExpectedSpeech

def get_phonemes(word):
    """Convert a word into its phoneme representation using CMUdict."""
    phoneme_list = pronouncing.phones_for_word(word.lower())
    return phoneme_list[0] if phoneme_list else None

def generate_audio(word):
    """Generate an audio file for correct pronunciation using Google TTS."""
    tts = gTTS(text=word, lang='en')
    audio_file = f"static/audio/{word}.mp3"  # Save in a static directory
    tts.save(audio_file)
    return f"/static/audio/{word}.mp3"

def recognize_speech(expected_word):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Say: {expected_word}")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        spoken_text = recognizer.recognize_google(audio).lower()
        print("Recognized Speech:", spoken_text)

        # Get phonemes
        expected_phoneme = get_phonemes(expected_word)
        spoken_phoneme = get_phonemes(spoken_text)

        # Check pronunciation similarity
        if expected_phoneme and spoken_phoneme and expected_phoneme == spoken_phoneme:
            result = f"✅ Correct pronunciation: {spoken_text}"
        else:
            result = f"❌ Incorrect pronunciation! You said: {spoken_text}"

        # Save result to database
        SpeechRecord.objects.create(text=spoken_text, created_at=now())

        return result, generate_audio(expected_word)

    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that.", None
    except sr.RequestError:
        return "Speech Recognition service is unavailable.", None
