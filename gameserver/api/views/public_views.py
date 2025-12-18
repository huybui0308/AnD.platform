"""
Public API Views
No authentication required - for scoreboard and public information
"""

import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gameserver.models import Team, Service, ServiceStatus, Tick, Score
from gameserver.api.serializers import (
    ScoreboardTeamSerializer,
    TeamDetailSerializer,
    TickInfoSerializer,
    ServiceSLASerializer
)
from gameserver.api.permissions import AllowAny
from gameserver.api.utils import StandardAPIResponse
from gameserver.config import game_config

logger = logging.getLogger(__name__)


class ScoreboardView(APIView):
    """
    GET /api/scoreboard
    Full scoreboard with all teams
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get full scoreboard
        - List all teams with scores
        - Attack points, defense points, SLA points breakdown
        - Current rankings
        - Last updated timestamp
        """
        try:
            # Get all scores ordered by rank
            scores = Score.objects.select_related('team').filter(
                team__is_active=True,
                team__is_nop_team=False
            ).order_by('rank')
            
            scoreboard_data = []
            for score in scores:
                scoreboard_data.append({
                    'team_id': score.team.id,
                    'team_name': score.team.name,
                    'rank': score.rank,
                    'total_points': score.total_points,
                    'attack_points': score.attack_points,
                    'defense_points': score.defense_points,
                    'sla_points': score.sla_points,
                    'flags_captured': score.flags_captured,
                    'flags_lost': score.flags_lost,
                    'services_up': score.services_up,
                    'services_total': score.services_total,
                    'sla_percentage': score.sla_percentage
                })
            
            serializer = ScoreboardTeamSerializer(scoreboard_data, many=True)
            
            # Get last update time
            last_updated = None
            if scores.exists():
                last_updated = max(s.last_updated for s in scores)
            
            return StandardAPIResponse.success(
                data={
                    'scoreboard': serializer.data,
                    'last_updated': last_updated.isoformat() if last_updated else None,
                    'total_teams': len(scoreboard_data)
                },
                message="Scoreboard retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get scoreboard: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to get scoreboard: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TeamScoreboardDetailView(APIView):
    """
    GET /api/scoreboard/team/{id}
    Single team scoreboard detail
    """
    permission_classes = [AllowAny]
    
    def get(self, request, team_id):
        """
        Get single team scoreboard detail
        - Team name and rank
        - Total score with breakdown
        - Service-by-service SLA
        """
        try:
            # Get team
            try:
                team = Team.objects.get(id=team_id, is_active=True)
            except Team.DoesNotExist:
                return StandardAPIResponse.error(
                    f"Team with id {team_id} not found",
                    status.HTTP_404_NOT_FOUND
                )
            
            # Get team score
            try:
                team_score = Score.objects.get(team=team)
            except Score.DoesNotExist:
                # Create default score if doesn't exist
                team_score = Score.objects.create(team=team)
            
            # Get all services
            services = Service.objects.filter(is_active=True)
            
            # Get latest status for each service
            service_statuses = []
            for service in services:
                # Get the most recent status for this team/service
                latest_status = ServiceStatus.objects.filter(
                    team=team,
                    service=service
                ).order_by('-checked_at').first()
                
                if latest_status:
                    service_statuses.append({
                        'service_id': service.id,
                        'service_name': service.name,
                        'status': latest_status.status,
                        'sla_percentage': latest_status.sla_percentage,
                        'last_check': latest_status.checked_at
                    })
                else:
                    service_statuses.append({
                        'service_id': service.id,
                        'service_name': service.name,
                        'status': 'unknown',
                        'sla_percentage': 0.0,
                        'last_check': None
                    })
            
            # Build response
            data = {
                'team_id': team.id,
                'team_name': team.name,
                'rank': team_score.rank,
                'total_points': team_score.total_points,
                'attack_points': team_score.attack_points,
                'defense_points': team_score.defense_points,
                'sla_points': team_score.sla_points,
                'services': service_statuses
            }
            
            serializer = TeamDetailSerializer(data)
            
            return StandardAPIResponse.success(
                data=serializer.data,
                message="Team detail retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get team detail: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to get team detail: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CurrentTickView(APIView):
    """
    GET /api/tick/current
    Current tick information
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get current tick information
        - Current tick number
        - Tick duration (seconds)
        - Next tick timestamp
        - Game status
        """
        try:
            current_tick = Tick.get_current_tick()
            latest_tick = Tick.get_latest_tick()
            
            if current_tick:
                tick_number = current_tick.tick_number
                game_status = "running"
                
                # Calculate next tick time
                next_tick_time = current_tick.start_time + timedelta(
                    seconds=game_config.TICK_DURATION_SECONDS
                )
            elif latest_tick:
                tick_number = latest_tick.tick_number
                game_status = "stopped"
                next_tick_time = None
            else:
                tick_number = 0
                game_status = "not_started"
                next_tick_time = None
            
            data = {
                'current_tick': tick_number,
                'tick_duration_seconds': game_config.TICK_DURATION_SECONDS,
                'next_tick_time': next_tick_time,
                'game_status': game_status
            }
            
            serializer = TickInfoSerializer(data)
            
            return StandardAPIResponse.success(
                data=serializer.data,
                message="Current tick information retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get current tick: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to get current tick: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
