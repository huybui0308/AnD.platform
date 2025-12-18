"""
Internal Management API Views
Requires authentication - only for admin/staff users
"""

import logging
import importlib
import sys
from datetime import timedelta

from django.utils import timezone
from django.db.models import Q, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from gameserver.models import Team, Service, ServiceStatus, Tick, Score
from gameserver.api.serializers import (
    GameStatusSerializer,
    ServiceStatusSerializer,
    TeamDetailSerializer,
    ServiceSLASerializer
)
from gameserver.api.permissions import IsAdminOrStaff
from gameserver.config import game_config

logger = logging.getLogger(__name__)


class StandardAPIResponse:
    """
    Helper class to standardize API responses
    """
    
    @staticmethod
    def success(data=None, message="Success"):
        """Return successful response"""
        return Response({
            'success': True,
            'data': data or {},
            'message': message,
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    @staticmethod
    def error(message, status_code=status.HTTP_400_BAD_REQUEST, data=None):
        """Return error response"""
        return Response({
            'success': False,
            'data': data or {},
            'message': message,
            'timestamp': timezone.now().isoformat()
        }, status=status_code)


class GameStartView(APIView):
    """
    POST /internal/game/start
    Start the CTF game
    """
    permission_classes = [IsAdminOrStaff]
    
    def post(self, request):
        """
        Start the game
        - Initialize game state
        - Start tick counter
        - Enable checker services
        """
        try:
            # Check if game is already running
            current_tick = Tick.get_current_tick()
            if current_tick:
                return StandardAPIResponse.error(
                    "Game is already running",
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Create the first tick
            start_time = timezone.now()
            tick = Tick.objects.create(
                tick_number=1,
                start_time=start_time,
                duration_seconds=game_config.TICK_DURATION_SECONDS,
                status=Tick.STATUS_ACTIVE
            )
            
            logger.info(f"Game started at {start_time} with tick {tick.tick_number}")
            
            return StandardAPIResponse.success(
                data={
                    'start_time': start_time.isoformat(),
                    'tick_number': tick.tick_number,
                    'tick_duration': game_config.TICK_DURATION_SECONDS
                },
                message="Game started successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to start game: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to start game: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GameStopView(APIView):
    """
    POST /internal/game/stop
    Stop the CTF game
    """
    permission_classes = [IsAdminOrStaff]
    
    def post(self, request):
        """
        Stop the game
        - Stop tick counter
        - Freeze scoreboard
        - Stop checker services
        """
        try:
            # Get current tick and complete it
            current_tick = Tick.get_current_tick()
            if not current_tick:
                return StandardAPIResponse.error(
                    "Game is not running",
                    status.HTTP_400_BAD_REQUEST
                )
            
            stop_time = timezone.now()
            current_tick.complete()
            
            logger.info(f"Game stopped at {stop_time}")
            
            return StandardAPIResponse.success(
                data={
                    'stop_time': stop_time.isoformat(),
                    'last_tick': current_tick.tick_number
                },
                message="Game stopped successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to stop game: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to stop game: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GameStatusView(APIView):
    """
    GET /internal/game/status
    Get current game status
    """
    permission_classes = [IsAdminOrStaff]
    
    def get(self, request):
        """
        Get current game status
        - Current tick number
        - Game status (running/stopped/paused)
        - Start time
        - Next tick timestamp
        """
        try:
            current_tick = Tick.get_current_tick()
            latest_tick = Tick.get_latest_tick()
            
            if current_tick:
                is_running = True
                game_status = "running"
                tick_number = current_tick.tick_number
                start_time = current_tick.start_time
                
                # Calculate next tick time
                next_tick_time = start_time + timedelta(
                    seconds=game_config.TICK_DURATION_SECONDS
                )
            elif latest_tick:
                is_running = False
                game_status = "stopped"
                tick_number = latest_tick.tick_number
                start_time = latest_tick.start_time
                next_tick_time = None
            else:
                is_running = False
                game_status = "not_started"
                tick_number = None
                start_time = None
                next_tick_time = None
            
            data = {
                'is_running': is_running,
                'current_tick': tick_number,
                'game_status': game_status,
                'start_time': start_time,
                'next_tick_time': next_tick_time,
                'tick_duration_seconds': game_config.TICK_DURATION_SECONDS
            }
            
            serializer = GameStatusSerializer(data)
            
            return StandardAPIResponse.success(
                data=serializer.data,
                message="Game status retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get game status: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to get game status: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CheckerReloadView(APIView):
    """
    POST /internal/checker/reload
    Reload checker scripts
    """
    permission_classes = [IsAdminOrStaff]
    
    def post(self, request):
        """
        Hot-reload checker modules
        - Reload checker modules from gameserver/checker/
        - Validate checker scripts
        - Return count of loaded checkers
        """
        try:
            loaded_checkers = []
            errors = []
            
            # Get all services with checker scripts
            services = Service.objects.filter(is_active=True)
            
            for service in services:
                try:
                    # Reload the checker module
                    module_name = service.checker_script
                    
                    if module_name in sys.modules:
                        importlib.reload(sys.modules[module_name])
                        loaded_checkers.append(service.name)
                        logger.info(f"Reloaded checker for {service.name}")
                    else:
                        # Try to import it
                        importlib.import_module(module_name)
                        loaded_checkers.append(service.name)
                        logger.info(f"Loaded checker for {service.name}")
                        
                except Exception as e:
                    error_msg = f"Failed to load checker for {service.name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            return StandardAPIResponse.success(
                data={
                    'loaded_checkers': loaded_checkers,
                    'count': len(loaded_checkers),
                    'errors': errors
                },
                message=f"Loaded {len(loaded_checkers)} checkers"
            )
            
        except Exception as e:
            logger.error(f"Failed to reload checkers: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to reload checkers: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TeamStatusView(APIView):
    """
    GET /internal/teams/{id}/status
    Get team service status
    """
    permission_classes = [IsAdminOrStaff]
    
    def get(self, request, team_id):
        """
        Get team service status
        - Team information
        - List of all services with their status
        - SLA percentage per service
        - Last check timestamp
        """
        try:
            # Get team
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                return StandardAPIResponse.error(
                    f"Team with id {team_id} not found",
                    status.HTTP_404_NOT_FOUND
                )
            
            # Get team score
            try:
                team_score = Score.objects.get(team=team)
                rank = team_score.rank
                total_points = team_score.total_points
                attack_points = team_score.attack_points
                defense_points = team_score.defense_points
                sla_points = team_score.sla_points
            except Score.DoesNotExist:
                rank = 0
                total_points = 0
                attack_points = 0
                defense_points = 0
                sla_points = 0
            
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
                'rank': rank,
                'total_points': total_points,
                'attack_points': attack_points,
                'defense_points': defense_points,
                'sla_points': sla_points,
                'services': service_statuses
            }
            
            serializer = TeamDetailSerializer(data)
            
            return StandardAPIResponse.success(
                data=serializer.data,
                message="Team status retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get team status: {e}", exc_info=True)
            return StandardAPIResponse.error(
                f"Failed to get team status: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
