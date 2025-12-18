# REST API Documentation

This document describes the REST API endpoints for the Attack & Defense CTF platform.

## Overview

The API provides two types of endpoints:
- **Internal Management APIs** (`/internal/*`) - Require authentication (admin/staff only)
- **Public APIs** (`/api/*`) - No authentication required

All responses follow a standardized format:

```json
{
  "success": true/false,
  "data": { ... },
  "message": "Success message or error description",
  "timestamp": "2025-12-18T07:00:00.000Z"
}
```

## Authentication

Internal management APIs require authentication. Use Django session authentication or basic authentication:

```bash
# Using session authentication (requires CSRF token)
curl -X POST http://localhost:8000/internal/game/start \
  -H "Cookie: sessionid=your_session_id" \
  -H "X-CSRFToken: your_csrf_token"

# Using basic authentication
curl -X POST http://localhost:8000/internal/game/start \
  -u username:password
```

## Internal Management APIs

### 1. Start Game

**Endpoint:** `POST /internal/game/start`  
**Authentication:** Required (admin/staff)  
**Description:** Initialize game state, start tick counter, and enable checker services

**Request:**
```bash
curl -X POST http://localhost:8000/internal/game/start -u admin:password
```

**Response:**
```json
{
  "success": true,
  "data": {
    "start_time": "2025-12-18T07:00:00.000Z",
    "tick_number": 1,
    "tick_duration": 60
  },
  "message": "Game started successfully",
  "timestamp": "2025-12-18T07:00:00.000Z"
}
```

**Error Cases:**
- `400 Bad Request` - Game is already running
- `401 Unauthorized` - Authentication required
- `500 Internal Server Error` - Failed to start game

---

### 2. Stop Game

**Endpoint:** `POST /internal/game/stop`  
**Authentication:** Required (admin/staff)  
**Description:** Stop tick counter, freeze scoreboard, and stop checker services

**Request:**
```bash
curl -X POST http://localhost:8000/internal/game/stop -u admin:password
```

**Response:**
```json
{
  "success": true,
  "data": {
    "stop_time": "2025-12-18T08:00:00.000Z",
    "last_tick": 60
  },
  "message": "Game stopped successfully",
  "timestamp": "2025-12-18T08:00:00.000Z"
}
```

**Error Cases:**
- `400 Bad Request` - Game is not running
- `401 Unauthorized` - Authentication required
- `500 Internal Server Error` - Failed to stop game

---

### 3. Get Game Status

**Endpoint:** `GET /internal/game/status`  
**Authentication:** Required (admin/staff)  
**Description:** Get current game status including tick number, game state, and timing information

**Request:**
```bash
curl http://localhost:8000/internal/game/status -u admin:password
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "current_tick": 15,
    "game_status": "running",
    "start_time": "2025-12-18T07:00:00.000Z",
    "next_tick_time": "2025-12-18T07:15:00.000Z",
    "tick_duration_seconds": 60
  },
  "message": "Game status retrieved successfully",
  "timestamp": "2025-12-18T07:14:30.000Z"
}
```

**Game Status Values:**
- `running` - Game is active
- `stopped` - Game was running but has been stopped
- `not_started` - Game has never been started

---

### 4. Reload Checkers

**Endpoint:** `POST /internal/checker/reload`  
**Authentication:** Required (admin/staff)  
**Description:** Hot-reload checker modules from gameserver/checker/

**Request:**
```bash
curl -X POST http://localhost:8000/internal/checker/reload -u admin:password
```

**Response:**
```json
{
  "success": true,
  "data": {
    "loaded_checkers": ["WebService", "DatabaseService", "APIService"],
    "count": 3,
    "errors": []
  },
  "message": "Loaded 3 checkers",
  "timestamp": "2025-12-18T07:14:30.000Z"
}
```

**Notes:**
- If a checker fails to load, it will be listed in the `errors` array
- Successfully loaded checkers are listed in `loaded_checkers`

---

### 5. Get Team Status

**Endpoint:** `GET /internal/teams/{id}/status`  
**Authentication:** Required (admin/staff)  
**Description:** Get detailed status for a specific team including all services and SLA

**Request:**
```bash
curl http://localhost:8000/internal/teams/1/status -u admin:password
```

**Response:**
```json
{
  "success": true,
  "data": {
    "team_id": 1,
    "team_name": "TeamAlpha",
    "rank": 1,
    "total_points": 5000,
    "attack_points": 2000,
    "defense_points": 1500,
    "sla_points": 1500,
    "services": [
      {
        "service_id": 1,
        "service_name": "WebService",
        "status": "up",
        "sla_percentage": 95.5,
        "last_check": "2025-12-18T07:14:00.000Z"
      },
      {
        "service_id": 2,
        "service_name": "DatabaseService",
        "status": "down",
        "sla_percentage": 0.0,
        "last_check": "2025-12-18T07:14:00.000Z"
      }
    ]
  },
  "message": "Team status retrieved successfully",
  "timestamp": "2025-12-18T07:14:30.000Z"
}
```

**Error Cases:**
- `404 Not Found` - Team with given ID does not exist
- `401 Unauthorized` - Authentication required

---

## Public APIs

### 6. Get Scoreboard

**Endpoint:** `GET /api/scoreboard`  
**Authentication:** Not required  
**Description:** Get full scoreboard with all teams, scores, and rankings

**Request:**
```bash
curl http://localhost:8000/api/scoreboard
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scoreboard": [
      {
        "team_id": 1,
        "team_name": "TeamAlpha",
        "rank": 1,
        "total_points": 5000,
        "attack_points": 2000,
        "defense_points": 1500,
        "sla_points": 1500,
        "flags_captured": 40,
        "flags_lost": 10,
        "services_up": 3,
        "services_total": 3,
        "sla_percentage": 100.0
      },
      {
        "team_id": 2,
        "team_name": "TeamBeta",
        "rank": 2,
        "total_points": 4200,
        "attack_points": 1800,
        "defense_points": 1200,
        "sla_points": 1200,
        "flags_captured": 36,
        "flags_lost": 12,
        "services_up": 2,
        "services_total": 3,
        "sla_percentage": 66.7
      }
    ],
    "last_updated": "2025-12-18T07:14:00.000Z",
    "total_teams": 2
  },
  "message": "Scoreboard retrieved successfully",
  "timestamp": "2025-12-18T07:14:30.000Z"
}
```

**Notes:**
- Teams are ordered by rank (best first)
- Only active, non-NOP teams are included
- `sla_percentage` is calculated as (services_up / services_total) * 100

---

### 7. Get Team Scoreboard Detail

**Endpoint:** `GET /api/scoreboard/team/{id}`  
**Authentication:** Not required  
**Description:** Get detailed scoreboard information for a specific team

**Request:**
```bash
curl http://localhost:8000/api/scoreboard/team/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "team_id": 1,
    "team_name": "TeamAlpha",
    "rank": 1,
    "total_points": 5000,
    "attack_points": 2000,
    "defense_points": 1500,
    "sla_points": 1500,
    "services": [
      {
        "service_id": 1,
        "service_name": "WebService",
        "status": "up",
        "sla_percentage": 95.5,
        "last_check": "2025-12-18T07:14:00.000Z"
      },
      {
        "service_id": 2,
        "service_name": "DatabaseService",
        "status": "up",
        "sla_percentage": 98.2,
        "last_check": "2025-12-18T07:14:00.000Z"
      }
    ]
  },
  "message": "Team detail retrieved successfully",
  "timestamp": "2025-12-18T07:14:30.000Z"
}
```

**Error Cases:**
- `404 Not Found` - Team with given ID does not exist or is not active

---

### 8. Get Current Tick

**Endpoint:** `GET /api/tick/current`  
**Authentication:** Not required  
**Description:** Get current tick information and game status

**Request:**
```bash
curl http://localhost:8000/api/tick/current
```

**Response (Game Running):**
```json
{
  "success": true,
  "data": {
    "current_tick": 15,
    "tick_duration_seconds": 60,
    "next_tick_time": "2025-12-18T07:15:00.000Z",
    "game_status": "running"
  },
  "message": "Current tick information retrieved successfully",
  "timestamp": "2025-12-18T07:14:30.000Z"
}
```

**Response (Game Stopped):**
```json
{
  "success": true,
  "data": {
    "current_tick": 60,
    "tick_duration_seconds": 60,
    "next_tick_time": null,
    "game_status": "stopped"
  },
  "message": "Current tick information retrieved successfully",
  "timestamp": "2025-12-18T08:00:30.000Z"
}
```

**Response (Game Not Started):**
```json
{
  "success": true,
  "data": {
    "current_tick": 0,
    "tick_duration_seconds": 60,
    "next_tick_time": null,
    "game_status": "not_started"
  },
  "message": "Current tick information retrieved successfully",
  "timestamp": "2025-12-18T06:59:30.000Z"
}
```

---

## Error Response Format

All error responses follow the same format:

```json
{
  "success": false,
  "data": {},
  "message": "Error description",
  "timestamp": "2025-12-18T07:14:30.000Z"
}
```

Common HTTP status codes:
- `200 OK` - Request successful
- `400 Bad Request` - Invalid request or operation not allowed
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Data Models

### Team
- `id` (integer) - Team ID
- `name` (string) - Team name
- `ip_address` (string) - Team IP address
- `is_active` (boolean) - Whether team is active

### Service
- `id` (integer) - Service ID
- `name` (string) - Service name
- `status` (string) - Current status: `up`, `down`, `corrupted`, `unknown`
- `sla_percentage` (float) - SLA percentage (0-100)

### Score Breakdown
- `attack_points` (integer) - Points from capturing flags
- `defense_points` (integer) - Points from defending flags
- `sla_points` (integer) - Points from service availability
- `total_points` (integer) - Sum of all points

---

## Testing the API

### Using curl

```bash
# Public API (no auth)
curl http://localhost:8000/api/scoreboard

# Internal API (with basic auth)
curl -u admin:password http://localhost:8000/internal/game/status

# POST request
curl -X POST -u admin:password http://localhost:8000/internal/game/start
```

### Using Python

```python
import requests

# Public API
response = requests.get('http://localhost:8000/api/scoreboard')
data = response.json()

# Internal API with authentication
response = requests.get(
    'http://localhost:8000/internal/game/status',
    auth=('admin', 'password')
)
data = response.json()
```

### Using JavaScript

```javascript
// Public API
fetch('http://localhost:8000/api/scoreboard')
  .then(response => response.json())
  .then(data => console.log(data));

// Internal API with credentials
fetch('http://localhost:8000/internal/game/status', {
  credentials: 'include',  // For session auth
  headers: {
    'Authorization': 'Basic ' + btoa('admin:password')
  }
})
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## Rate Limiting

Currently, there is no rate limiting implemented on the API endpoints. In production, consider implementing rate limiting to prevent abuse.

## CORS Configuration

CORS is not configured by default. If you need to access the API from a different origin, add `django-cors-headers` to your setup and configure it appropriately.

---

## Questions or Issues?

For questions or issues related to the API, please consult the main documentation or create an issue in the repository.
