from django.contrib import admin
from .models import Block


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('x', 'y', 'owner', 'color', 'claimed_at')
    list_filter = ('owner',)
    search_fields = ('owner',)
    ordering = ('y', 'x')
