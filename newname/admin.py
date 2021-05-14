from django.contrib import admin
from .models import Name, Kanjidata, FortuneTelling

# Register your models here.

class KanjidataAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,{'fields': ['id', 'figure']}),
        ('Stroke Data', {'fields': ['stroke']}),
        ('Kanji Type', {'fields': ['joyo', 'jinmeiyo', 'kana', 'kigou']}),
        ('Reading Data', {'fields': ['reading_onyomi', 'reading_kunyomi']}),
        ('Mean Data', {'fields': ['mean']}),        
        ('Count Data', {'fields': ['search_count', 'p_impression_count', 'n_impression_count']}),        
    ]
    list_display = ('id', 'figure')
    search_fields = ['figure']
    list_filter = ['joyo', 'jinmeiyo', 'kana', 'kigou']

admin.site.register(Name)
admin.site.register(Kanjidata, KanjidataAdmin)
admin.site.register(FortuneTelling)