from django.test import TestCase

# Create your tests here.

# Asynchronous Task Example
from celery import shared_task

@shared_task
def send_event_update_email(event_id):
    event = Event.objects.get(pk=event_id)
    rsvps = RSVP.objects.filter(event=event)
    for rsvp in rsvps:
        send_mail(
            subject=f"Update on Event: {event.title}",
            message=f"Dear {rsvp.user.full_name},\n\nThe event '{event.title}' has been updated.\n\nRegards,\nEvent Management Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[rsvp.user.email],
        )
