from fastapi import APIRouter , Depends , HTTPException , status , Response
from sqlalchemy.orm import Session 
from app.models import Parent , Child 
from app.schemas import ParentResponse , ParentCreate , ChildResponse , ChildCreate , LoginRequest
from app.auth import hash_password , verify_password , create_access_token , get_current_user
from app.database import get_db
from typing import List
router = APIRouter(prefix="/auth", tags=["Authentication"])

#starting with the first route the sign up for parents

@router.post("/register/parent" , response_model = ParentResponse , status_code= status.HTTP_201_CREATED)
def registerParent(data : ParentCreate , db : Session = Depends(get_db)):
    #first we need to check if the user already exists
    user = db.query(Parent).filter(Parent.email == data.email).first()
    if user:
       raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Email already registered")
    #now that the user does not exist we generate a hashed password
    hash_pass = hash_password(data.password)
    new_user = Parent(email = data.email , fullName = data.fullName ,hashed_password = hash_pass , username= data.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

#sign up for children 

@router.post("/register/child", response_model = ChildResponse , status_code = status.HTTP_201_CREATED)
def registerChild(data : ChildCreate , db : Session = Depends(get_db)):
    #first we check if the child exists
    user = db.query(Child).filter(Child.email == data.email).first()
    if user :
       raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST , detail ="email already registered")
    #else we create the hashed password
    hash_pwd = hash_password(data.password)
    parent = db.query(Parent).filter(Parent.username == data.parent_username).first()
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent not found")
    new_user = Child(email = data.email , username= data.childUsername ,fullName = data.fullName , hashed_password = hash_pwd , parent_id = int(parent.id))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 
    

@router.post("/login/parent")
def loginParent(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    # 1. Fetch user
    user = db.query(Parent).filter(Parent.email == data.email).first()
    
    # 2. Check existence BEFORE checking password hash
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials"
        )
        
    # 3. Generate token & set HttpOnly cookie
    token = create_access_token(data={"sub": str(user.id), "role": "parent"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=7200,
        samesite="lax",
        secure=False
    )
    return {"message": "Login successful Parent 🥳🥳"}


# ==========================================
# CHILD LOGIN
# ==========================================
@router.post("/login/child")
def loginChild(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    # 1. Fetch user using .first()
    user = db.query(Child).filter(Child.email == data.email).first() # ✅ Added .first()
    
    # 2. Check existence BEFORE checking password hash
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Credentials"
        )
        
    # 3. Generate token & set HttpOnly cookie
    token = create_access_token(data={"sub": str(user.id), "role": "child"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=7200,
        samesite="lax",
        secure=False
    )
    return {"message": "Login successful Child 🥳🥳"}


# ==========================================
# LOGOUT
# ==========================================
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}  


@router.get("/getAllParents", response_model=List[ParentResponse])
def getAllParents(db: Session = Depends(get_db)):
    parents = db.query(Parent).all()
    return parents

@router.get("/getAllChildren", response_model=List[ChildResponse])
def getAllChildren(db: Session = Depends(get_db)):
    children = db.query(Child).all()
    return children