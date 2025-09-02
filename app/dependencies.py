from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import redis
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import settings
from app.database import get_db
from app.models import User, Role

from app.config import settings
from app.repositories.attachments import AttachmentRepository
from app.repositories.comments import CommentRepository
from app.repositories.organizations import OrganizationRepository
from app.repositories.projects import ProjectRepository
from app.repositories.users import UserRepository
from app.repositories.tasks import TaskRepository
from app.services.attachments import AttachmentService
from app.services.comments import CommentService
from app.services.notifications import NotificationService
from app.services.organizations import OrganizationService
from app.services.projects import ProjectService
from app.services.tasks import TaskService
from app.services.users import UserService

redis_pool = redis.from_url(settings.redis_url, decode_responses=True)


def get_redis_client():
    return redis_pool


# -- Repositories Dependencies --
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_organization_repo(db: Session = Depends(get_db)) -> OrganizationRepository:
    return OrganizationRepository(db)


def get_project_repo(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_task_repo(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)


def get_comment_repo(db: Session = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)


def get_attachment_repo(db: Session = Depends(get_db)) -> AttachmentRepository:
    return AttachmentRepository(db)


# -- Services Dependencies --
# Services depend on Repositories, so we inject them here.
# Note the correct dependency flow to avoid circular imports.


def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


def get_organization_service(
    organization_repo: OrganizationRepository = Depends(get_organization_repo),
    user_service: UserService = Depends(get_user_service),
) -> OrganizationService:
    return OrganizationService(organization_repo, user_service)


def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
    user_service: UserService = Depends(get_user_service),
) -> ProjectService:
    return ProjectService(project_repo, user_service)


def get_notification_service(
    redis_client: redis.Redis = Depends(get_redis_client),
) -> NotificationService:
    return NotificationService(redis_client)


def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repo),
    project_service: ProjectService = Depends(get_project_service),
    redis_client: redis.Redis = Depends(get_redis_client),
    notification_service: NotificationService = Depends(get_notification_service),
) -> TaskService:
    return TaskService(task_repo, project_service, redis_client, notification_service)


def get_comment_service(
    comment_repo: CommentRepository = Depends(get_comment_repo),
    task_service: TaskService = Depends(get_task_service),
    notification_service: NotificationService = Depends(get_notification_service),
) -> CommentService:
    return CommentService(comment_repo, task_service, notification_service)


def get_attachment_service(
    attachment_repo: AttachmentRepository = Depends(get_attachment_repo),
    task_service: TaskService = Depends(get_task_service),
) -> AttachmentService:
    return AttachmentService(attachment_repo, task_service)


def get_object_or_404(db: Session, model: any, obj_id: int):
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found.")
    return obj


def create_access_token(data: dict, expires_delta: int | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_delta or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _get_user_from_token(token: str, db: Session) -> User:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


def get_current_user_no_org(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    return _get_user_from_token(token, db)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    user = _get_user_from_token(token, db)
    if not user.organization_id:
        raise HTTPException(
            status_code=403,
            detail="You must belong to an organization to access this resource.",
        )
    return user


def require_role(*roles: Role):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker
