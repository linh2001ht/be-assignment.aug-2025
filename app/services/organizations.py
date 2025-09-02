from app.repositories.organizations import OrganizationRepository
from app.models import Organization, User, Project, Role
from app.schemas import OrganizationBase
from app.services.users import UserService


class OrganizationService:
    def __init__(self, org_repo: OrganizationRepository, user_service: UserService):
        self.org_repo = org_repo
        self.user_service = user_service

    def create(self, org_in: OrganizationBase, current_user: User) -> Organization:
        if current_user.organization_id:
            raise ValueError("User already belongs to an organization")
        existing_org = self.org_repo.get_by_name(org_in.name)
        if existing_org:
            raise ValueError(f"Organization with name '{org_in.name}' already exists.")
        org_data = org_in.model_dump()
        new_org = self.org_repo.create(**org_data)
        self.user_service.add_to_org(user_id=current_user.id, org_id=new_org.id, role=Role.ADMIN, current_user=current_user)
        return new_org

    def get_by_id(self, org_id: int) -> Organization:
        org = self.org_repo.get_by_id(org_id)
        if not org:
            raise ValueError("Organization not found.")
        return org

    def update(
        self, org_id: int, org_in: OrganizationBase, current_user: User
    ) -> Organization:
        organization = self.get_by_id(org_id)
    
        if (
            current_user.role != Role.ADMIN
            or current_user.organization_id != organization.id
        ):
            raise ValueError("You do not have permission to update this organization.")

        updated_org = self.org_repo.update(organization, **org_in.model_dump())
        return updated_org

    def delete(self, org_id: int, current_user: User) -> None:
        organization = self.get_by_id(org_id)

        if (
            current_user.role != Role.ADMIN
            or current_user.organization_id != organization.id
        ):
            raise ValueError("You do not have permission to delete this organization.")

        if (
            self.org_repo.db.query(Project)
            .filter(Project.organization_id == org_id)
            .first()
        ):
            raise ValueError("Cannot delete organization while projects exist.")

        self.org_repo.delete(organization)

    def get_all(self) -> list[Organization]:
        return self.org_repo.get_all()

    def list_users(self, org_id: int, current_user: User) -> list[User]:
        organization = self.get_by_id(org_id)

        if current_user.organization_id != organization.id:
            raise ValueError("You do not have permission to list users in this organization.")

        return organization.users

    def add_user(self, org_id: int, user_id: int, role: Role, current_user: User) -> User:
        organization = self.get_by_id(org_id)

        if current_user.role != Role.ADMIN or current_user.organization_id != organization.id:
            raise ValueError("You do not have permission to add users to this organization.")

        target_user = self.user_service.add_to_org(user_id=user_id, org_id=organization.id, role=role, current_user=current_user)

        return target_user