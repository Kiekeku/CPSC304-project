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
    transcript_data VARCHAR2(255),
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
