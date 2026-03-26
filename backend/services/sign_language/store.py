from datetime import date
from db import get_connection


def save_recording_transcript(user_id, recording_name, fps, duration, transcript_text):
    """
    saves recording + recording transcript to db, returns recording_id transcript_id
    """
    words = transcript_text.split()
    word_count = len(words)
    today = date.today()

    return {"recording_id": 0, "transcript_id": 0}


def delete_recording(recording_id):
    """
    deletes recording by id
    """