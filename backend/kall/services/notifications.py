from dataclasses import dataclass


@dataclass
class NotificationAction:
    label: str
    deep_link: str


class NotificationService:
    def send_email(self, recipient: str, subject: str, html: str, actions: list[NotificationAction]) -> None:
        print(f"EMAIL to={recipient} subject={subject} actions={actions}")

    def send_push(self, user_id: int, title: str, body: str, actions: list[NotificationAction]) -> None:
        print(f"PUSH user={user_id} title={title} actions={actions}")
