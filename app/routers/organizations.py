from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas import OrganizationRead, OrganizationBase, UserRead
from app.dependencies import get_current_user, get_organization_service, get_current_user_no_org, require_role
from app.models import Role
from app.services.organizations import OrganizationService

router = APIRouter(prefix="/orgs")

@router.get("/", response_model=list[OrganizationRead])
def list_organizations(organization_service: OrganizationService = Depends(get_organization_service)):
    try:
        return organization_service.get_all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=OrganizationRead)
def create_organization(organization_in: OrganizationBase, current_user: User = Depends(get_current_user_no_org), organization_service: OrganizationService = Depends(get_organization_service)):
    try:
        return organization_service.create(organization_in, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{org_id}", response_model=OrganizationRead)
def read_organization(org_id: int, organization_service: OrganizationService = Depends(get_organization_service)):
    try:
        return organization_service.get_by_id(org_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{org_id}", response_model=OrganizationRead)
def update_organization(org_id: int, organization_in: OrganizationBase, current_user: User = Depends(require_role(Role.ADMIN)), organization_service: OrganizationService = Depends(get_organization_service)):
    try:
        return organization_service.update(org_id, organization_in, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/{org_id}", status_code=204)
def delete_organization(org_id: int, current_user: User = Depends(require_role(Role.ADMIN)), organization_service: OrganizationService = Depends(get_organization_service)):
    try:
        organization_service.delete(org_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{org_id}/users", response_model=list[UserRead])
def list_users(org_id: int, current_user: User = Depends(get_current_user), organization_service: OrganizationService = Depends(get_organization_service)):
    try:
        return organization_service.list_users(org_id, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{org_id}/users", response_model=UserRead, status_code=201)
def add_user_to_org(org_id: int, user_id: int, role: Role, current_user: User = Depends(require_role(Role.ADMIN)), organization_service: OrganizationService = Depends(get_organization_service)):
    try:
        return organization_service.add_user(org_id, user_id, role, current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

