import speech_recognition as sr
import pronouncing  # For phoneme comparison
from gtts import gTTS  # For generating correct audio
import os
from django.utils.timezone import now
from .models import SpeechRecord, ExpectedSpeech

def get_phonemes(word):
    """Convert a word into its phoneme representation using CMUdict."""
    words = word.lower().split()  # Handle multi-word phrases
    phoneme_list = [pronouncing.phones_for_word(w) for w in words if pronouncing.phones_for_word(w)]
    return phoneme_list[0][0] if phoneme_list else None  # Take first phoneme result

def generate_audio(word):
    """Generate an audio file for correct pronunciation using Google TTS."""
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)  # ✅ Ensure directory exists
    audio_file = f"{audio_dir}/{word}.mp3"

    # ✅ Generate audio only if not already saved
    if not os.path.exists(audio_file):
        tts = gTTS(text=word, lang='en')
        tts.save(audio_file)

    return f"/static/audio/{word}.mp3"

def recognize_speech(expected_word):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Say: {expected_word}...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        spoken_text = recognizer.recognize_google(audio).lower().strip()
        print("Recognized Speech:", spoken_text)

        expected_phoneme = get_phonemes(expected_word)
        spoken_phoneme = get_phonemes(spoken_text)

        audio_url = generate_audio(expected_word)  # ✅ Get correct pronunciation audio

        if not expected_phoneme or not spoken_phoneme:
            result = f"⚠️ Cannot analyze pronunciation.\n✅ Expected: {expected_word}\n❌ You said: {spoken_text}"
        elif expected_phoneme == spoken_phoneme:
            result = f"✅ Correct pronunciation: {spoken_text}"
        else:
            result = f"❌ Incorrect pronunciation!\n✅ Expected: {expected_word}\n❌ You said: {spoken_text}"

        # ✅ Save recognized speech to database
        SpeechRecord.objects.create(text=spoken_text, created_at=now())

        return result, audio_url

    except sr.UnknownValueError:
        return "❌ Sorry, I couldn't understand that.", None
    except sr.RequestError:
        return "❌ Speech Recognition service is unavailable.", None
