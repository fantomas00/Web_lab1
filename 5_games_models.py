from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    # Зв'язки Foreign Key з таблицею User
    player_x = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_x')
    player_o = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games_as_o')
    
    # Поле board з 9 символів для збереження стану сітки 3x3
    board = models.CharField(max_length=9, default=" " * 9) 
    
    current_turn = models.ForeignKey(User, on_delete=models.CASCADE, related_name='current_games')
    is_finished = models.BooleanField(default=False)
    winner = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"Game {self.id}: {self.player_x.username} vs {self.player_o.username}"