from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import select
from pathlib import Path
from app.db import init_db, get_session
from app.models import User, Policy
from app.auth import hash_password, verify_password, create_access_token, get_current_user, require_admin
from app.pdf_loader import save_uploaded_file, load_and_chunk
from app.rag_pipeline import RAGPipeline
from app.config import DATA_DIR, VECTOR_COLLECTION
from rich import print as rprint
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import RedirectResponse


app = FastAPI(title="Policy MCP + IAM Server (Windows)")
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")


init_db()
RAG = RAGPipeline(collection_name=VECTOR_COLLECTION)

class RegisterRequest(BaseModel):
    full_name: str
    phone: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/register", status_code=201)
def register(req: RegisterRequest):
    session = get_session()
    existing = session.exec(select(User).where(User.email == req.email)).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        full_name=req.full_name,
        phone=req.phone,
        email=req.email,
        hashed_password=hash_password(req.password),
        is_admin=False,
        is_validated=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return {"message": "Registration successful. Awaiting admin validation."}

@app.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    session = get_session()
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        session.close()
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not user.is_validated:
        session.close()
        raise HTTPException(status_code=403, detail="User not validated by admin yet")
    access_token = create_access_token({"sub": user.email})
    session.close()
    return {"access_token": access_token}

@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "phone": user.phone,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_validated": user.is_validated,
        "created_at": user.created_at,
    }

@app.get("/admin/users")
def list_users(admin: User = Depends(require_admin)):
    session = get_session()
    users = session.exec(select(User)).all()
    session.close()
    out = []
    for u in users:
        out.append({
            "id": u.id,
            "full_name": u.full_name,
            "phone": u.phone,
            "email": u.email,
            "is_admin": u.is_admin,
            "is_validated": u.is_validated,
            "created_at": u.created_at,
        })
    return out

@app.post("/admin/validate/{user_id}")
def validate_user(user_id: int, approve: bool = True, admin: User = Depends(require_admin)):
    session = get_session()
    target = session.get(User, user_id)
    if not target:
        session.close()
        raise HTTPException(status_code=404, detail="User not found")
    if approve:
        target.is_validated = True
        session.add(target)
        session.commit()
        session.refresh(target)
        session.close()
        return {"status": "approved", "user_id": user_id}
    else:
        session.delete(target)
        session.commit()
        session.close()
        return {"status": "rejected_and_deleted", "user_id": user_id}

@app.post("/admin/upload_policy")
def upload_policy(file: UploadFile = File(...), admin: User = Depends(require_admin)):
    filename = file.filename
    safe_path = Path(DATA_DIR) / filename
    save_uploaded_file(file, safe_path)
    rprint(f"[green]Policy saved to[/green] {safe_path}")
    chunks = load_and_chunk(str(safe_path))
    collection_name = RAG.initialize_collection(chunks)
    session = get_session()
    pol = Policy(filename=filename, uploaded_by=admin.email, collection_name=collection_name, active=True)
    session.add(pol)
    session.commit()
    session.refresh(pol)
    session.close()
    return {"status": "uploaded", "filename": filename, "collection": collection_name}

class QueryReq(BaseModel):
    question: str

@app.post("/ask")
def ask(req: QueryReq, user: User = Depends(get_current_user)):
    if not user.is_validated:
        raise HTTPException(status_code=403, detail="User not validated")
    res = RAG.answer_query(req.question)
    return res

@app.get("/admin/ui", include_in_schema=False)
def admin_ui():
    return RedirectResponse(url="/static/admin.html")