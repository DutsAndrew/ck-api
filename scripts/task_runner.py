import schedule
import time

def task_runner(app):
    schedule.every().day.at("00:00").do(migrate_past_calendar_events_to_archives, app)
    schedule.every().day.at("00:00").do(migrate_past_calendar_notes_to_archives, app)

    while True:
        schedule.run_pending()
        time.sleep(60)


async def migrate_past_calendar_events_to_archives(app):
    pass


async def migrate_past_calendar_notes_to_archives(app):
    pass