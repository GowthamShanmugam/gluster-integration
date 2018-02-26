import json

from tendrl.commons.utils import event_utils

POST_RECOVERY_TTL = 200
NOTIFICATION_TTL = 86400   # one day


def process_events():
    events = NS.gluster.objects.NativeEvents().load_all()
    if events:
        for event in events:
            try:
                event.tags = json.loads(event.tags)
            except(TypeError, ValueError):
                # tags can be None
                pass
            if event.severity == "recovery" and not event.recovery_processed:
                # this perticular event is recovery event
                # so process this event and delete it
                event_utils.emit_event(
                    event.context.split("|")[0],
                    event.current_value,
                    event.message,
                    event.context,
                    "INFO",
                    tags=event.tags
                )
                processed_event = NS.gluster.objects.NativeEvents(
                    event.context,
                    recovery_processed=True
                )
                processed_event.save(ttl=POST_RECOVERY_TTL)
                continue

            if event.alert_notify and not event.processed:
                event_utils.emit_event(
                    event.context.split("|")[0],
                    event.current_value,
                    event.message,
                    event.context,
                    event.severity.upper(),
                    alert_notify=event.alert_notify,
                    tags=event.tags
                )
                processed_event = NS.gluster.objects.NativeEvents(
                    event.context,
                    processed=True
                )
                processed_event.save(NOTIFICATION_TTL)
                continue

            if event.severity == "warning" and not event.processed:
                event_utils.emit_event(
                    event.context.split("|")[0],
                    event.current_value,
                    event.message,
                    event.context,
                    "WARNING",
                    tags=event.tags
                )
                processed_event = NS.gluster.objects.NativeEvents(
                    event.context,
                    processed=True
                )
                processed_event.save()
                continue
