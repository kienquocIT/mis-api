from firebase_admin.messaging import Message, Notification, send


def send_fcm_notification(token, title, body):
    message = Message(
        token=token,
        notification=Notification(
            title=title,
            body=body,
        ),
    )
    send(message)
