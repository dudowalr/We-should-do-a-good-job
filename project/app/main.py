from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routers import predict, feedback, csv_analysis, chat


app = FastAPI(title="Cyber Threat Prediction API")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h1>서버 정상 작동!</h1>"

app.include_router(predict.router, prefix="/predict", tags=["Predict"])
app.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
app.include_router(csv_analysis.router, prefix="/csv-analysis", tags=["CSV Analysis"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

