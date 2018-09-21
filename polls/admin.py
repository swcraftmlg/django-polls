from django.contrib import admin
from django.utils import timezone

from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'published', 'closed', 'votes']
    list_filter = ['published']
    search_fields = ['text']

    fieldsets = [
        (None, {'fields': ['text']}),
        ('Date information', {
            'fields': ['published', 'closed'],
            'classes': ['collapse'],
        }),
    ]
    inlines = [ChoiceInline]

    actions = ['make_close']

    def make_close(self, request, queryset):
        now = timezone.now()
        queryset.filter(published__lte=now, closed__isnull=True).update(closed=now)

    make_close.short_description = 'Close selected questions'
