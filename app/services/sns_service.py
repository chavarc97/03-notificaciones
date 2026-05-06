import boto3
import os
from botocore.exceptions import ClientError


class SNSService:
    def __init__(self):
        # If credentials are provided, use them; otherwise let boto3 use the EC2 instance role
        kwargs = {"region_name": os.getenv("AWS_REGION", "us-east-1")}
        if os.getenv("AWS_ACCESS_KEY_ID"):
            kwargs["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            kwargs["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
            kwargs["aws_session_token"] = os.getenv("AWS_SESSION_TOKEN")
        self.sns_client = boto3.client("sns", **kwargs)
        self.topic_arn = os.getenv("SNS_TOPIC_ARN")
        # If no topic ARN is provided, create/find one
        if not self.topic_arn:
            self.topic_arn = self._create_or_get_topic()

    def _create_or_get_topic(self):
        """Create the SNS topic (idempotent - returns existing if already created)."""
        try:
            response = self.sns_client.create_topic(Name="notas-venta-notifications")
            return response["TopicArn"]
        except ClientError as e:
            print(f"Error creating SNS topic: {e}")
            return None

    def subscribe_email(self, email: str):
        """Subscribe an email to the topic. The subscriber must confirm via email."""
        if not self.topic_arn:
            return False, "No SNS topic available"
        try:
            response = self.sns_client.subscribe(
                TopicArn=self.topic_arn,
                Protocol="email",
                Endpoint=email,
                ReturnSubscriptionArn=True,
            )
            return True, response["SubscriptionArn"]
        except ClientError as e:
            return False, str(e)

    def send_nota_notification(self, folio: str, download_link: str):
        """Publish a notification message to the SNS topic."""
        if not self.topic_arn:
            return False, "No SNS topic available"

        subject = f"Su Nota de Venta {folio} ya esta disponible"
        message = (
            f"Hola,\n\n"
            f"Su nota de venta con folio {folio} ha sido generada.\n\n"
            f"Puede descargarla en el siguiente enlace:\n{download_link}\n\n"
            f"Gracias por su preferencia."
        )

        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message,
            )
            return True, response["MessageId"]
        except ClientError as e:
            return False, str(e)
