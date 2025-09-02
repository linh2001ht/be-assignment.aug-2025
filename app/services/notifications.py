import json
from datetime import datetime
from redis import Redis
from app.schemas import NotificationRead


class NotificationService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    def _get_notification_key(self, user_id: int) -> str:
        return f"notifications:user:{user_id}"

    def create_notification(self, user_id: int, message: str) -> None:
        notification_key = self._get_notification_key(user_id)

        # Use Redis INCR to get a unique ID
        notification_id = self.redis_client.incr("notification:id_counter")

        notification_data = {
            "id": notification_id,
            "message": message,
            "user_id": user_id,
            "is_read": False,
            "created_at": str(datetime.utcnow()),
        }
        self.redis_client.hset(notification_key, str(notification_id), json.dumps(notification_data))

    def get_unread_notifications(self, user_id: int) -> list[NotificationRead]:
        notification_key = self._get_notification_key(user_id)
        notifications = self.redis_client.hgetall(notification_key)
        
        unread_list = []
        for notif_json in notifications.values():
            notif = json.loads(notif_json)
            if not notif["is_read"]:
                unread_list.append(NotificationRead.model_validate(notif))
        return unread_list


    def mark_as_read(self, user_id: int, notification_id: int) -> bool:
        notification_key = self._get_notification_key(user_id)
        notif_json = self.redis_client.hget(notification_key, str(notification_id))

        if not notif_json:
            raise ValueError("Notification not found.")

        notif = json.loads(notif_json)
        notif["is_read"] = True
        
        self.redis_client.hset(notification_key, str(notification_id), json.dumps(notif))

        return True
        