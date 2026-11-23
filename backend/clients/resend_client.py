from exceptions import EmailError, EmailTemporaryError
import resend
from config import get_settings

settings = get_settings()
resend.api_key = settings.resend_api_key


async def send_email(to: str, subject: str, html: str) -> None:
    try:
        params: resend.Emails.SendParams = {
            "from": "Inkdrop <onboarding@resend.dev>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
        await resend.Emails.send_async(params)
    except resend.exceptions.ResendError as e:
        status_code = int(e.code)
        if status_code == 429 or status_code >= 500:
            raise EmailTemporaryError(f"Resend error {status_code}: {e}")
        raise EmailError(f"Resend error {status_code}: {e}")
