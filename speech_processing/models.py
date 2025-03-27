from django.db import models
from django.utils.translation import gettext_lazy as _

class Language(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    native_name = models.CharField(max_length=50, default='', blank=True)
    is_active = models.BooleanField(default=True)
    flag_code = models.CharField(max_length=10, default='', blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['name']

    @classmethod
    def get_default_language(cls):
        try:
            return cls.objects.get(code='en')
        except cls.DoesNotExist:
            return cls.objects.create(
                code='en', 
                name='English', 
                native_name='English',
                is_active=True
            )

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    language = models.ForeignKey(
        Language, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='categories'
    )

    def __str__(self):
        return f"{self.name} ({self.language.code if self.language else 'No Language'})"

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
        unique_together = ('name', 'language')

    @classmethod
    def get_or_create_default(cls, language):
        default_category, created = cls.objects.get_or_create(
            name='Uncategorized',
            language=language,
            defaults={
                'description': 'Default category for words',
                'order': 0
            }
        )
        return default_category

class ExpectedSpeech(models.Model):
    text = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, 
        related_name='words', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)
    language = models.ForeignKey(
        Language, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='expected_speeches'
    )
    difficulty_level = models.CharField(max_length=50, default="medium")


    def __str__(self):
        return f"{self.text} ({self.language.code if self.language else 'No Language'})"

    class Meta:
        verbose_name_plural = "Expected Speeches"
        unique_together = ('text', 'language')
        ordering = ['order', 'text']

    @classmethod
    def get_word_for_language(cls, word, language_code):
        try:
            return cls.objects.get(
                text__iexact=word, 
                language__code=language_code
)
        except cls.DoesNotExist:
            return None

class SpeechRecord(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expected_speech = models.ForeignKey(
        ExpectedSpeech, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='speech_records'
    )
    language = models.ForeignKey(
        Language, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.text[:50]

    @classmethod
    def create_record(cls, text, expected_speech=None, language=None):
        return cls.objects.create(
            text=text,
            expected_speech=expected_speech,
            language=language
        )