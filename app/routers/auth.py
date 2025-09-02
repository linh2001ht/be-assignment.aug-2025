from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserCreate, Token, UserRead
from app.services.users import UserService
from app.core.security import verify_password
from app.dependencies import get_user_service, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, user_service: UserService = Depends(get_user_service)):
    try:
        user = user_service.create(user_in)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service)):
    user = user_service.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}
