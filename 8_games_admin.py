from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'player_x', 'player_o', 'current_turn', 'is_finished', 'winner')