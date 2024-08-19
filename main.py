import uvicorn
from fastapi import FastAPI
from routers import todo_router, index_router,user_router
from database.config import Base, engine
from fastapi.middleware.cors import CORSMiddleware

# Ma'lumotlar bazasi jadvallarini yaratish
Base.metadata.create_all(bind=engine)

# FastAPI ilovasini yaratish
app = FastAPI()

origins = [
    "http://localhost:3000",  # Frontend ilovangizning URL manzili
    "http://127.0.0.1:3000",   # Agar boshqa portda bo'lsa
    # Boshqa kerakli domenlar yoki manzillarni qo'shishingiz mumkin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Qaysi manzillardan kelgan so'rovlarni ruxsat berish
    allow_credentials=True,  # Cookie'larni o'z ichiga olgan so'rovlarni ruxsat berish
    allow_methods=["*"],     # Hamma HTTP metodlarni ruxsat berish (GET, POST, va boshqalar)
    allow_headers=["*"],     # Hamma header'larni ruxsat berish
)

# Routerlarni ulash
app.include_router(todo_router)
app.include_router(index_router)
app.include_router(user_router)

if __name__ == "__main__":
    # Uvicorn orqali ilovani ishga tushirish
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
