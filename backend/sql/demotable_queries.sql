--JOIN QUERY: find translated words in a specific transcript + their confidence scores
SELECT 
    TW1.instance_id,
    TW5.translation,
    TW4.translation_confidence,
    TW1.transcript_id
FROM Translated_Word_1 TW1
JOIN Translated_Word_5 TW5 
    ON TW1.instance_id = TW5.instance_id
JOIN Translated_Word_4 TW4 
    ON TW1.instance_id = TW4.instance_id
WHERE TW1.transcript_id = :transcript_id;

--UPDATE QUERY: changes the name and email of the tuple that has user_id=1 
UPDATE Calibrated_User
SET 
    name = 'Unlucky Bin',
    email = 'unlucky@example.com'
WHERE 
    user_id = 1;

--NESTED AGGREGATION: find transcripts whose word count > the average word count of all transcripts
SELECT transcript_id, word_count
FROM Documented_Saved_Transcript_4
WHERE word_count > (
    SELECT AVG(word_count)
    FROM Documented_Saved_Transcript_4
);

--DELETE QUERY:     delete a predicted gesture handmark using the def_id
DELETE FROM Predicted_Gesture_Handmark2
WHERE def_id = :input_def_id;
COMMIT;

--PROJECTION: allows the user to select any number of attributes from their user profile to view
SELECT &attributes
FROM Calibrated_User
WHERE user_id = :input_user_id;

--HAVING: checks if the selected user has a name documented
SELECT user_id
FROM Calibrated_User
WHERE user_id = :input_user_id
GROUP BY user_id
HAVING COUNT(name) > 0;

--SELECTION QUERY: find all recordings created by a specific user
SELECT recording_id, recording_name, fps, recording_date
FROM Created_Documented_Recording
WHERE user_id = :input_user_id;

--GROUP BY QUERY: count how many transcripts each user has saved
SELECT user_id, COUNT(*) AS transcript_count
FROM Documented_Saved_Transcript_2
GROUP BY user_id;

--INSERT QUERY: add a new calibrated definition for a user
INSERT INTO Calibrated_Definition (def_id, user_id, gesture, def_name, description)
VALUES (
    :input_def_id,
    :input_user_id,
    :input_gesture,
    :input_def_name,
    :input_description
);
COMMIT;

--DIVISION QUERY: find users who have saved transcripts in every language currently stored
SELECT CU.user_id, CU.name
FROM Calibrated_User CU
WHERE NOT EXISTS (
    SELECT DS6.language
    FROM Documented_Saved_Transcript_6 DS6
    WHERE NOT EXISTS (
        SELECT 1
        FROM Documented_Saved_Transcript_2 DS2
        JOIN Documented_Saved_Transcript_6 DS6_USER
            ON DS2.transcript_id = DS6_USER.transcript_id
        WHERE DS2.user_id = CU.user_id
          AND DS6_USER.language = DS6.language
    )
);
