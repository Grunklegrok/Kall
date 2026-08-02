# Kall Mobile

React Native/Expo starter boundary.

Primary mobile flows:
- Push notification with match score and compensation
- Review prepared resume and answers
- Confirm sensitive fields
- Approve submission
- Track application status

Recommended bootstrap:

```bash
npx create-expo-app@latest .
```

Use the shared Kall API. Firebase Cloud Messaging should implement the backend
`NotificationService` contract. Deep links should open `/applications/{id}/review`.
