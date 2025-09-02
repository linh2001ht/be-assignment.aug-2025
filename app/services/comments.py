from app.models.enums import Role
from app.repositories.comments import CommentRepository
from app.services.tasks import TaskService
from app.services.notifications import NotificationService
from app.models import Comment
from app.schemas import CommentBase
from app.models import User


class CommentService:
    def __init__(
        self,
        comment_repo: CommentRepository,
        task_service: TaskService,
        notification_service: NotificationService,
    ):
        self.comment_repo = comment_repo
        self.task_service = task_service
        self.notification_service = notification_service

    def get_by_id(self, comment_id: int, current_user: User) -> Comment:
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
        self.task_service.get_by_id(comment.task_id, current_user)
        return comment

    def list_comments(self, task_id: int, current_user: User) -> list[Comment]:
        self.task_service.get_by_id(task_id, current_user)
        return self.comment_repo.get_by_task(task_id)

    def add_comment(
        self, task_id: int, comment_in: CommentBase, current_user: User
    ) -> Comment:
        task = self.task_service.get_by_id(task_id, current_user)

        comment_data = comment_in.model_dump()
        comment_data["task_id"] = task_id
        comment_data["user_id"] = current_user.id

        new_comment = self.comment_repo.create(**comment_data)

        # Notify assignee that a comment has been added
        self.notification_service.create_notification(
            user_id=task.assignee_id, message=f"New comment on task '{task.title}'"
        )

        return new_comment
    
    def delete_comment(self, comment_id: int, current_user: User) -> None:
        comment = self.get_by_id(comment_id)
      
        if comment.user_id != current_user.id and current_user.role != Role.ADMIN:
            raise ValueError("You do not have permission to delete this comment.")

        self.comment_repo.delete(comment_id)
