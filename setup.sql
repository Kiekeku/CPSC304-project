/* CPSC 304 Group 107 - ASL Translator
- Run this file to fully reset and repopulate the database.*/

/* drop tables */

DROP TABLE Translated_Word_9 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_8 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_6 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_5 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_4 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_3 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_2 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_1 CASCADE CONSTRAINTS;
DROP TABLE Translated_Word_7 CASCADE CONSTRAINTS;

DROP TABLE Predicted_Gesture_Handmark1 CASCADE CONSTRAINTS;
DROP TABLE Predicted_Gesture_Handmark2 CASCADE CONSTRAINTS;

DROP TABLE Trained_Machine_Learning_Model CASCADE CONSTRAINTS;

DROP TABLE Contained_Analyzed_Frame1 CASCADE CONSTRAINTS;
DROP TABLE Contained_Analyzed_Frame2 CASCADE CONSTRAINTS;

DROP TABLE Live CASCADE CONSTRAINTS;
DROP TABLE Video CASCADE CONSTRAINTS;

DROP TABLE Documented_Saved_Transcript_14 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_13 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_12 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_11 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_10 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_9  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_8  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_6  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_5  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_4  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_3  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_2  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_7  CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_1  CASCADE CONSTRAINTS;

DROP TABLE Created_Documented_Recording CASCADE CONSTRAINTS;

DROP TABLE Calibrated_Definition CASCADE CONSTRAINTS;
DROP TABLE Calibrated_User CASCADE CONSTRAINTS;

/* create tables */
CREATE TABLE Contained_Analyzed_Frame2( 
    data VARCHAR[255] PRIMARY KEY, 
    resolution VARCHAR[255] NOT NULL
) ;

CREATE TABLE Translated_Word_7 ( 
    Translation VARCHAR[255] PRIMARY KEY, 
    character_length INT);

     
CREATE TABLE Predicted_Gesture_Handmark2( 
    def_id INT PRIMARY KEY, 
    number_of_frames INT NOT NULL, 
    x_position VARCHAR[255] NOT NULL, 
    y_position VARCHAR[255] NOT NULL, 
    UNIQUE(x_position, y_position));

    
CREATE TABLE Trained_Machine_Learning_Model( 
    model_id INT PRIMARY KEY, 
    handmark_id INT, 
    accuracy INT, 
    hyperparameter INT NOT NULL, 
    model_type VARCHAR[255]);

CREATE TABLE Predicted_Gesture_Handmark1( 
    handmark_id INT PRIMARY KEY, 
    def_id INT, 
    model_id INT, 
    FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) 
    ON DELETE CASCADE, 
    FOREIGN KEY (def_id) REFERENCES Predicted_Gesture_Handmark2(def_id) 
    ON DELETE CASCADE);

ALTER TABLE Trained_Machine_Learning_Model
    ADD CONSTRAINT fk_mlmodel_handmark
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1 (handmark_id);

CREATE TABLE Calibrated_User( 
    user_id INT PRIMARY KEY, 
    def_id INT, 
    date_of_creation DATE NOT NULL, 
    email VARCHAR[50] NOT NULL, 
    name VARCHAR[50], 
    UNIQUE(email), 
    FOREIGN KEY(def_id) REFERENCES Calibrated_Definition(def_id)
    ); 
 
CREATE TABLE Calibrated_Definition( 
    def_id INT PRIMARY KEY,  
    user_id INT, 
    gesture VARCHAR[255] NOT NULL,  
    def_name VARCHAR[50] NOT NULL,  
    description VARCHAR[255] 
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 	 
    ON DELETE CASCADE
); 

ALTER TABLE Calibrated_User
    ADD CONSTRAINT fk_user_def
    FOREIGN KEY (def_id) REFERENCES Calibrated_Definition (def_id);

CREATE TABLE Documented_Saved_Transcript_7 ( 
    recording_id INT PRIMARY KEY, 
    transcript_id INT, 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) 
    ON DELETE CASCADE);

CREATE TABLE Documented_Saved_Transcript_1 (
    transcript_id INT PRIMARY KEY, 
    recording_id INT, 
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 
    ON DELETE CASCADE
);

ALTER TABLE Documented_Saved_Transcript_7
    ADD CONSTRAINT fk_t7_transcript
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id)
        ON DELETE CASCADE;

CREATE TABLE Documented_Saved_Transcript_2 ( 
    transcript_id INT PRIMARY KEY, 
    user_id INT, 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1(transcript_id) 
    ON DELETE CASCADE, 
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 
    ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_3 ( 
    transcript_id INT PRIMARY KEY, 
    transcript_data VARCHAR[255], 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1(transcript_id) 
    ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_4 ( 
    transcript_id INT PRIMARY KEY, 
    word_count INT 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) 
    ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_5 ( 
    transcript_id INT PRIMARY KEY, 
    transcription_date date, 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) 
    ON DELETE CASCADE);


CREATE TABLE Documented_Saved_Transcript_6 ( 
    transcript_id INT PRIMARY KEY, 
    language VARCHAR[50], 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) 
    ON DELETE CASCADE);


CREATE TABLE Documented_Saved_Transcript_8 ( 
    recording_id INT PRIMARY KEY, 
    user_id INT, 
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 
    ON DELETE CASCADE, 
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 
    ON DELETE CASCADE);

CREATE TABLE Documented_Saved_Transcript_9 ( 
    recording_id INT PRIMARY KEY, 
    transcript_data VARCHAR[255], 
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 
    ON DELETE CASCADE);

CREATE TABLE Documented_Saved_Transcript_10 ( 
    recording_id INT PRIMARY KEY, 
    word_count INT, 
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 
    ON DELETE CASCADE);

CREATE TABLE Documented_Saved_Transcript_11 ( 
    recording_id INT PRIMARY KEY, 
    transcription_date date, 
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 
    ON DELETE CASCADE);

CREATE TABLE Documented_Saved_Transcript_12 ( 
    recording_id INT PRIMARY KEY, 
    language VARCHAR[50], 
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 
    ON DELETE CASCADE);

CREATE TABLE Documented_Saved_Transcript_13 ( 
    transcript_data VARCHAR[255] PRIMARY KEY, 
    word_count INT, 
    FOREIGN KEY (transcript_data) REFERENCES Documented_Saved_Transcript_10 (transcript_data) 
    ON DELETE CASCADE);
    
CREATE TABLE Documented_Saved_Transcript_14 ( 
    transcript_data VARCHAR[255] PRIMARY KEY, 
    language VARCHAR[50], 
    FOREIGN KEY (transcript_data) REFERENCES Documented_Saved_Transcript1 (transcript_id) 
    ON DELETE CASCADE);

CREATE TABLE Created_Documented_Recording( 
    recording_id INT PRIMARY KEY, 
    transcript_id INT, 
    user_id INT,  
    fps INT NOT NULL, 
    recording_date DATE NOT NULL,  
    recording_name VARCHAR[50] NOT NULL, 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1(transcript_id), 
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 
    ON DELETE CASCADE, 
    UNIQUE(recording_name)
); 

CREATE TABLE Live( 
    recording_id INT PRIMARY KEY, 
    livestream_source VARCHAR[255] NOT NULL, 
    FOREIGN KEY (recording_id) REFERENCES Created_Documented_Recording(recording_id) 
    ON DELETE CASCADE
);

CREATE TABLE Video( 
    recording_id INT PRIMARY KEY, 
    duration INT NOT NULL, 
    FOREIGN KEY (recording_id) REFERENCES Created_Documented_Recording (recording_id) 
    ON DELETE CASCADE
);

CREATE TABLE Contained_Analyzed_Frame1( 
    data VARCHAR[255] NOT NULL, 
    recording_id INT, 
    frame_id INT, 
    timestamp TIMESTAMP NOT NULL, 
    PRIMARY KEY(recording_id, frame_id), 
    FOREIGN KEY(recording_id) REFERENCES  
    Created_Documented_Recording(recording_id) 
    ON DELETE CASCADE, 
    FOREIGN KEY(data) REFERENCES Contained_Analyzed_Frame2(data) 
    ON DELETE CASCADE
);

CREATE TABLE Translated_Word_1 ( 
    instance_id INT PRIMARY KEY,  
    transcript_id INT, 
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id)  
    ON DELETE CASCADE);

CREATE TABLE Translated_Word_2 ( 
    instance_id INT PRIMARY KEY,  
    handmark_id INT, 
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1(handmark_id)  
    ON DELETE CASCADE, 
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 
    ON DELETE CASCADE);

CREATE TABLE Translated_Word_3 ( 
    instance_id INT PRIMARY KEY,  
    character_length INT, 
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 
    ON DELETE CASCADE);

CREATE TABLE Translated_Word_4 ( 
    instance_id INT PRIMARY KEY,  
    translation_confidence INT, 
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 
    ON DELETE CASCADE);

CREATE TABLE Translated_Word_5 ( 
    instance_id INT PRIMARY KEY,  
    translation VARCHAR[255] NOT NULL, 
    FOREIGN KEY (translation) REFERENCES Translated_Word_7 (translation)  
    ON DELETE CASCADE, 
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 
    ON DELETE CASCADE, 
    UNIQUE (translation));
    
CREATE TABLE Translated_Word_6 ( 
    instance_id INT PRIMARY KEY,  
    model_id INT,
    FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) 
    ON DELETE CASCADE, 
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 
    ON DELETE CASCADE);

CREATE TABLE Translated_Word_8 ( 
    model_id INT, 
    handmark_id INT, 
    translation VARCHAR[255], 
    translation_confidence INT NOT NULL, 
    PRIMARY KEY (model_id, handmark_id, translation), 
    FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) 
    ON DELETE CASCADE, 
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1(handmark_id) 
    ON DELETE CASCADE, 
    FOREIGN KEY (translation) REFERENCES Translated_Word_7(translation) 
    ON DELETE CASCADE);

CREATE TABLE Translated_Word_9 ( 
    handmark_id INT PRIMARY KEY, 
    word_timestamp TIMESTAMP NOT NULL, 
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1(handmark_id) 
    ON DELETE CASCADE);

/* insert tables */

INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_open_palm',    '1920x1080');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_closed_fist',  '1920x1080');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_index_point',  '1280x720');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_thumb_up',     '1280x720');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_victory_sign', '1920x1080');

-- English word lookup (referenced by Translated_Word_5 and Translated_Word_8)
INSERT INTO Translated_Word_7 VALUES ('HELLO',  5);
INSERT INTO Translated_Word_7 VALUES ('THANK',  5);
INSERT INTO Translated_Word_7 VALUES ('HELP',   4);
INSERT INTO Translated_Word_7 VALUES ('YES',    3);
INSERT INTO Translated_Word_7 VALUES ('NO',     2);
INSERT INTO Translated_Word_7 VALUES ('PLEASE', 6);
INSERT INTO Translated_Word_7 VALUES ('SORRY',  5);
INSERT INTO Translated_Word_7 VALUES ('GOOD',   4);

-- Hand position patterns (referenced by Predicted_Gesture_Handmark1)
INSERT INTO Predicted_Gesture_Handmark2 VALUES (1, 12, '0.45,0.50,0.50', '0.30,0.35,0.40');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (2,  8, '0.20,0.25,0.30', '0.60,0.65,0.70');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (3, 15, '0.70,0.75,0.80', '0.20,0.25,0.30');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (4, 10, '0.35,0.40,0.45', '0.50,0.55,0.60');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (5,  9, '0.55,0.60,0.65', '0.10,0.15,0.20');

-- ML models (handmark_id FK added via UPDATE after Handmark1 rows exist)
INSERT INTO Trained_Machine_Learning_Model (model_id, accuracy, hyperparameter, model_type)
    VALUES (1, 92, 100, 'RandomForest');
INSERT INTO Trained_Machine_Learning_Model (model_id, accuracy, hyperparameter, model_type)
    VALUES (2, 87,  50, 'RandomForest');
INSERT INTO Trained_Machine_Learning_Model (model_id, accuracy, hyperparameter, model_type)
    VALUES (3, 78, 200, 'MLP');
INSERT INTO Trained_Machine_Learning_Model (model_id, accuracy, hyperparameter, model_type)
    VALUES (4, 95, 150, 'MLP');
INSERT INTO Trained_Machine_Learning_Model (model_id, accuracy, hyperparameter, model_type)
    VALUES (5, 81,  75, 'RandomForest');

INSERT INTO Predicted_Gesture_Handmark1 VALUES (101, 1, 1);
INSERT INTO Predicted_Gesture_Handmark1 VALUES (102, 2, 1);
INSERT INTO Predicted_Gesture_Handmark1 VALUES (103, 3, 1);
INSERT INTO Predicted_Gesture_Handmark1 VALUES (104, 4, 2);
INSERT INTO Predicted_Gesture_Handmark1 VALUES (105, 5, 2);
INSERT INTO Predicted_Gesture_Handmark1 VALUES (106, 1, 3);
INSERT INTO Predicted_Gesture_Handmark1 VALUES (107, 2, 3);
INSERT INTO Predicted_Gesture_Handmark1 VALUES (108, 3, 4);

UPDATE Trained_Machine_Learning_Model SET handmark_id = 101 WHERE model_id = 1;
UPDATE Trained_Machine_Learning_Model SET handmark_id = 104 WHERE model_id = 2;
UPDATE Trained_Machine_Learning_Model SET handmark_id = 106 WHERE model_id = 3;
UPDATE Trained_Machine_Learning_Model SET handmark_id = 108 WHERE model_id = 4;
UPDATE Trained_Machine_Learning_Model SET handmark_id = 102 WHERE model_id = 5;

INSERT INTO Translated_Word_9 VALUES (101, TIMESTAMP '2025-11-01 10:00:00.100');
INSERT INTO Translated_Word_9 VALUES (102, TIMESTAMP '2025-11-01 10:00:00.233');
INSERT INTO Translated_Word_9 VALUES (103, TIMESTAMP '2025-12-01 09:00:00.150');
INSERT INTO Translated_Word_9 VALUES (104, TIMESTAMP '2025-12-10 11:00:00.200');
INSERT INTO Translated_Word_9 VALUES (105, TIMESTAMP '2025-12-15 13:00:00.300');
INSERT INTO Translated_Word_9 VALUES (106, TIMESTAMP '2025-11-15 14:00:00.100');
INSERT INTO Translated_Word_9 VALUES (107, TIMESTAMP '2026-01-05 15:00:00.050');
INSERT INTO Translated_Word_9 VALUES (108, TIMESTAMP '2026-01-20 09:30:00.200');

INSERT INTO Translated_Word_8 VALUES (1, 101, 'HELLO', 94);
INSERT INTO Translated_Word_8 VALUES (1, 102, 'THANK', 91);
INSERT INTO Translated_Word_8 VALUES (1, 103, 'HELP', 88);
INSERT INTO Translated_Word_8 VALUES (1, 104, 'YES', 96);
INSERT INTO Translated_Word_8 VALUES (1, 105, 'NO', 83);
INSERT INTO Translated_Word_8 VALUES (2, 101, 'HELLO', 87);
INSERT INTO Translated_Word_8 VALUES (2, 102, 'SORRY', 85);
INSERT INTO Translated_Word_8 VALUES (2, 103, 'HELP', 79);
INSERT INTO Translated_Word_8 VALUES (3, 104, 'GOOD', 91);
INSERT INTO Translated_Word_8 VALUES (3, 101, 'HELLO', 86); 

INSERT INTO Calibrated_User (user_id, date_of_creation, email, name)
    VALUES (1, DATE '2025-09-01', 'jett@example.com', 'Jett Chen');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name)
    VALUES (2, DATE '2025-09-15', 'bob@example.com', 'Bob Bill');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name)
    VALUES (3, DATE '2025-10-01', 'angel@example.com', 'Angel Super');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name)
    VALUES (4, DATE '2025-10-20', 'justin@example.com', 'Justin Awesome');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name)
    VALUES (5, DATE '2025-11-05', 'hao@example.com', 'Hao Cool');

INSERT INTO Calibrated_Definition VALUES (1, 1, 'open_palm', 'HELLO Gesture', 'Flat open hand, fingers together, palm facing out');
INSERT INTO Calibrated_Definition VALUES (2, 1, 'closed_fist', 'THANK Gesture', 'Closed fist moving forward from chin');
INSERT INTO Calibrated_Definition VALUES (3, 2, 'index_point', 'HELP Gesture', 'Thumb up resting on open palm, both hands rise');
INSERT INTO Calibrated_Definition VALUES (4, 3, 'thumb_up', 'YES Gesture', 'Closed fist bobbing at wrist');
INSERT INTO Calibrated_Definition VALUES (5, 4, 'victory_sign', 'NO Gesture', 'Index and middle finger, wave side to side');

UPDATE Calibrated_User SET def_id = 1 WHERE user_id = 1;
UPDATE Calibrated_User SET def_id = 3 WHERE user_id = 2;
UPDATE Calibrated_User SET def_id = 4 WHERE user_id = 3;
UPDATE Calibrated_User SET def_id = 5 WHERE user_id = 4;
UPDATE Calibrated_User SET def_id = 2 WHERE user_id = 5;

INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (1);
INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (2);

INSERT INTO Documented_Saved_Transcript_1 VALUES (201, 1);
INSERT INTO Documented_Saved_Transcript_1 VALUES (202, 2);

UPDATE Documented_Saved_Transcript_7 SET transcript_id = 201 WHERE recording_id = 1;
UPDATE Documented_Saved_Transcript_7 SET transcript_id = 202 WHERE recording_id = 2;

INSERT INTO Documented_Saved_Transcript_2 VALUES (201, 1);
INSERT INTO Documented_Saved_Transcript_2 VALUES (202, 1);

INSERT INTO Documented_Saved_Transcript_3 VALUES (201, 'HELLO THANK HELP YES NO PLEASE');
INSERT INTO Documented_Saved_Transcript_3 VALUES (202, 'YES NO SORRY GOOD HELLO');

INSERT INTO Documented_Saved_Transcript_4 VALUES (201, 6);
INSERT INTO Documented_Saved_Transcript_4 VALUES (202, 5);

INSERT INTO Documented_Saved_Transcript_5 VALUES (201, DATE '2025-11-01');
INSERT INTO Documented_Saved_Transcript_5 VALUES (202, DATE '2025-11-15');

INSERT INTO Documented_Saved_Transcript_6 VALUES (201, 'English');
INSERT INTO Documented_Saved_Transcript_6 VALUES (202, 'English');

INSERT INTO Documented_Saved_Transcript_8 VALUES (1, 1);
INSERT INTO Documented_Saved_Transcript_8 VALUES (2, 1);

INSERT INTO Documented_Saved_Transcript_9 VALUES (1, 'HELLO THANK HELP YES NO PLEASE');
INSERT INTO Documented_Saved_Transcript_9 VALUES (2, 'YES NO SORRY GOOD HELLO');

INSERT INTO Documented_Saved_Transcript_10 VALUES (1, 6);
INSERT INTO Documented_Saved_Transcript_10 VALUES (2, 5);

INSERT INTO Documented_Saved_Transcript_11 VALUES (1, DATE '2025-11-01');
INSERT INTO Documented_Saved_Transcript_11 VALUES (2, DATE '2025-11-15');

INSERT INTO Documented_Saved_Transcript_12 VALUES (1, 'English');
INSERT INTO Documented_Saved_Transcript_12 VALUES (2, 'English');

INSERT INTO Created_Documented_Recording VALUES (1, 201, 1, 30, DATE '2025-11-01', 'jett_session_1');
INSERT INTO Created_Documented_Recording VALUES (2, 202, 1, 30, DATE '2025-11-15', 'jett_session_2');

INSERT INTO Live  VALUES (1, 'webcam://device_0');
INSERT INTO Video VALUES (2, 120);

INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_open_palm',   1, 1, TIMESTAMP '2025-11-01 10:00:00.000');
INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_closed_fist', 1, 2, TIMESTAMP '2025-11-01 10:00:00.033');
INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_index_point', 2, 1, TIMESTAMP '2025-11-15 14:00:00.000');

INSERT INTO Translated_Word_1 VALUES (1,  201);
INSERT INTO Translated_Word_1 VALUES (2,  201);
INSERT INTO Translated_Word_1 VALUES (3,  201);
INSERT INTO Translated_Word_1 VALUES (4,  201);
INSERT INTO Translated_Word_1 VALUES (5,  201);
INSERT INTO Translated_Word_1 VALUES (6,  201);
INSERT INTO Translated_Word_1 VALUES (7,  202);
INSERT INTO Translated_Word_1 VALUES (8,  202);
INSERT INTO Translated_Word_1 VALUES (9,  202);
INSERT INTO Translated_Word_1 VALUES (10, 202);
INSERT INTO Translated_Word_1 VALUES (11, 202);

INSERT INTO Translated_Word_2 VALUES (1,  101); -- def 1 open_palm = HELLO
INSERT INTO Translated_Word_2 VALUES (2,  102); -- def 2 closed_fist = THANK
INSERT INTO Translated_Word_2 VALUES (3,  103); -- def 3 index_point = HELP
INSERT INTO Translated_Word_2 VALUES (4,  104); -- def 4 thumb_up = YES
INSERT INTO Translated_Word_2 VALUES (5,  105); -- def 5 victory = NO
INSERT INTO Translated_Word_2 VALUES (6,  101); -- def 1 again = PLEASE
INSERT INTO Translated_Word_2 VALUES (7,  104); -- def 4 = YES
INSERT INTO Translated_Word_2 VALUES (8,  105); -- def 5 = NO
INSERT INTO Translated_Word_2 VALUES (9,  102); -- def 2 = SORRY
INSERT INTO Translated_Word_2 VALUES (10, 101); -- def 1 = GOOD
INSERT INTO Translated_Word_2 VALUES (11, 101); -- def 1 = HELLO

INSERT INTO Translated_Word_3 VALUES (1,  5);
INSERT INTO Translated_Word_3 VALUES (2,  5);
INSERT INTO Translated_Word_3 VALUES (3,  4);
INSERT INTO Translated_Word_3 VALUES (4,  3);
INSERT INTO Translated_Word_3 VALUES (5,  2);
INSERT INTO Translated_Word_3 VALUES (6,  6);
INSERT INTO Translated_Word_3 VALUES (7,  3);
INSERT INTO Translated_Word_3 VALUES (8,  2);
INSERT INTO Translated_Word_3 VALUES (9,  5);
INSERT INTO Translated_Word_3 VALUES (10, 4);
INSERT INTO Translated_Word_3 VALUES (11, 5);

INSERT INTO Translated_Word_4 VALUES (1,  94);
INSERT INTO Translated_Word_4 VALUES (2,  91);
INSERT INTO Translated_Word_4 VALUES (3,  88);
INSERT INTO Translated_Word_4 VALUES (4,  96);
INSERT INTO Translated_Word_4 VALUES (5,  83);
INSERT INTO Translated_Word_4 VALUES (6,  92);
INSERT INTO Translated_Word_4 VALUES (7,  90);
INSERT INTO Translated_Word_4 VALUES (8,  85);
INSERT INTO Translated_Word_4 VALUES (9,  93);
INSERT INTO Translated_Word_4 VALUES (10, 87);
INSERT INTO Translated_Word_4 VALUES (11, 95);

INSERT INTO Translated_Word_5 VALUES (1, 'HELLO');
INSERT INTO Translated_Word_5 VALUES (2, 'THANK');
INSERT INTO Translated_Word_5 VALUES (3, 'HELP');
INSERT INTO Translated_Word_5 VALUES (4, 'YES');
INSERT INTO Translated_Word_5 VALUES (5, 'NO');
INSERT INTO Translated_Word_5 VALUES (6, 'PLEASE');
INSERT INTO Translated_Word_5 VALUES (7, 'YES');
INSERT INTO Translated_Word_5 VALUES (8, 'NO');
INSERT INTO Translated_Word_5 VALUES (9, 'SORRY');
INSERT INTO Translated_Word_5 VALUES (10, 'GOOD');
INSERT INTO Translated_Word_5 VALUES (11, 'HELLO');

INSERT INTO Translated_Word_6 VALUES (1, 1);
INSERT INTO Translated_Word_6 VALUES (2, 1);
INSERT INTO Translated_Word_6 VALUES (3, 1);
INSERT INTO Translated_Word_6 VALUES (4, 1);
INSERT INTO Translated_Word_6 VALUES (5, 1);
INSERT INTO Translated_Word_6 VALUES (6, 1);
INSERT INTO Translated_Word_6 VALUES (7, 1);
INSERT INTO Translated_Word_6 VALUES (8, 1);
INSERT INTO Translated_Word_6 VALUES (9, 2);
INSERT INTO Translated_Word_6 VALUES (10, 2);
INSERT INTO Translated_Word_6 VALUES (11, 2);

