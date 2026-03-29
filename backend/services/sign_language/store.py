from datetime import date
from db import get_connection


def save_recording_transcript(user_id, recording_name, fps, duration, transcript_text):
    """
    saves recording + recording transcript to db, returns recording_id transcript_id
    """
    words = transcript_text.split()
    word_count = len(words)
    today = date.today()

    with get_connection() as conn:
        cur = conn.cursor()

        # get new ids
        cur.execute("SELECT NVL(MAX(recording_id), 0) + 1 FROM Created_Documented_Recording")
        rec_id = cur.fetchone()[0]
        cur.execute("SELECT NVL(MAX(transcript_id), 0) + 1 FROM Documented_Saved_Transcript_1")
        tr_id = cur.fetchone()[0]

        language = "English"

        # The transcript schema is stored twice:
        # - transcript-centric tables keyed by transcript_id (1-6)
        # - recording-centric tables keyed by recording_id (7-12)
        # Seed data creates the 7 <-> 1 link in two steps because of the circular FK.
        cur.execute("INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (:1)", [rec_id])
        cur.execute("INSERT INTO Documented_Saved_Transcript_1 VALUES (:1, :2)", [tr_id, rec_id])
        cur.execute(
            "UPDATE Documented_Saved_Transcript_7 SET transcript_id = :1 WHERE recording_id = :2",
            [tr_id, rec_id],
        )

        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_2 VALUES (:1, :2)",
            [tr_id, user_id],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_3 VALUES (:1, :2)",
            [tr_id, transcript_text],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_4 VALUES (:1, :2)",
            [tr_id, word_count],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_5 VALUES (:1, :2)",
            [tr_id, today],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_6 VALUES (:1, :2)",
            [tr_id, language],
        )

        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_8 VALUES (:1, :2)",
            [rec_id, user_id],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_9 VALUES (:1, :2)",
            [rec_id, transcript_text],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_10 VALUES (:1, :2)",
            [rec_id, word_count],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_11 VALUES (:1, :2)",
            [rec_id, today],
        )
        cur.execute(
            "INSERT INTO Documented_Saved_Transcript_12 VALUES (:1, :2)",
            [rec_id, language],
        )

        # 13 and 14 behave like transcript-content lookup tables keyed by transcript text.
        # Use MERGE so repeated transcript text does not raise duplicate key errors.
        cur.execute(
            """
            MERGE INTO Documented_Saved_Transcript_13 dst
            USING (SELECT :1 AS transcript_data, :2 AS word_count FROM dual) src
            ON (dst.transcript_data = src.transcript_data)
            WHEN NOT MATCHED THEN
                INSERT (transcript_data, word_count)
                VALUES (src.transcript_data, src.word_count)
            """,
            [transcript_text, word_count],
        )
        cur.execute(
            """
            MERGE INTO Documented_Saved_Transcript_14 dst
            USING (SELECT :1 AS transcript_data, :2 AS language FROM dual) src
            ON (dst.transcript_data = src.transcript_data)
            WHEN NOT MATCHED THEN
                INSERT (transcript_data, language)
                VALUES (src.transcript_data, src.language)
            """,
            [transcript_text, language],
        )

        cur.execute(
            "INSERT INTO Created_Documented_Recording VALUES (:1, :2, :3, :4, :5, :6)",
            [rec_id, tr_id, user_id, fps, today, recording_name],
        )
        cur.execute("INSERT INTO Video VALUES (:1, :2)", [rec_id, duration])

        conn.commit()
    return {"recording_id": rec_id, "transcript_id": tr_id}

def delete_recording(recording_id):
    """
    deletes recording by id
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Created_Documented_Recording WHERE recording_id = :1", [recording_id])
        conn.commit()
