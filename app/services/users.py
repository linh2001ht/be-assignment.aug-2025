from app.repositories.users import UserRepository
from app.models import User, Role
from app.core.security import get_password_hash
from app.schemas import UserUpdate

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_by_id(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        return user

    def get_by_email(self, email: str):
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("User not found.")
        return user

    def get_all(self):
        return self.user_repo.get_all()
    
    def create(self, user_in):
        existing_user = self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise ValueError("Email already exists.")

        user_data = user_in.model_dump()
        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
        user_data["organization_id"] = None
        user_data["role"] = Role.MEMBER
        
        return self.user_repo.create(**user_data)

    def add_to_org(self, user_id: int, org_id: int, role: Role, current_user: User) -> User:
        user = self.get_by_id(user_id)
        if user.organization_id:
            raise ValueError("User already belongs to an organization.")
        if current_user.role != Role.ADMIN and user.id != current_user.id:
            raise ValueError("You do not have permission to add users to this organization.")

        update_data = {"organization_id": org_id, "role": role}
        return self.user_repo.update(user, **update_data)


    def update(self, user_in: UserUpdate, current_user: User) -> User:
        if user_in.email and user_in.email != current_user.email:
            existing_user = self.user_repo.get_by_email(user_in.email)
            if existing_user and existing_user.id != current_user.id:
                raise ValueError("Email already exists.")
        if current_user.organization_id:
            if user_in.organization_id and user_in.organization_id != current_user.organization_id:
                raise ValueError("You cannot change your organization.")
            if user_in.role and user_in.role != current_user.role:
                raise ValueError("You do not have permission to change your role.")

        update_data = user_in.model_dump(exclude_unset=True)
        return self.user_repo.update(current_user, **update_data)

    def change_user_role(self, user_id: int, new_role: Role, current_user: User) -> User:
        if current_user.role != Role.ADMIN:
            raise ValueError("You do not have permission to change user roles.")

        target_user = self.get_by_id(user_id)
        if not target_user:
            raise ValueError("User not found.")

        if target_user.role == Role.ADMIN and current_user.id != target_user.id:
            raise ValueError("You cannot change another Admin's role.")

        if target_user.organization_id != current_user.organization_id:
            raise ValueError("You can only change the role of users in the same organization.")

        target_user.role = new_role
        self.user_repo.db.add(target_user)
        self.user_repo.db.commit()
        self.user_repo.db.refresh(target_user)

        return target_user

    