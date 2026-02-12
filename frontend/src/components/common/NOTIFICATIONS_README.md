# Notifications and Alerts System

This directory contains the notification and alert components for the AI Health Intelligence Platform.

## Components

### NotificationCenter
Displays non-intrusive notifications in the top-right corner of the screen.
- Auto-dismisses non-critical notifications after 5 seconds
- All notifications have a dismiss button
- Includes critical error modal support

**Usage:**
```tsx
import { NotificationCenter } from '@/components/common';

// Add to your app layout
<NotificationCenter />
```

### CriticalErrorModal
Modal dialog for critical errors that require user acknowledgment.
- Cannot be dismissed by clicking outside or pressing ESC
- Requires explicit user acknowledgment

**Usage:**
```tsx
import { useNotificationStore } from '@/stores/notificationStore';

const { setCriticalError } = useNotificationStore();

// Trigger critical error
setCriticalError({
  title: 'Critical Error',
  message: 'Something went wrong',
  details: 'Additional error details...'
});
```

### DataQualityAlert
Alert component that displays when data quality score is below 60%.
- Provides suggestions to improve data quality
- Only renders when score < 60%

**Usage:**
```tsx
import { DataQualityAlert } from '@/components/common';

<DataQualityAlert 
  dataQualityScore={45}
  suggestions={['Add more symptoms', 'Include vitals']}
/>
```

### ConfidenceWarning
Prominent warning for LOW confidence assessments.
- Only displays for LOW confidence level
- Provides recommendations for users

**Usage:**
```tsx
import { ConfidenceWarning } from '@/components/common';

<ConfidenceWarning 
  confidence="LOW"
  confidenceScore={42}
/>
```

### SessionMonitor
Component that monitors session expiration and displays warnings.
- Checks token expiration every minute
- Displays warning 5 minutes before expiration
- Automatically refreshes token to extend session

**Usage:**
```tsx
import { SessionMonitor } from '@/components/common';

// Add to your app layout (authenticated routes only)
<SessionMonitor />
```

## Notification Store

The notification store manages all notifications and critical errors.

**Methods:**
- `addNotification(notification)` - Add a new notification
- `removeNotification(id)` - Remove a specific notification
- `clearAll()` - Clear all notifications
- `setCriticalError(error)` - Set a critical error
- `acknowledgeCriticalError()` - Clear the critical error

**Example:**
```tsx
import { useNotificationStore } from '@/stores/notificationStore';

const { addNotification } = useNotificationStore();

addNotification({
  type: 'success',
  message: 'Operation completed successfully',
  dismissible: true
});
```

## Requirements Mapping

- **11.1**: Data quality alerts (DataQualityAlert)
- **11.2**: Confidence warnings (ConfidenceWarning)
- **11.3**: Session expiration warnings (SessionMonitor)
- **11.5**: Non-intrusive notification area (NotificationCenter)
- **11.6**: Dismissible notifications (NotificationCenter)
- **11.7**: Critical error modals (CriticalErrorModal)
