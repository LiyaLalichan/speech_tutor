from speech_processing.models import ExpectedSpeech

# List of words to add
words = ["hello", "good morning", "thank you", "congratulations", "welcome", "beautiful", "sunshine"]

# Add each word if it doesn't exist
for word in words:
    if not ExpectedSpeech.objects.filter(text=word).exists():
        ExpectedSpeech.objects.create(text=word)

print("✅ Words added successfully!")

#exec(open("word.py").read())

