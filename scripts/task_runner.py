import schedule
import time

# global variable for task runner thread
task_runner_flag = True


def task_runner(app):
    print('Running task_runner')

    schedule.every().day.at("00:00").do(migrate_past_calendar_events_to_archives, app)
    schedule.every().day.at("00:00").do(migrate_past_calendar_notes_to_archives, app)

    global task_runner_flag

    while task_runner_flag is True:
        schedule.run_pending()
        time.sleep(60)


def stop_task_runner():
    global task_runner_flag
    task_runner_flag = False


def migrate_past_calendar_events_to_archives(app):
    return


def migrate_past_calendar_notes_to_archives(app):
    return