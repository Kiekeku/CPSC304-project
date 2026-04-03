BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE DEMOTABLE';
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE != -942 THEN
            RAISE;
        END IF;
END;
/

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
DROP TABLE Documented_Saved_Transcript_9 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_8 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_6 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_5 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_4 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_3 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_2 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_7 CASCADE CONSTRAINTS;
DROP TABLE Documented_Saved_Transcript_1 CASCADE CONSTRAINTS;

DROP TABLE Created_Documented_Recording CASCADE CONSTRAINTS;

DROP TABLE Calibrated_Definition CASCADE CONSTRAINTS;
DROP TABLE Calibrated_User CASCADE CONSTRAINTS;

CREATE TABLE Contained_Analyzed_Frame2 (
    data VARCHAR2(255) PRIMARY KEY,
    resolution VARCHAR2(255) NOT NULL
);

CREATE TABLE Translated_Word_7 (
    translation VARCHAR2(255) PRIMARY KEY,
    character_length NUMBER
);

CREATE TABLE Predicted_Gesture_Handmark2 (
    def_id NUMBER PRIMARY KEY,
    number_of_frames NUMBER NOT NULL,
    x_position VARCHAR2(255) NOT NULL,
    y_position VARCHAR2(255) NOT NULL,
    UNIQUE (x_position, y_position)
);

CREATE TABLE Trained_Machine_Learning_Model (
    model_id NUMBER PRIMARY KEY,
    handmark_id NUMBER,
    accuracy NUMBER,
    hyperparameter NUMBER NOT NULL,
    model_type VARCHAR2(255)
);

CREATE TABLE Predicted_Gesture_Handmark1 (
    handmark_id NUMBER PRIMARY KEY,
    def_id NUMBER,
    model_id NUMBER,
    FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) ON DELETE CASCADE,
    FOREIGN KEY (def_id) REFERENCES Predicted_Gesture_Handmark2 (def_id) ON DELETE CASCADE
);

ALTER TABLE Trained_Machine_Learning_Model
    ADD CONSTRAINT fk_mlmodel_handmark
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1 (handmark_id);

CREATE TABLE Calibrated_User (
    user_id NUMBER PRIMARY KEY,
    def_id NUMBER,
    date_of_creation DATE NOT NULL,
    email VARCHAR2(50) NOT NULL,
    name VARCHAR2(50),
    password_hash VARCHAR2(255),
    UNIQUE (email)
);

CREATE TABLE Calibrated_Definition (
    def_id NUMBER PRIMARY KEY,
    user_id NUMBER,
    gesture VARCHAR2(255) NOT NULL,
    def_name VARCHAR2(50) NOT NULL,
    description VARCHAR2(255),
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) ON DELETE CASCADE
);

ALTER TABLE Calibrated_User
    ADD CONSTRAINT fk_user_def
    FOREIGN KEY (def_id) REFERENCES Calibrated_Definition (def_id);

CREATE TABLE Documented_Saved_Transcript_1 (
    transcript_id NUMBER PRIMARY KEY,
    recording_id NUMBER
);

CREATE TABLE Documented_Saved_Transcript_7 (
    recording_id NUMBER PRIMARY KEY,
    transcript_id NUMBER,
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) ON DELETE CASCADE
);

ALTER TABLE Documented_Saved_Transcript_1
    ADD CONSTRAINT fk_t1_recording
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id);

CREATE TABLE Documented_Saved_Transcript_2 (
    transcript_id NUMBER PRIMARY KEY,
    user_id NUMBER,
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_3 (
    transcript_id NUMBER PRIMARY KEY,
    transcript_data VARCHAR2(1000),
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_4 (
    transcript_id NUMBER PRIMARY KEY,
    word_count NUMBER,
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_5 (
    transcript_id NUMBER PRIMARY KEY,
    transcription_date DATE,
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_6 (
    transcript_id NUMBER PRIMARY KEY,
    language VARCHAR2(50),
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_8 (
    recording_id NUMBER PRIMARY KEY,
    user_id NUMBER,
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_9 (
    recording_id NUMBER PRIMARY KEY,
    transcript_data VARCHAR2(255),
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_10 (
    recording_id NUMBER PRIMARY KEY,
    word_count NUMBER,
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_11 (
    recording_id NUMBER PRIMARY KEY,
    transcription_date DATE,
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_12 (
    recording_id NUMBER PRIMARY KEY,
    language VARCHAR2(50),
    FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) ON DELETE CASCADE
);

CREATE TABLE Documented_Saved_Transcript_13 (
    transcript_data VARCHAR2(255) PRIMARY KEY,
    word_count NUMBER
);

CREATE TABLE Documented_Saved_Transcript_14 (
    transcript_data VARCHAR2(255) PRIMARY KEY,
    language VARCHAR2(50)
);

CREATE TABLE Created_Documented_Recording (
    recording_id NUMBER PRIMARY KEY,
    transcript_id NUMBER,
    user_id NUMBER,
    fps NUMBER NOT NULL,
    recording_date DATE NOT NULL,
    recording_name VARCHAR2(50) NOT NULL,
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id),
    FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) ON DELETE CASCADE,
    UNIQUE (recording_name)
);

CREATE TABLE Live (
    recording_id NUMBER PRIMARY KEY,
    livestream_source VARCHAR2(255) NOT NULL,
    FOREIGN KEY (recording_id) REFERENCES Created_Documented_Recording (recording_id) ON DELETE CASCADE
);

CREATE TABLE Video (
    recording_id NUMBER PRIMARY KEY,
    duration NUMBER NOT NULL,
    FOREIGN KEY (recording_id) REFERENCES Created_Documented_Recording (recording_id) ON DELETE CASCADE
);

CREATE TABLE Contained_Analyzed_Frame1 (
    data VARCHAR2(255) NOT NULL,
    recording_id NUMBER,
    frame_id NUMBER,
    timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (recording_id, frame_id),
    FOREIGN KEY (recording_id) REFERENCES Created_Documented_Recording (recording_id) ON DELETE CASCADE,
    FOREIGN KEY (data) REFERENCES Contained_Analyzed_Frame2 (data) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_1 (
    instance_id NUMBER PRIMARY KEY,
    transcript_id NUMBER,
    FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 (transcript_id) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_2 (
    instance_id NUMBER PRIMARY KEY,
    handmark_id NUMBER,
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1 (handmark_id) ON DELETE CASCADE,
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_3 (
    instance_id NUMBER PRIMARY KEY,
    character_length NUMBER,
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_4 (
    instance_id NUMBER PRIMARY KEY,
    translation_confidence NUMBER,
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_5 (
    instance_id NUMBER PRIMARY KEY,
    translation VARCHAR2(255) NOT NULL,
    FOREIGN KEY (translation) REFERENCES Translated_Word_7 (translation) ON DELETE CASCADE,
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_6 (
    instance_id NUMBER PRIMARY KEY,
    model_id NUMBER,
    FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) ON DELETE CASCADE,
    FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_8 (
    model_id NUMBER,
    handmark_id NUMBER,
    translation VARCHAR2(255),
    translation_confidence NUMBER NOT NULL,
    PRIMARY KEY (model_id, handmark_id, translation),
    FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) ON DELETE CASCADE,
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1 (handmark_id) ON DELETE CASCADE,
    FOREIGN KEY (translation) REFERENCES Translated_Word_7 (translation) ON DELETE CASCADE
);

CREATE TABLE Translated_Word_9 (
    handmark_id NUMBER PRIMARY KEY,
    word_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1 (handmark_id) ON DELETE CASCADE
);


INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_open_palm',    '1920x1080');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_closed_fist',  '1920x1080');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_index_point',  '1280x720');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_thumb_up',     '1280x720');
INSERT INTO Contained_Analyzed_Frame2 VALUES ('frame_data_victory_sign', '1920x1080');

INSERT INTO Translated_Word_7 VALUES ('HELLO',  5);
INSERT INTO Translated_Word_7 VALUES ('THANK',  5);
INSERT INTO Translated_Word_7 VALUES ('HELP',   4);
INSERT INTO Translated_Word_7 VALUES ('YES',    3);
INSERT INTO Translated_Word_7 VALUES ('NO',     2);
INSERT INTO Translated_Word_7 VALUES ('PLEASE', 6);
INSERT INTO Translated_Word_7 VALUES ('SORRY',  5);
INSERT INTO Translated_Word_7 VALUES ('GOOD',   4);

INSERT INTO Predicted_Gesture_Handmark2 VALUES (1, 12, '0.45,0.50,0.50', '0.30,0.35,0.40');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (2,  8, '0.20,0.25,0.30', '0.60,0.65,0.70');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (3, 15, '0.70,0.75,0.80', '0.20,0.25,0.30');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (4, 10, '0.35,0.40,0.45', '0.50,0.55,0.60');
INSERT INTO Predicted_Gesture_Handmark2 VALUES (5,  9, '0.55,0.60,0.65', '0.10,0.15,0.20');

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

INSERT INTO Calibrated_User (user_id, date_of_creation, email, name, password_hash)
    VALUES (1, DATE '2025-09-01', 'jett@example.com', 'Jett Chen', '$2b$12$/f6u0hDYReDS4nAeNsNJpO4gmcJ2sfu2CPKyiRwUg3r6gmSV0DKeO');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name, password_hash)
    VALUES (2, DATE '2025-09-15', 'bob@example.com', 'Bob Bill', '$2b$12$9lne9zuLJZ0CegHUfOXM1OlffIFUVslVyk8MlPhoyoRdNMr.Um9Si');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name, password_hash)
    VALUES (3, DATE '2025-10-01', 'angel@example.com', 'Angel Super', '$2b$12$bD1WLOU8iq0cQKsLUSnVUey0IdOwJ04gy2Was.wcA9/o6whUksRfO');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name, password_hash)
    VALUES (4, DATE '2025-10-20', 'justin@example.com', 'Justin Awesome', '$2b$12$q5rjZQghy6O/d.XyyIuxte/Zbz41te6g9mofIkgMPhst3BkiXxmiO');
INSERT INTO Calibrated_User (user_id, date_of_creation, email, name, password_hash)
    VALUES (5, DATE '2025-11-05', 'hao@example.com', 'Hao Cool', '$2b$12$pvYrN14gEKNvgwri46KxzeiqY3/5kgCULmkfgAQCjWvTLLnGontpq');

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


INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (3);
INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (8);

INSERT INTO Documented_Saved_Transcript_1 VALUES (203, 3);
INSERT INTO Documented_Saved_Transcript_1 VALUES (208, 8);

UPDATE Documented_Saved_Transcript_7 SET transcript_id = 203 WHERE recording_id = 3;
UPDATE Documented_Saved_Transcript_7 SET transcript_id = 208 WHERE recording_id = 8;

INSERT INTO Documented_Saved_Transcript_2 VALUES (203, 2);
INSERT INTO Documented_Saved_Transcript_2 VALUES (208, 2);

INSERT INTO Documented_Saved_Transcript_3 VALUES (203, 'HELP PLEASE SORRY');
INSERT INTO Documented_Saved_Transcript_3 VALUES (208, 'HELLO HELP PLEASE');

INSERT INTO Documented_Saved_Transcript_4 VALUES (203, 3);
INSERT INTO Documented_Saved_Transcript_4 VALUES (208, 3);

INSERT INTO Documented_Saved_Transcript_5 VALUES (203, DATE '2025-12-01');
INSERT INTO Documented_Saved_Transcript_5 VALUES (208, DATE '2026-01-10');

INSERT INTO Documented_Saved_Transcript_6 VALUES (203, 'English');
INSERT INTO Documented_Saved_Transcript_6 VALUES (208, 'English');

INSERT INTO Documented_Saved_Transcript_8 VALUES (3, 2);
INSERT INTO Documented_Saved_Transcript_8 VALUES (8, 2);

INSERT INTO Documented_Saved_Transcript_9 VALUES (3, 'HELP PLEASE SORRY');
INSERT INTO Documented_Saved_Transcript_9 VALUES (8, 'HELLO HELP PLEASE');

INSERT INTO Documented_Saved_Transcript_10 VALUES (3, 3);
INSERT INTO Documented_Saved_Transcript_10 VALUES (8, 3);

INSERT INTO Documented_Saved_Transcript_11 VALUES (3, DATE '2025-12-01');
INSERT INTO Documented_Saved_Transcript_11 VALUES (8, DATE '2026-01-10');

INSERT INTO Documented_Saved_Transcript_12 VALUES (3, 'English');
INSERT INTO Documented_Saved_Transcript_12 VALUES (8, 'English');

INSERT INTO Created_Documented_Recording VALUES (3, 203, 2, 24, DATE '2025-12-01', 'bob_session_1');
INSERT INTO Created_Documented_Recording VALUES (8, 208, 2, 60, DATE '2026-01-10', 'bob_session_2');

INSERT INTO Live  VALUES (3, 'webcam://device_0');
INSERT INTO Video VALUES (8, 90);

INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_index_point', 3, 1, TIMESTAMP '2025-12-01 09:00:00.000');
INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_open_palm',   8, 1, TIMESTAMP '2026-01-10 10:00:00.000');

INSERT INTO Translated_Word_1 VALUES (12, 203);
INSERT INTO Translated_Word_1 VALUES (13, 203);
INSERT INTO Translated_Word_1 VALUES (14, 203);
INSERT INTO Translated_Word_1 VALUES (15, 208);
INSERT INTO Translated_Word_1 VALUES (16, 208);
INSERT INTO Translated_Word_1 VALUES (17, 208);

INSERT INTO Translated_Word_2 VALUES (12, 103); -- def 3
INSERT INTO Translated_Word_2 VALUES (13, 101); -- def 1
INSERT INTO Translated_Word_2 VALUES (14, 102); -- def 2
INSERT INTO Translated_Word_2 VALUES (15, 101); -- def 1
INSERT INTO Translated_Word_2 VALUES (16, 103); -- def 3
INSERT INTO Translated_Word_2 VALUES (17, 101); -- def 1

INSERT INTO Translated_Word_3 VALUES (12, 4);
INSERT INTO Translated_Word_3 VALUES (13, 6);
INSERT INTO Translated_Word_3 VALUES (14, 5);
INSERT INTO Translated_Word_3 VALUES (15, 5);
INSERT INTO Translated_Word_3 VALUES (16, 4);
INSERT INTO Translated_Word_3 VALUES (17, 6);

INSERT INTO Translated_Word_4 VALUES (12, 79);
INSERT INTO Translated_Word_4 VALUES (13, 82);
INSERT INTO Translated_Word_4 VALUES (14, 88);
INSERT INTO Translated_Word_4 VALUES (15, 86);
INSERT INTO Translated_Word_4 VALUES (16, 81);
INSERT INTO Translated_Word_4 VALUES (17, 90);

INSERT INTO Translated_Word_5 VALUES (12, 'HELP');
INSERT INTO Translated_Word_5 VALUES (13, 'PLEASE');
INSERT INTO Translated_Word_5 VALUES (14, 'SORRY');
INSERT INTO Translated_Word_5 VALUES (15, 'HELLO');
INSERT INTO Translated_Word_5 VALUES (16, 'HELP');
INSERT INTO Translated_Word_5 VALUES (17, 'PLEASE');

INSERT INTO Translated_Word_6 VALUES (12, 2);
INSERT INTO Translated_Word_6 VALUES (13, 2);
INSERT INTO Translated_Word_6 VALUES (14, 2);
INSERT INTO Translated_Word_6 VALUES (15, 2);
INSERT INTO Translated_Word_6 VALUES (16, 2);
INSERT INTO Translated_Word_6 VALUES (17, 2);


INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (4);
INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (5);

INSERT INTO Documented_Saved_Transcript_1 VALUES (204, 4);
INSERT INTO Documented_Saved_Transcript_1 VALUES (205, 5);

UPDATE Documented_Saved_Transcript_7 SET transcript_id = 204 WHERE recording_id = 4;
UPDATE Documented_Saved_Transcript_7 SET transcript_id = 205 WHERE recording_id = 5;

INSERT INTO Documented_Saved_Transcript_2 VALUES (204, 3);
INSERT INTO Documented_Saved_Transcript_2 VALUES (205, 3);

INSERT INTO Documented_Saved_Transcript_3 VALUES (204, 'GOOD YES HELLO THANK');
INSERT INTO Documented_Saved_Transcript_3 VALUES (205, 'NO SORRY');

INSERT INTO Documented_Saved_Transcript_4 VALUES (204, 4);
INSERT INTO Documented_Saved_Transcript_4 VALUES (205, 2);

INSERT INTO Documented_Saved_Transcript_5 VALUES (204, DATE '2025-12-10');
INSERT INTO Documented_Saved_Transcript_5 VALUES (205, DATE '2025-12-15');

INSERT INTO Documented_Saved_Transcript_6 VALUES (204, 'English');
INSERT INTO Documented_Saved_Transcript_6 VALUES (205, 'English');

INSERT INTO Documented_Saved_Transcript_8 VALUES (4, 3);
INSERT INTO Documented_Saved_Transcript_8 VALUES (5, 3);

INSERT INTO Documented_Saved_Transcript_9 VALUES (4, 'GOOD YES HELLO THANK');
INSERT INTO Documented_Saved_Transcript_9 VALUES (5, 'NO SORRY');

INSERT INTO Documented_Saved_Transcript_10 VALUES (4, 4);
INSERT INTO Documented_Saved_Transcript_10 VALUES (5, 2);

INSERT INTO Documented_Saved_Transcript_11 VALUES (4, DATE '2025-12-10');
INSERT INTO Documented_Saved_Transcript_11 VALUES (5, DATE '2025-12-15');

INSERT INTO Documented_Saved_Transcript_12 VALUES (4, 'English');
INSERT INTO Documented_Saved_Transcript_12 VALUES (5, 'English');

INSERT INTO Created_Documented_Recording VALUES (4, 204, 3, 30, DATE '2025-12-10', 'angel_session_1');
INSERT INTO Created_Documented_Recording VALUES (5, 205, 3, 15, DATE '2025-12-15', 'angel_session_2');

INSERT INTO Live  VALUES (4, 'webcam://device_1');
INSERT INTO Video VALUES (5, 45);

INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_thumb_up',     4, 1, TIMESTAMP '2025-12-10 11:00:00.000');
INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_victory_sign', 5, 1, TIMESTAMP '2025-12-15 13:00:00.000');

INSERT INTO Translated_Word_1 VALUES (18, 204);
INSERT INTO Translated_Word_1 VALUES (19, 204);
INSERT INTO Translated_Word_1 VALUES (20, 204);
INSERT INTO Translated_Word_1 VALUES (21, 204);
INSERT INTO Translated_Word_1 VALUES (22, 205);
INSERT INTO Translated_Word_1 VALUES (23, 205);

INSERT INTO Translated_Word_2 VALUES (18, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (19, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (20, 101); -- def 1
INSERT INTO Translated_Word_2 VALUES (21, 102); -- def 2
INSERT INTO Translated_Word_2 VALUES (22, 105); -- def 5
INSERT INTO Translated_Word_2 VALUES (23, 102); -- def 2

INSERT INTO Translated_Word_3 VALUES (18, 4);
INSERT INTO Translated_Word_3 VALUES (19, 3);
INSERT INTO Translated_Word_3 VALUES (20, 5);
INSERT INTO Translated_Word_3 VALUES (21, 5);
INSERT INTO Translated_Word_3 VALUES (22, 2);
INSERT INTO Translated_Word_3 VALUES (23, 5);

INSERT INTO Translated_Word_4 VALUES (18, 91);
INSERT INTO Translated_Word_4 VALUES (19, 94);
INSERT INTO Translated_Word_4 VALUES (20, 86);
INSERT INTO Translated_Word_4 VALUES (21, 90);
INSERT INTO Translated_Word_4 VALUES (22, 77);
INSERT INTO Translated_Word_4 VALUES (23, 84);

INSERT INTO Translated_Word_5 VALUES (18, 'GOOD');
INSERT INTO Translated_Word_5 VALUES (19, 'YES');
INSERT INTO Translated_Word_5 VALUES (20, 'HELLO');
INSERT INTO Translated_Word_5 VALUES (21, 'THANK');
INSERT INTO Translated_Word_5 VALUES (22, 'NO');
INSERT INTO Translated_Word_5 VALUES (23, 'SORRY');

INSERT INTO Translated_Word_6 VALUES (18, 3);
INSERT INTO Translated_Word_6 VALUES (19, 3);
INSERT INTO Translated_Word_6 VALUES (20, 3);
INSERT INTO Translated_Word_6 VALUES (21, 3);
INSERT INTO Translated_Word_6 VALUES (22, 4);
INSERT INTO Translated_Word_6 VALUES (23, 4);


INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (6);
INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (9);

INSERT INTO Documented_Saved_Transcript_1 VALUES (206, 6);
INSERT INTO Documented_Saved_Transcript_1 VALUES (209, 9);

UPDATE Documented_Saved_Transcript_7 SET transcript_id = 206 WHERE recording_id = 6;
UPDATE Documented_Saved_Transcript_7 SET transcript_id = 209 WHERE recording_id = 9;

INSERT INTO Documented_Saved_Transcript_2 VALUES (206, 4);
INSERT INTO Documented_Saved_Transcript_2 VALUES (209, 4);

INSERT INTO Documented_Saved_Transcript_3 VALUES (206, 'HELLO YES GOOD');
INSERT INTO Documented_Saved_Transcript_3 VALUES (209, 'YES HELLO GOOD');

INSERT INTO Documented_Saved_Transcript_4 VALUES (206, 3);
INSERT INTO Documented_Saved_Transcript_4 VALUES (209, 3);

INSERT INTO Documented_Saved_Transcript_5 VALUES (206, DATE '2026-01-05');
INSERT INTO Documented_Saved_Transcript_5 VALUES (209, DATE '2026-02-01');

INSERT INTO Documented_Saved_Transcript_6 VALUES (206, 'English');
INSERT INTO Documented_Saved_Transcript_6 VALUES (209, 'English');

INSERT INTO Documented_Saved_Transcript_8 VALUES (6, 4);
INSERT INTO Documented_Saved_Transcript_8 VALUES (9, 4);

INSERT INTO Documented_Saved_Transcript_9 VALUES (6, 'HELLO YES GOOD');
INSERT INTO Documented_Saved_Transcript_9 VALUES (9, 'YES HELLO GOOD');

INSERT INTO Documented_Saved_Transcript_10 VALUES (6, 3);
INSERT INTO Documented_Saved_Transcript_10 VALUES (9, 3);

INSERT INTO Documented_Saved_Transcript_11 VALUES (6, DATE '2026-01-05');
INSERT INTO Documented_Saved_Transcript_11 VALUES (9, DATE '2026-02-01');

INSERT INTO Documented_Saved_Transcript_12 VALUES (6, 'English');
INSERT INTO Documented_Saved_Transcript_12 VALUES (9, 'English');

INSERT INTO Created_Documented_Recording VALUES (6, 206, 4, 24, DATE '2026-01-05', 'justin_session_1');
INSERT INTO Created_Documented_Recording VALUES (9, 209, 4, 30, DATE '2026-02-01', 'justin_session_2');

INSERT INTO Live  VALUES (6, 'webcam://device_0');
INSERT INTO Video VALUES (9, 60);

INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_closed_fist', 6, 1, TIMESTAMP '2026-01-05 15:00:00.000');
INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_open_palm',   9, 1, TIMESTAMP '2026-02-01 11:00:00.000');

INSERT INTO Translated_Word_1 VALUES (24, 206);
INSERT INTO Translated_Word_1 VALUES (25, 206);
INSERT INTO Translated_Word_1 VALUES (26, 206);
INSERT INTO Translated_Word_1 VALUES (27, 209);
INSERT INTO Translated_Word_1 VALUES (28, 209);
INSERT INTO Translated_Word_1 VALUES (29, 209);

INSERT INTO Translated_Word_2 VALUES (24, 101); -- def 1
INSERT INTO Translated_Word_2 VALUES (25, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (26, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (27, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (28, 101); -- def 1
INSERT INTO Translated_Word_2 VALUES (29, 104); -- def 4

INSERT INTO Translated_Word_3 VALUES (24, 5);
INSERT INTO Translated_Word_3 VALUES (25, 3);
INSERT INTO Translated_Word_3 VALUES (26, 4);
INSERT INTO Translated_Word_3 VALUES (27, 3);
INSERT INTO Translated_Word_3 VALUES (28, 5);
INSERT INTO Translated_Word_3 VALUES (29, 4);

INSERT INTO Translated_Word_4 VALUES (24, 89);
INSERT INTO Translated_Word_4 VALUES (25, 93);
INSERT INTO Translated_Word_4 VALUES (26, 91);
INSERT INTO Translated_Word_4 VALUES (27, 94);
INSERT INTO Translated_Word_4 VALUES (28, 88);
INSERT INTO Translated_Word_4 VALUES (29, 92);

INSERT INTO Translated_Word_5 VALUES (24, 'HELLO');
INSERT INTO Translated_Word_5 VALUES (25, 'YES');
INSERT INTO Translated_Word_5 VALUES (26, 'GOOD');
INSERT INTO Translated_Word_5 VALUES (27, 'YES');
INSERT INTO Translated_Word_5 VALUES (28, 'HELLO');
INSERT INTO Translated_Word_5 VALUES (29, 'GOOD');

INSERT INTO Translated_Word_6 VALUES (24, 4);
INSERT INTO Translated_Word_6 VALUES (25, 4);
INSERT INTO Translated_Word_6 VALUES (26, 4);
INSERT INTO Translated_Word_6 VALUES (27, 4);
INSERT INTO Translated_Word_6 VALUES (28, 4);
INSERT INTO Translated_Word_6 VALUES (29, 4);

INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (7);
INSERT INTO Documented_Saved_Transcript_7 (recording_id) VALUES (10);

INSERT INTO Documented_Saved_Transcript_1 VALUES (207, 7);
INSERT INTO Documented_Saved_Transcript_1 VALUES (210, 10);

UPDATE Documented_Saved_Transcript_7 SET transcript_id = 207 WHERE recording_id = 7;
UPDATE Documented_Saved_Transcript_7 SET transcript_id = 210 WHERE recording_id = 10;

INSERT INTO Documented_Saved_Transcript_2 VALUES (207, 5);
INSERT INTO Documented_Saved_Transcript_2 VALUES (210, 5);

INSERT INTO Documented_Saved_Transcript_3 VALUES (207, 'THANK PLEASE YES SORRY GOOD');
INSERT INTO Documented_Saved_Transcript_3 VALUES (210, 'HELLO THANK YES GOOD PLEASE');

INSERT INTO Documented_Saved_Transcript_4 VALUES (207, 5);
INSERT INTO Documented_Saved_Transcript_4 VALUES (210, 5);

INSERT INTO Documented_Saved_Transcript_5 VALUES (207, DATE '2026-01-20');
INSERT INTO Documented_Saved_Transcript_5 VALUES (210, DATE '2026-02-15');

INSERT INTO Documented_Saved_Transcript_6 VALUES (207, 'English');
INSERT INTO Documented_Saved_Transcript_6 VALUES (210, 'English');

INSERT INTO Documented_Saved_Transcript_8 VALUES (7, 5);
INSERT INTO Documented_Saved_Transcript_8 VALUES (10, 5);

INSERT INTO Documented_Saved_Transcript_9 VALUES (7, 'THANK PLEASE YES SORRY GOOD');
INSERT INTO Documented_Saved_Transcript_9 VALUES (10, 'HELLO THANK YES GOOD PLEASE');

INSERT INTO Documented_Saved_Transcript_10 VALUES (7, 5);
INSERT INTO Documented_Saved_Transcript_10 VALUES (10, 5);

INSERT INTO Documented_Saved_Transcript_11 VALUES (7, DATE '2026-01-20');
INSERT INTO Documented_Saved_Transcript_11 VALUES (10, DATE '2026-02-15');

INSERT INTO Documented_Saved_Transcript_12 VALUES (7, 'English');
INSERT INTO Documented_Saved_Transcript_12 VALUES (10, 'English');

INSERT INTO Created_Documented_Recording VALUES (7,  207, 5, 30, DATE '2026-01-20', 'hao_session_1');
INSERT INTO Created_Documented_Recording VALUES (10, 210, 5, 24, DATE '2026-02-15', 'hao_session_2');

INSERT INTO Live  VALUES (7, 'webcam://device_2');
INSERT INTO Video VALUES (10, 200);

INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_closed_fist',  7, 1, TIMESTAMP '2026-01-20 09:00:00.000');
INSERT INTO Contained_Analyzed_Frame1 VALUES ('frame_data_victory_sign', 10, 1, TIMESTAMP '2026-02-15 14:00:00.000');

INSERT INTO Translated_Word_1 VALUES (30, 207);
INSERT INTO Translated_Word_1 VALUES (31, 207);
INSERT INTO Translated_Word_1 VALUES (32, 207);
INSERT INTO Translated_Word_1 VALUES (33, 207);
INSERT INTO Translated_Word_1 VALUES (34, 207);
INSERT INTO Translated_Word_1 VALUES (35, 210);
INSERT INTO Translated_Word_1 VALUES (36, 210);
INSERT INTO Translated_Word_1 VALUES (37, 210);
INSERT INTO Translated_Word_1 VALUES (38, 210);
INSERT INTO Translated_Word_1 VALUES (39, 210);

INSERT INTO Translated_Word_2 VALUES (30, 102); -- def 2
INSERT INTO Translated_Word_2 VALUES (31, 101); -- def 1
INSERT INTO Translated_Word_2 VALUES (32, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (33, 102); -- def 2
INSERT INTO Translated_Word_2 VALUES (34, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (35, 101); -- def 1
INSERT INTO Translated_Word_2 VALUES (36, 102); -- def 2
INSERT INTO Translated_Word_2 VALUES (37, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (38, 104); -- def 4
INSERT INTO Translated_Word_2 VALUES (39, 101); -- def 1

INSERT INTO Translated_Word_3 VALUES (30, 5);
INSERT INTO Translated_Word_3 VALUES (31, 6);
INSERT INTO Translated_Word_3 VALUES (32, 3);
INSERT INTO Translated_Word_3 VALUES (33, 5);
INSERT INTO Translated_Word_3 VALUES (34, 4);
INSERT INTO Translated_Word_3 VALUES (35, 5);
INSERT INTO Translated_Word_3 VALUES (36, 5);
INSERT INTO Translated_Word_3 VALUES (37, 3);
INSERT INTO Translated_Word_3 VALUES (38, 4);
INSERT INTO Translated_Word_3 VALUES (39, 6);

INSERT INTO Translated_Word_4 VALUES (30, 88);
INSERT INTO Translated_Word_4 VALUES (31, 92);
INSERT INTO Translated_Word_4 VALUES (32, 96);
INSERT INTO Translated_Word_4 VALUES (33, 85);
INSERT INTO Translated_Word_4 VALUES (34, 90);
INSERT INTO Translated_Word_4 VALUES (35, 91);
INSERT INTO Translated_Word_4 VALUES (36, 87);
INSERT INTO Translated_Word_4 VALUES (37, 95);
INSERT INTO Translated_Word_4 VALUES (38, 89);
INSERT INTO Translated_Word_4 VALUES (39, 93);

INSERT INTO Translated_Word_5 VALUES (30, 'THANK');
INSERT INTO Translated_Word_5 VALUES (31, 'PLEASE');
INSERT INTO Translated_Word_5 VALUES (32, 'YES');
INSERT INTO Translated_Word_5 VALUES (33, 'SORRY');
INSERT INTO Translated_Word_5 VALUES (34, 'GOOD');
INSERT INTO Translated_Word_5 VALUES (35, 'HELLO');
INSERT INTO Translated_Word_5 VALUES (36, 'THANK');
INSERT INTO Translated_Word_5 VALUES (37, 'YES');
INSERT INTO Translated_Word_5 VALUES (38, 'GOOD');
INSERT INTO Translated_Word_5 VALUES (39, 'PLEASE');

INSERT INTO Translated_Word_6 VALUES (30, 5);
INSERT INTO Translated_Word_6 VALUES (31, 5);
INSERT INTO Translated_Word_6 VALUES (32, 5);
INSERT INTO Translated_Word_6 VALUES (33, 5);
INSERT INTO Translated_Word_6 VALUES (34, 5);
INSERT INTO Translated_Word_6 VALUES (35, 5);
INSERT INTO Translated_Word_6 VALUES (36, 5);
INSERT INTO Translated_Word_6 VALUES (37, 5);
INSERT INTO Translated_Word_6 VALUES (38, 5);
INSERT INTO Translated_Word_6 VALUES (39, 5);


INSERT INTO Documented_Saved_Transcript_13 VALUES ('HELLO THANK HELP YES NO PLEASE', 6);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('YES NO SORRY GOOD HELLO', 5);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('HELP PLEASE SORRY', 3);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('HELLO HELP PLEASE', 3);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('GOOD YES HELLO THANK', 4);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('NO SORRY', 2);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('HELLO YES GOOD', 3);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('YES HELLO GOOD', 3);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('THANK PLEASE YES SORRY GOOD', 5);
INSERT INTO Documented_Saved_Transcript_13 VALUES ('HELLO THANK YES GOOD PLEASE', 5);

INSERT INTO Documented_Saved_Transcript_14 VALUES ('HELLO THANK HELP YES NO PLEASE', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('YES NO SORRY GOOD HELLO', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('HELP PLEASE SORRY', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('HELLO HELP PLEASE', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('GOOD YES HELLO THANK', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('NO SORRY', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('HELLO YES GOOD', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('YES HELLO GOOD', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('THANK PLEASE YES SORRY GOOD', 'English');
INSERT INTO Documented_Saved_Transcript_14 VALUES ('HELLO THANK YES GOOD PLEASE', 'English');