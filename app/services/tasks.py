from typing import Any
from app.repositories.tasks import TaskRepository
from app.services.projects import ProjectService
from app.services.notifications import NotificationService
from app.models import Task
from app.schemas import TaskCreate, TaskRead, TaskStatusUpdate
from app.models import User, Role, TaskStatus, Priority
from datetime import date
import json
from redis import Redis


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        project_service: ProjectService,
        redis_client: Redis,
        notification_service: NotificationService,
    ):
        self.task_repo = task_repo
        self.project_service = project_service
        self.redis_client = redis_client
        self.notification_service = notification_service

    def get_by_id(self, task_id: int, current_user) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Task not found.")
        # Check if the user has access to the project
        self.project_service.get_by_id(task.project_id, current_user)
        return task

    def _get_cache_key(self, project_id: int) -> str:
        return f"tasks:project:{project_id}"

    def _invalidate_cache(self, project_id: int) -> None:
        cache_key = self._get_cache_key(project_id)
        self.redis_client.delete(cache_key)

    def get_tasks_in_project(self, project_id: int, current_user: User, status: TaskStatus | None = None,
        assignee_id: int | None = None,
        priority: Priority | None = None,) -> list[Task]:
        cache_key = self._get_cache_key(project_id)
        cached_data = self.redis_client.get(cache_key)

        project = self.project_service.get_by_id(project_id, current_user)
        if not any([status, assignee_id, priority]):
            cache_key = self._get_cache_key(project.id)
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                # The data is in the cache, return it after deserializing.
                tasks_data = json.loads(cached_data)
                return [TaskRead.model_validate(task_dict).model_dump() for task_dict in tasks_data]

            tasks = self.task_repo.get_filtered_tasks(project_id=project.id)
            task_list_json = [TaskRead.model_validate(task).model_dump_json() for task in tasks]
            self.redis_client.set(cache_key, json.dumps(task_list_json), ex=300) # Expire in 5 minutes
            return tasks
        
        return self.task_repo.get_filtered_tasks(
            project_id=project.id,
            status=status,
            assignee_id=assignee_id,
            priority=priority,
        )


    def create_task(self, project_id: int, task_in: TaskCreate, current_user: User) -> Task:
        project = self.project_service.get_by_id(project_id, current_user)
    
        # Business Rule: Due date must be today or in the future
        if task_in.due_date and task_in.due_date < date.today():
            raise ValueError("Due date must be today or in the future.")

        task_data = task_in.model_dump()
        task_data["project_id"] = project_id

        assignee = next((user for user in project.users if user.id == task_in.assignee_id), None)

        if not assignee:
            raise ValueError("Assignee not a member of the project.")
        
        # Business Rule: Only Admin/Manager can assign to others
        if assignee.id != current_user.id and current_user.role not in [
            Role.ADMIN,
            Role.MANAGER,
            ]:
            raise ValueError("You can only assign tasks to yourself.")

        new_task = self.task_repo.create(**task_data)

        # Notify assignee
        self.notification_service.create_notification(
            user_id=assignee.id,
            message=f"You have been assigned a new task '{new_task.title}'.",
        )
        # Invalidate the current user's cache
        self._invalidate_cache(project.id)
        return new_task

    def update_assignee(self, task_id: int, assignee_id: int, current_user: User) -> Task:
        task = self.get_by_id(task_id, current_user)

        assignee = next((user for user in task.project.users if user.id == assignee_id), None)

        if not assignee:
            raise ValueError("Assignee not a member of the project.")
        
        # Business Rule: Only Admin/Manager can assign to others
        if assignee.id != current_user.id and current_user.role not in [
            Role.ADMIN,
            Role.MANAGER,
            ]:
            raise ValueError("You can only assign tasks to yourself.")

        task.assignee_id = assignee.id
        updated_task = self.task_repo.update(task, assignee_id=assignee.id)

        # Notify assignee
        self.notification_service.create_notification(
            user_id=assignee.id,
            message=f"You have been assigned a new task '{updated_task.title}'.",
        )

        return updated_task

    def update_task_status(
        self, task_id: int, task_in: TaskStatusUpdate, current_user: User
    ) -> Task:
        task = self.get_by_id(task_id, current_user)

        # Business Rule: Status can only progress forward
        status_order = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE]
        current_index = status_order.index(task.status)
        new_index = status_order.index(task_in.status)
        if new_index < current_index:
            raise ValueError("Status can only progress forward.")

        task.status = task_in.status
        updated_task = self.task_repo.update(task, status=task_in.status)

        self._invalidate_cache(task.project_id)

        if updated_task.assignee_id:
            self.notification_service.create_notification(
                user_id=updated_task.assignee_id,
                message=f"Task '{updated_task.title}' status has changed.",
            )

        return updated_task

    def delete_task(self, task_id: int, current_user: User) -> None:
        task = self.get_by_id(task_id, current_user)
        self.task_repo.delete(task)
        self._invalidate_cache(task.project_id)

    def get_status_report(self, project_id: int, current_user: User) -> list[dict[str, Any]]:
        self.project_service.get_by_id(project_id, current_user)
        return self.task_repo.get_count_by_status(project_id)

    def get_overdue_tasks_in_project(self, project_id: int, current_user: User) -> list[Task]:
        self.project_service.get_by_id(project_id, current_user)
        return self.task_repo.get_overdue(project_id)