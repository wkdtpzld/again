from django.contrib import admin
from .models import Question, Answer

class QustionAdmin(admin.ModelAdmin):
    search_fields=['subject']


admin.site.register(Question,QustionAdmin)
admin.site.register(Answer)
