import fastapi
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import SessionLocal, engine
import models
from sqlalchemy.orm import Session
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

models.Base.metadata.create_all(bind=engine)

security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Feedback(BaseModel):
    name: str
    email: str
    message: str

app = fastapi.FastAPI()

@app.post("/feedback")
def submit_feedback(name: str=Form(...), email: str=Form(...), message: str=Form(...), db: Session = fastapi.Depends(get_db)):
    new_feedback = models.DataBase(name=name, email=email, message=message)
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return RedirectResponse(url="/thank-you", status_code=303)

@app.get("/send")
def send_feedback(request: fastapi.Request):
    return templates.TemplateResponse(request=request, name="form.html")

@app.get("/view")
def view_feedbacks(request: fastapi.Request, db: Session = fastapi.Depends(get_db), credentials: HTTPBasicCredentials = fastapi.Depends(security)):
    if credentials.username != "admin" or credentials.password != "20120406@adil.com!!":
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")
    
    feedbacks_raw = db.query(models.DataBase).all()
    feedbacks = [{"id": f.id, "name": f.name, "email": f.email, "message": f.message} for f in feedbacks_raw]
    db.query(models.DataBase).order_by(models.DataBase.id.desc()).all()

    return templates.TemplateResponse(
	request=request,
        name="feedbacks.html", 
        context={"feedbacks": feedbacks}
    )

@app.get("/thank-you")
def thank_you(request: fastapi.Request):
    return templates.TemplateResponse(request=request, name="thank.html")

@app.get("/delete/{feedback_id}")
def delete_feedback(feedback_id: int, db: Session = fastapi.Depends(get_db), credentials: HTTPBasicCredentials = fastapi.Depends(security)):
    if credentials.username != "admin" or credentials.password != "20120406@adil.com!!":
        raise fastapi.HTTPException(status_code=401, detail="Unauthorized")
    feedback = db.query(models.DataBase).filter(models.DataBase.id == feedback_id).first()
    if feedback:
        db.delete(feedback)
        db.commit()
    return RedirectResponse(url="/view", status_code=303)

@app.get("/")
def read_root(request: fastapi.Request):
    return templates.TemplateResponse(request=request, name="home.html")
