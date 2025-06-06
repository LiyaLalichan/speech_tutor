# In speech_processing/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Language, ExpectedSpeech,SpeechRecord

# Your existing Language and Category admin classes remain the same

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'native_name', 'is_active', 'flag_code')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'native_name')
    list_editable = ('is_active',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'language_display', 'order', 'description_short', 'word_count')
    list_filter = ('language__name',)  # Filter by language name
    search_fields = ('name', 'description')
    list_editable = ('order',)
    
    # Group by language in the change list
    list_per_page = 50
    
    def get_queryset(self, request):
        # Order by language first, then by name
        return super().get_queryset(request).select_related('language').order_by('language__name', 'order', 'name')
    
    def language_display(self, obj):
        if obj.language:
            return format_html(
                '<span style="display: inline-block; padding: 2px 6px; background-color: #f0f0f0; border-radius: 3px;">{}</span>',
                obj.language.name
            )
        return "No Language"
    language_display.short_description = "Language"
    language_display.admin_order_field = 'language__name'
    
    def description_short(self, obj):
        if obj.description and len(obj.description) > 30:
            return obj.description[:30] + "..."
        return obj.description or "-"
    description_short.short_description = "Description"
    
    def word_count(self, obj):
        count = obj.words.count()
        if count > 0:
            return format_html('<span style="font-weight: bold;">{}</span>', count)
        return "0"
    word_count.short_description = "Words"
    
    # Custom admin form layout
    fieldsets = (
        (None, {
            'fields': ('name', 'language', 'order')
        }),
        ('Additional Information', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    
    # Add list action to copy categories to another language
    actions = ['duplicate_to_language']
    
    def duplicate_to_language(self, request, queryset):
        # Implementation for duplicating categories
        pass
    duplicate_to_language.short_description = "Duplicate selected categories to another language"


@admin.register(ExpectedSpeech)
class ExpectedSpeechAdmin(admin.ModelAdmin):
    list_display = ('text', 'translation', 'category_display', 'language_display', 
                    'difficulty_level', 'order')
    list_filter = ('language', 'category', 'difficulty_level')
    search_fields = ('text', 'translation')
    list_editable = ('order', 'difficulty_level')
    autocomplete_fields = ['category']
    
    def language_display(self, obj):
        if obj.language:
            return format_html(
                '<span style="display: inline-block; padding: 2px 6px; background-color: #f0f0f0; border-radius: 3px;">{}</span>',
                obj.language.name
            )
        return "No Language"
    language_display.short_description = "Language"
    language_display.admin_order_field = 'language__name'
    
    def category_display(self, obj):
        if obj.category:
            return obj.category.name
        return "Uncategorized"
    category_display.short_description = "Category"
    
    fieldsets = (
        (None, {
            'fields': ('text', 'translation', 'language', 'category', 'difficulty_level', 'order')
        }),
    )
    
    # Optional: Add bulk import action
    actions = ['bulk_import_words']
    
    def bulk_import_words(self, request, queryset):
        # You can implement CSV import functionality here
        pass
    bulk_import_words.short_description = "Import words from CSV"

# Optionally, you can also register the SpeechRecord model
@admin.register(SpeechRecord)
class SpeechRecordAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'expected_speech', 'language', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('text', 'expected_speech__text')
    readonly_fields = ('created_at',)
    
    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = "Speech Text"