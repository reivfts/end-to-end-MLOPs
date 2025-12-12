# Admin Notification System

## Overview
The admin notification system tracks all actions across the microservices platform and sends detailed notifications to all admin users. Each notification includes:
- **Timestamp**: When the action occurred (UTC ISO format)
- **Actor**: Who performed the action (name and user ID)
- **Action Type**: What type of action was performed
- **Affected Entity**: What was changed and who was affected

## Notification Format
All admin notifications follow this format:
```
[YYYY-MM-DDTHH:MM:SS.ffffffZ] Actor Name (ID: actor-id...): Action description
```

Example:
```
[2025-12-12T15:30:45.123456Z] Kevin Admin (ID: admin-00...): Deleted Rei Student's booking for Room 101 on 2025-12-15 at 10:00 AM - 12:00 PM
```

## Tracked Actions

### User Management Service (Port 8002)

#### User Created
- **Type**: `user_created`
- **Trigger**: Admin creates a new user
- **Message Format**: "Created new {role} user: {name} ({email})"
- **Example**: "Created new student user: John Doe (john@example.com)"

#### User Updated
- **Type**: `user_updated`
- **Trigger**: Admin or user updates profile information
- **Message Format**: "Updated user {name} ({email}): changed {fields}"
- **Example**: "Updated user Jane Smith (jane@example.com): changed role to 'faculty'"

#### User Deleted
- **Type**: `user_deleted`
- **Trigger**: Admin deletes a user account
- **Message Format**: "Deleted user: {email}"
- **Example**: "Deleted user: olduser@example.com"

### Booking Service (Port 8001)

#### Booking Created
- **Type**: `booking_created`
- **Trigger**: Any user creates a room booking
- **Message Format**: "{actor} created a booking for {room} on {date} at {time_slot}"
- **Example**: "Kevin Admin created a booking for Room 201 on 2025-12-15 at 2:00 PM - 4:00 PM"

#### Booking Deleted
- **Type**: `booking_deleted`
- **Trigger**: User deletes their own booking OR admin/faculty deletes any booking
- **Message Format (self-delete)**: "{actor} deleted their own booking for {room} on {date} at {time_slot}"
- **Message Format (admin delete)**: "{actor} deleted {user}'s booking for {room} on {date} at {time_slot}"
- **Example**: "Faculty User deleted Rei Student's booking for Room 101 on 2025-12-20 at 6:00 PM - 8:00 PM"

### Maintenance Service (Port 8080)

#### Maintenance Ticket Created
- **Type**: `maintenance_created`
- **Trigger**: Any user submits a maintenance request
- **Message Format**: "{actor} created a new maintenance ticket (Priority: {score}): {description}"
- **Example**: "Student User created a new maintenance ticket (Priority: 8.5): Broken AC in Room 305..."

#### Maintenance Ticket Updated
- **Type**: `maintenance_updated`
- **Trigger**: User or admin updates ticket status
- **Message Format**: "{actor} updated ticket status from '{old_status}' to '{new_status}' for: {description}"
- **Example**: "Faculty User updated ticket status from 'open' to 'in-progress' for: Leaking faucet in bathroom..."

#### Maintenance Ticket Deleted
- **Type**: `maintenance_deleted`
- **Trigger**: User deletes their own ticket OR admin deletes any ticket
- **Message Format (self-delete)**: "{actor} deleted their own maintenance ticket: {description}"
- **Message Format (admin delete)**: "{actor} deleted {user}'s maintenance ticket: {description}"
- **Example**: "Admin User deleted John Doe's maintenance ticket: Flickering lights in hallway..."

## Implementation Details

### Notification Service Endpoint
**POST** `/notifications/admin`

**Headers**:
```json
{
  "Authorization": "Bearer <jwt_token>",
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "type": "action_type",
  "message": "Action description",
  "actor_name": "User Name",
  "actor_id": "uuid-string"
}
```

**Response**:
```json
{
  "message": "Notified N admin(s)",
  "notificationIds": ["uuid1", "uuid2", ...]
}
```

### Service Integration

Each microservice includes a `notify_admins()` helper function:

```python
def notify_admins(action_type: str, message: str, actor_name: str, actor_id: str, token: str):
    """Send notification to all admin users"""
    try:
        requests.post(
            f'{NOTIFICATION_SERVICE}/notifications/admin',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={
                'type': action_type,
                'message': message,
                'actor_name': actor_name,
                'actor_id': actor_id
            },
            timeout=2
        )
    except Exception as e:
        print(f"Failed to notify admins: {e}")
```

### Admin Detection
The notification service automatically:
1. Queries the User Management Service for all users
2. Filters users where `role == 'admin'`
3. Creates individual notifications for each admin
4. Excludes the actor if they are an admin (to avoid self-notification)

### Fallback Mechanism
If the User Management Service is unavailable, the system falls back to a hardcoded list of known admin IDs: `['admin-001']`

## Testing the System

### 1. Login as Admin
```bash
# Navigate to the gateway
http://localhost:5001

# Login with admin credentials
Email: admin@example.com
Password: admin123
```

### 2. Perform Actions to Generate Notifications

#### Test User Creation
1. Go to "User Management"
2. Click "Add New User"
3. Create a test user
4. Check Notifications - should see: "Created new student user: Test User (test@example.com)"

#### Test Booking Creation (as student)
1. Login as student (student@example.com / student123)
2. Go to "Room Booking"
3. Create a booking
4. Login back as admin
5. Check Notifications - should see: "Student User created a booking for..."

#### Test Booking Deletion (admin deleting student booking)
1. As admin, go to "Room Booking"
2. Delete a student's booking
3. Check Notifications - should see: "Admin User deleted Student User's booking for..."

#### Test Maintenance Ticket
1. Login as student
2. Go to "Maintenance"
3. Submit a ticket
4. Login as admin
5. Check Notifications - should see: "Student User created a new maintenance ticket..."

### 3. View Notifications
Navigate to the Notifications page to see all admin notifications with:
- Full timestamp
- Actor information
- Complete action details

## Database Schema

### Notifications Table
```sql
CREATE TABLE notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,        -- Admin's user ID
    type TEXT NOT NULL,            -- Action type (e.g., 'user_created')
    message TEXT NOT NULL,         -- Full formatted message with timestamp
    read BOOLEAN DEFAULT 0,        -- Read/unread status
    created_at TEXT NOT NULL       -- Notification creation time
)
```

## Benefits

1. **Full Audit Trail**: Admins can see every action in the system
2. **Accountability**: Every action is tied to a specific user
3. **Real-time Monitoring**: Admins are notified immediately when actions occur
4. **Detailed Context**: Notifications include who performed the action and who was affected
5. **Timestamp Precision**: All actions are timestamped to the microsecond

## Future Enhancements

1. **Email Notifications**: Send emails to admins for critical actions
2. **Notification Filtering**: Allow admins to filter by action type or date
3. **Action Reversal**: Add "undo" functionality for certain actions
4. **Dashboard Analytics**: Show statistics on most common actions
5. **Severity Levels**: Categorize actions by importance (info, warning, critical)
