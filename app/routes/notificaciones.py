from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sns_service import SNSService

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])

sns_service = SNSService()

class NotificationRequest(BaseModel):
    folio: str
    download_link: str

@router.post("/send")
def send_notification(request: NotificationRequest):
    success, detail = sns_service.send_nota_notification(
        folio=request.folio,
        download_link=request.download_link,
    )

    if not success:
        raise HTTPException(status_code=500, detail=f"Error al enviar correo: {detail}")

    return {"message": "Correo enviado con éxito", "message_id": detail}
