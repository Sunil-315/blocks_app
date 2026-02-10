from django.shortcuts import render


def game(request):
    """Render the block claiming game."""
    return render(request, 'blocks/game.html')
