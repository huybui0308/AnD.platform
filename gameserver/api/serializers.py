"""
Serializers for REST API
Converts Django models to JSON and validates input
"""

from rest_framework import serializers
from gameserver.models import Team, Tick, Service, ServiceStatus, Score


class TeamSerializer(serializers.ModelSerializer):
    """
    Basic team information serializer
    """
    class Meta:
        model = Team
        fields = ['id', 'name', 'ip_address', 'is_active', 'is_nop_team']
        read_only_fields = ['id']


class TickSerializer(serializers.ModelSerializer):
    """
    Tick/round information serializer
    """
    actual_duration = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Tick
        fields = [
            'id', 'tick_number', 'start_time', 'end_time', 
            'duration_seconds', 'status', 'flags_placed', 
            'flags_checked', 'checker_errors', 'actual_duration'
        ]
        read_only_fields = ['id', 'actual_duration']


class ServiceSerializer(serializers.ModelSerializer):
    """
    Service definition serializer
    """
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'port', 'is_active',
            'user_flag_points', 'root_flag_points', 'sla_points_per_tick'
        ]
        read_only_fields = ['id']


class ServiceStatusSerializer(serializers.ModelSerializer):
    """
    Service status with SLA information
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = ServiceStatus
        fields = [
            'id', 'team_name', 'service_name', 'status', 
            'user_flag_placed', 'root_flag_placed',
            'user_flag_retrieved', 'root_flag_retrieved',
            'sla_percentage', 'check_duration_ms', 
            'error_message', 'checked_at'
        ]
        read_only_fields = ['id']


class ScoreSerializer(serializers.ModelSerializer):
    """
    Score information serializer
    """
    team_name = serializers.CharField(source='team.name', read_only=True)
    sla_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Score
        fields = [
            'team_name', 'attack_points', 'defense_points', 
            'sla_points', 'total_points', 'rank',
            'flags_captured', 'flags_lost', 
            'services_up', 'services_total', 
            'sla_percentage', 'last_updated'
        ]


class ScoreboardTeamSerializer(serializers.Serializer):
    """
    Full scoreboard entry for a team
    """
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    rank = serializers.IntegerField()
    total_points = serializers.IntegerField()
    attack_points = serializers.IntegerField()
    defense_points = serializers.IntegerField()
    sla_points = serializers.IntegerField()
    flags_captured = serializers.IntegerField()
    flags_lost = serializers.IntegerField()
    services_up = serializers.IntegerField()
    services_total = serializers.IntegerField()
    sla_percentage = serializers.FloatField()


class ServiceSLASerializer(serializers.Serializer):
    """
    Service-specific SLA information
    """
    service_id = serializers.IntegerField()
    service_name = serializers.CharField()
    status = serializers.CharField()
    sla_percentage = serializers.FloatField()
    last_check = serializers.DateTimeField()


class TeamDetailSerializer(serializers.Serializer):
    """
    Detailed team information with per-service SLA
    """
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    rank = serializers.IntegerField()
    total_points = serializers.IntegerField()
    attack_points = serializers.IntegerField()
    defense_points = serializers.IntegerField()
    sla_points = serializers.IntegerField()
    services = ServiceSLASerializer(many=True)


class GameStatusSerializer(serializers.Serializer):
    """
    Current game state information
    """
    is_running = serializers.BooleanField()
    current_tick = serializers.IntegerField(allow_null=True)
    game_status = serializers.CharField()
    start_time = serializers.DateTimeField(allow_null=True)
    next_tick_time = serializers.DateTimeField(allow_null=True)
    tick_duration_seconds = serializers.IntegerField()


class TickInfoSerializer(serializers.Serializer):
    """
    Current tick information for public API
    """
    current_tick = serializers.IntegerField()
    tick_duration_seconds = serializers.IntegerField()
    next_tick_time = serializers.DateTimeField(allow_null=True)
    game_status = serializers.CharField()
