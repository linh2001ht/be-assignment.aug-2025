from app.repositories.projects import ProjectRepository
from app.services.users import UserService
from app.models import User, Project
from app.schemas import ProjectBase
from app.models.enums import Role

class ProjectService:
    def __init__(self, project_repo: ProjectRepository, user_service: UserService):
        self.project_repo = project_repo
        self.user_service = user_service

    def create_project(self, project_in: ProjectBase, current_user: User) -> Project:
        if current_user.role not in [Role.ADMIN, Role.MANAGER]:
            raise ValueError("You do not have permission to create a project.")

        project_data = project_in.model_dump()
        project_data["organization_id"] = current_user.organization_id

        new_project = self.project_repo.create_with_member(current_user, **project_data)

        return new_project
    
    def get_by_id(self, project_id: int, current_user: User) -> Project:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found.")
        
        if current_user not in project.users: 
            raise ValueError("You do not have permission to access this project.")
        return project
    
    def get_all(self, current_user: User) -> list[Project]:
        return self.project_repo.get_by_organization(current_user.organization_id)

    def update(self, project_id: int, project_in: ProjectBase, current_user: User) -> Project:
        project = self.get_by_id(project_id, current_user)
        
        if current_user.role not in [Role.ADMIN, Role.MANAGER] and current_user not in project.users:
            raise ValueError("You do not have permission to update this project.")

        update_data = project_in.model_dump(exclude_unset=True)
        return self.project_repo.update(project, **update_data)

    def delete(self, project_id: int, current_user: User) -> None:
        project = self.get_by_id(project_id, current_user)
        
        if current_user.role != Role.ADMIN:
            raise ValueError("You do not have permission to delete this project.")

        self.project_repo.delete(project)

    def list_members(self, project_id: int, current_user: User) -> list[User]:
        project = self.get_by_id(project_id, current_user)
        return project.users

    def add_member(self, project_id: int, user_id: int, current_user: User) -> User:
        if current_user.role not in [Role.ADMIN, Role.MANAGER]:
            raise ValueError("You do not have permission to add members.")

        project = self.get_by_id(project_id, current_user)

        user = self.user_service.get_by_id(user_id)
        
        if user.organization_id != current_user.organization_id:
            raise ValueError("User does not belong to your organization.")

        if user in project.users:
            raise ValueError("User is already a member of the project.")

        return self.project_repo.add_user(project, user)

    def remove_member(self, project_id: int, user_id: int, current_user: User) -> None:
        if current_user.role not in [Role.ADMIN, Role.MANAGER]:
            raise ValueError("You do not have permission to remove members.")

        project = self.get_by_id(project_id, current_user)

        user = self.user_service.get_by_id(user_id)

        if user not in project.users:
            raise ValueError("User is not a member of the project.")

        self.project_repo.remove_user(project, user)