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

