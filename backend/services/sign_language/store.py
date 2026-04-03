from datetime import date
from db import get_connection


def _next_id(cursor, table_names, column_name):
    """
    Return the next numeric id across a set of tables that should share the same key space.
    This prevents collisions when one table contains a newer id than another.
    """
    # table_names and column_name are hardcoded by caller, never user input, so direct interpolation is OK
    select_parts = [
        f"SELECT NVL(MAX({column_name}), 0) AS max_id FROM {table_name}" for table_name in table_names
    ]
    union_query = " UNION ALL ".join(select_parts)
    cursor.execute(f"SELECT MAX(max_id) + 1 FROM ({union_query})")
    return cursor.fetchone()[0]


def save_recording_transcript(user_id, recording_name, fps, duration, transcript_text):
    """
    saves recording + recording transcript to db, returns recording_id transcript_id
    """
    words = transcript_text.split()
    word_count = len(words)
    today = date.today()

    with get_connection() as conn:
        cur = conn.cursor()

        # Keep ids aligned across the decomposed transcript/recording tables.
        rec_id = _next_id(
            cur,
            [
                "Documented_Saved_Transcript_7",
                "Documented_Saved_Transcript_8",
                "Documented_Saved_Transcript_9",
                "Documented_Saved_Transcript_10",
                "Documented_Saved_Transcript_11",
                "Documented_Saved_Transcript_12",
                "Created_Documented_Recording",
                "Video",
            ],
            "recording_id",
        )
        tr_id = _next_id(
            cur,
            [
                "Documented_Saved_Transcript_1",
                "Documented_Saved_Transcript_2",
                "Documented_Saved_Transcript_3",
                "Documented_Saved_Transcript_4",
                "Documented_Saved_Transcript_5",
                "Documented_Saved_Transcript_6",
                "Created_Documented_Recording",
            ],
            "transcript_id",
        )

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
