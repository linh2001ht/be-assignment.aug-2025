import redis
import json

from .models import Notification
from .config import settings  
from app.database import SessionLocal

redis_client = redis.from_url(settings.redis_url)


def run_notification_worker():

    pubsub = redis_client.pubsub()
    pubsub.subscribe('notifications_channel')
    
    print("Notification worker started. Listening for messages...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            
            db = SessionLocal()
            try:
                event_type = data.get("event_type")
                user_id = data.get("user_id")
                message_text = "A new event has occurred related to you."
                if event_type == "task_assigned":
                    message_text = f"You have been assigned a new task: {data['task_id']}"
                elif event_type == "status_changed":
                    message_text = f"The status of task {data['task_id']} has changed."
                elif event_type == "comment_added":
                    message_text =f"A new comment has been added to your task: {data['task_id']}"
                new_notification = Notification(
                    message=message_text,
                    user_id=user_id,
                )
                db.add(new_notification)
                db.commit()
                                            
            except Exception as e:
                db.rollback()
                print(f"Error: {e}")
            finally:
                db.close()

if __name__ == "__main__":
    run_notification_worker()