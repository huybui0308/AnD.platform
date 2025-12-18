"""
API URL Configuration
Routes for both internal management and public APIs
"""

from django.urls import path
from gameserver.api.views.internal_views import (
    GameStartView,
    GameStopView,
    GameStatusView,
    CheckerReloadView,
    TeamStatusView
)
from gameserver.api.views.public_views import (
    ScoreboardView,
    TeamScoreboardDetailView,
    CurrentTickView
)

# Internal Management APIs (require authentication)
internal_patterns = [
    path('game/start', GameStartView.as_view(), name='game-start'),
    path('game/stop', GameStopView.as_view(), name='game-stop'),
    path('game/status', GameStatusView.as_view(), name='game-status'),
    path('checker/reload', CheckerReloadView.as_view(), name='checker-reload'),
    path('teams/<int:team_id>/status', TeamStatusView.as_view(), name='team-status'),
]

# Public APIs (no authentication)
public_patterns = [
    path('scoreboard', ScoreboardView.as_view(), name='scoreboard'),
    path('scoreboard/team/<int:team_id>', TeamScoreboardDetailView.as_view(), name='team-scoreboard-detail'),
    path('tick/current', CurrentTickView.as_view(), name='current-tick'),
]

urlpatterns = internal_patterns + public_patterns
