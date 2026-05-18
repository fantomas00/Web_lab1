from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Game

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')

class GameSerializer(serializers.ModelSerializer):
    player_x = UserSerializer(read_only=True)
    player_o = UserSerializer(read_only=True)
    current_turn = UserSerializer(read_only=True)

    class Meta:
        model = Game
        fields = '__all__' # Гарантує сумісність і автогенерацію полів у Swagger

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    # Створення ігрової партії за допомогою POST /api/games/
    def create(self, request):
        opponent_id = request.data.get('opponent_id')
        if not opponent_id:
            return Response({"error": "Вкажіть opponent_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        opponent = get_object_or_404(User, id=opponent_id)
        
        game = Game.objects.create(
            player_x=request.user,
            player_o=opponent,
            current_turn=request.user,
            board=" " * 9
        )
        serializer = self.get_serializer(game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Здійснення ігрового ходу через POST /api/games/{id}/move/
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        game = self.get_object()
        if game.is_finished:
            return Response({"error": "Гра вже закінчена"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user != game.current_turn:
            if game.player_x != game.player_o:
                return Response({"error": "Зараз не ваш хід!"}, status=status.HTTP_400_BAD_REQUEST)

        position = request.data.get('position')
        if position is None or not (0 <= int(position) <= 8):
            return Response({"error": "Вкажіть правильну позицію (0-8)"}, status=status.HTTP_400_BAD_REQUEST)
        
        position = int(position)
        board_list = list(game.board)

        if board_list[position] != " ":
            return Response({"error": "Ця клітинка вже зайнята"}, status=status.HTTP_400_BAD_REQUEST)

        symbol = "X" if request.user == game.player_x else "O"
        board_list[position] = symbol
        game.board = "".join(board_list)

        # Валідація переможної комбінації 3х3 на ігровому полі
        win_lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for line in win_lines:
            if board_list[line[0]] == board_list[line[1]] == board_list[line[2]] != " ":
                game.is_finished = True
                game.winner = str(request.user.username)
                break

        if " " not in board_list and not game.is_finished:
            game.is_finished = True
            game.winner = "Draw"

        if not game.is_finished:
            game.current_turn = game.player_o if request.user == game.player_x else game.player_x

        game.save()
        return Response(self.get_serializer(game).data)