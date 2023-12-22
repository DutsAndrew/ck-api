import schedule
import time

# global variable for task runner thread
task_runner_flag = True


def task_runner(app):
    schedule.every().day.at("00:00").do(migrate_past_calendar_events_to_archives, app)
    schedule.every().day.at("00:00").do(migrate_past_calendar_notes_to_archives, app)

    global task_runner_flag

    while task_runner_flag:
        schedule.run_pending()
        time.sleep(60)



def stop_task_runner():
    global task_runner_flag
    task_runner_flag = False


async def migrate_past_calendar_events_to_archives(app):
    pass


async def migrate_past_calendar_notes_to_archives(app):
    pass