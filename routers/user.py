from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database.config import SessionLocal
from database.models import User
from schemas.user import UserCreate, UserLogin, Token
from jose import JWTError, jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/users", tags=["users"])

# Parolni hashlash uchun kontekst
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT yaratish uchun kalitlar
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Ma'lumotlar bazasi sessiyasini olish uchun dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Parolni hashlash funksiyasi
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Yangi foydalanuvchini yaratish funksiyasi
def create_user(db: Session, username: str, email: str, hashed_password: str):
    db_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Foydalanuvchini autentifikatsiya qilish funksiyasi
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# JWT yaratish funksiyasi
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Foydalanuvchini tekshirish
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Parolni hashlash va yangi foydalanuvchini yaratish
    hashed_password = hash_password(user.password)
    user = create_user(db, username=user.username, email=user.email, hashed_password=hashed_password)
    
    # Agar foydalanuvchi yaratilmagan bo‘lsa, xato qaytariladi
    if not user:
        raise HTTPException(status_code=500, detail="User creation failed")
    
    # Access token yaratish
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id}
