from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
import uuid

app = FastAPI()

# دیتابیس ساده برای مثال
users_db = {}

class User(BaseModel):
    telegram_id: str
    name: Optional[str] = ""
    ref_code: Optional[str] = None

@app.post("/register")
async def register(user: User):
    if user.telegram_id in users_db:
        return users_db[user.telegram_id]
    
    ref_link = str(uuid.uuid4())[:8]
    inviter_id = None

    # اگه از طریق لینک دعوت ثبت‌نام کرده
    if user.ref_code:
        for u_id, u_data in users_db.items():
            if u_data["ref_link"] == user.ref_code:
                inviter_id = u_id
                users_db[u_id]["score"] += 10  # به معرف ۱۰ امتیاز بده

    users_db[user.telegram_id] = {
        "name": user.name,
        "ref_link": ref_link,
        "invited_by": inviter_id,
        "score": 0,
        "invited": []
    }

    if inviter_id:
        users_db[inviter_id]["invited"].append(user.telegram_id)

    return users_db[user.telegram_id]

@app.get("/referrals/{telegram_id}")
async def get_referrals(telegram_id: str):
    user = users_db.get(telegram_id)
    if not user:
        return JSONResponse(status_code=404, content={"message": "کاربر یافت نشد"})
    return user
