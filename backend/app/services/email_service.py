from brevo import Brevo
from brevo.transactional_emails import (SendTransacEmailRequestSender,SendTransacEmailRequestToItem,)

from app.core.config import get_settings

def build_verification_email(recipient_name: str,verification_url: str,) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify your MealQ account</title>
    </head>

    <body style="
        margin: 0;
        padding: 0;
        background-color: #f7f7f7;
        font-family: Arial, Helvetica, sans-serif;
        color: #292524;
    ">

        <div style="
            max-width: 600px;
            margin: 40px auto;
            padding: 0 20px;
        ">

            <div style="
                background-color: #ffffff;
                padding: 24px 32px;
                border-radius: 14px 14px 0 0;
                border-bottom: 1px solid #f1f1f1;
            ">
                <div style="
                    font-size: 24px;
                    font-weight: 800;
                    color: #f97316;
                ">
                    MealQ
                </div>
            </div>

            <div style="
                background-color: #ffffff;
                padding: 40px 32px;
            ">

                <h1 style="
                    margin: 0 0 20px;
                    font-size: 26px;
                    line-height: 1.3;
                    color: #292524;
                ">
                    Verify your MealQ account
                </h1>

                <p style="
                    margin: 0 0 16px;
                    font-size: 15px;
                    line-height: 1.6;
                ">
                    Hi {recipient_name},
                </p>

                <p style="
                    margin: 0 0 24px;
                    font-size: 15px;
                    line-height: 1.6;
                    color: #57534e;
                ">
                    Welcome to MealQ. Please verify your email address
                    to activate your account and continue using MealQ.
                </p>

                <div style="
                    text-align: center;
                    margin: 30px 0;
                ">
                    <a
                        href="{verification_url}"
                        style="
                            display: inline-block;
                            padding: 14px 28px;
                            background-color: #f97316;
                            color: #ffffff;
                            text-decoration: none;
                            border-radius: 8px;
                            font-size: 15px;
                            font-weight: 700;
                        "
                    >
                        Verify My Account
                    </a>
                </div>

                <p style="
                    margin: 0 0 16px;
                    font-size: 14px;
                    line-height: 1.6;
                    color: #57534e;
                ">
                    If you did not create a MealQ account,
                    you can safely ignore this email.
                </p>

                <p style="
                    margin: 24px 0 8px;
                    font-size: 13px;
                    line-height: 1.5;
                    color: #78716c;
                ">
                    If the button does not work, copy and paste
                    the following link into your browser:
                </p>

                <p style="
                    margin: 0;
                    font-size: 12px;
                    line-height: 1.5;
                    word-break: break-all;
                    color: #f97316;
                ">
                    {verification_url}
                </p>

            </div>

            <div style="
                background-color: #fafaf9;
                padding: 24px 32px;
                border-radius: 0 0 14px 14px;
                text-align: center;
            ">

                <p style="
                    margin: 0;
                    font-size: 12px;
                    color: #78716c;
                ">
                    © MealQ
                </p>

            </div>

        </div>

    </body>
    </html>
    """
    
def send_email(to: str, subject: str, body: str) -> None:
    settings = get_settings()

    if not settings.BREVO_API_KEY:
        raise RuntimeError("BREVO_API_KEY is not configured")

    if not settings.BREVO_SENDER_EMAIL:
        raise RuntimeError("BREVO_SENDER_EMAIL is not configured")

    client = Brevo(api_key=settings.BREVO_API_KEY)

    try:
        client.transactional_emails.send_transac_email(
            subject=subject,
            html_content=body,
            sender=SendTransacEmailRequestSender(
                name=settings.BREVO_SENDER_NAME,
                email=settings.BREVO_SENDER_EMAIL,
            ),
            to=[
                SendTransacEmailRequestToItem(
                    email=to,
                )
            ],
        )
    except Exception as exc:
        raise RuntimeError(f"Brevo email failed: {exc}") from exc