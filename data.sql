CREATE TABLE Calibrated_User( 

user_id INT PRIMARY KEY, 

def_id INT, 

date_of_creation DATE NOT NULL, 

email VARCHAR[50] NOT NULL, 

name VARCHAR[50], 

UNIQUE(email), 

FOREIGN KEY(def_id) REFERENCES Calibrated_Definition(def_id)) 

 

Deleting a definition does not logically require deleting the user. Therefore, ON DELETE does not need to cascade. 

 

CREATE TABLE Calibrated_Definition( 

def_id INT PRIMARY KEY,  

user_id INT, 

gesture VARCHAR[255] NOT NULL,  

def_name VARCHAR[50] NOT NULL,  

description VARCHAR[255] 

FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 	 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the user_id foreign key because a definition cannot exist without the user who created it. 

 

CREATE TABLE Created_Documented_Recording( 

recording_id INT PRIMARY KEY, 

transcript_id INT, 

user_id INT,  

fps INT NOT NULL, 

recording_date DATE NOT NULL,  

recording_name VARCHAR[50] NOT NULL, 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1  

(transcript_id), 

FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 

ON DELETE CASCADE, 

UNIQUE(recording_name)) 

 

We used ON DELETE CASCADE for the user_id foreign key because a Recording cannot exist without the user who created it. 

 

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

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording _id foreign key because a Frame cannot exist without the original recording. 

 

We used ON DELETE CASCADE for the data foreign key because a Frame cannot exist without the data in the Frame itself. 

 

CREATE TABLE Contained_Analyzed_Frame2( 

data VARCHAR[255] PRIMARY KEY, 

resolution VARCHAR[255] NOT NULL) 

 

CREATE TABLE Live( 

recording_id INT PRIMARY KEY, 

livestream_source VARCHAR[255] NOT NULL, 

FOREIGN KEY (recording_id) REFERENCES  

Created_Documented_Recording(recording_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording_id foreign key because a Live cannot exist without the original recording. 

 

CREATE TABLE Video( 

recording_id INT PRIMARY KEY, 

duration INT NOT NULL, 

FOREIGN KEY (recording_id) REFERENCES Created_Documented_Recording 	 

(recording_id) 

ON DELETE CASCADE) 

We used ON DELETE CASCADE for the recording_id foreign key because a Video cannot exist without the original recording. 

 

CREATE TABLE Documented_Saved_Transcript_1 ( 

transcript_id INT PRIMARY KEY, 

recording_id INT, 

FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 		(recording_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording_id foreign key because a Transcript cannot exist without the original recording. 

  

CREATE TABLE Documented_Saved_Transcript_2 ( 

transcript_id INT PRIMARY KEY, 

user_id INT, 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 		(transcript_id) 

ON DELETE CASCADE, 

FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the transcript_id foreign key because this relation cannot exist without the transcript. 

 

We used ON DELETE CASCADE for the user_id foreign key because a Transcript cannot exist without the user who wants the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_3 ( 

transcript_id INT PRIMARY KEY, 

transcript_data VARCHAR[255], 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 		(transcript_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the transcript_id foreign key because this relation cannot exist without the transcript. 

 

  

CREATE TABLE Documented_Saved_Transcript_4 ( 

transcript_id INT PRIMARY KEY, 

word_count INT 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 		(transcript_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the transcript_id foreign key because this relation cannot exist without the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_5 ( 

transcript_id INT PRIMARY KEY, 

transcription_date date, 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 		(transcript_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the transcript_id foreign key because this relation cannot exist without the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_6 ( 

transcript_id INT PRIMARY KEY, 

language VARCHAR[50], 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 		(transcript_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the transcript_id foreign key because this relation cannot exist without the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_7 ( 

recording_id INT PRIMARY KEY, 

transcript_id INT, 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 		(transcript_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the transcript_id foreign key because this relation cannot exist without the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_8 ( 

recording_id INT PRIMARY KEY, 

user_id INT, 

FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 		(recording_id) 

ON DELETE CASCADE, 

FOREIGN KEY (user_id) REFERENCES Calibrated_User (user_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording _id foreign key because a transcript cannot exist without the original recording. 

 

We used ON DELETE CASCADE for the user_id foreign key because a Transcript cannot exist without the user who wants the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_9 ( 

recording_id INT PRIMARY KEY, 

transcript_data VARCHAR[255], 

FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 

ON DELETE CASCADE, 

FOREIGN KEY (transcript_data) REFERENCES Documented_Saved_Transcript_10 (transcript_data) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording_id foreign key because a transcript cannot exist without the original recording. 

 

We used ON DELETE CASCADE for the transcript_ data foreign key because a transcript cannot exist without the content of the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_10 ( 

recording_id INT PRIMARY KEY, 

word_count INT, 

FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording_id foreign key because a transcript cannot exist without the original recording. 

  

CREATE TABLE Documented_Saved_Transcript_11 ( 

recording_id INT PRIMARY KEY, 

transcription_date date, 

FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 

ON DELETE CASCADE, 

FOREIGN KEY (transcript_data) REFERENCES Documented_Saved_Transcript_10 (transcript_data) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording_id foreign key because a transcript cannot exist without the original recording. 

 

We used ON DELETE CASCADE for the transcript_data foreign key because a transcript cannot exist without the content of the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_12 ( 

recording_id INT PRIMARY KEY, 

language VARCHAR[50], 

FOREIGN KEY (recording_id) REFERENCES Documented_Saved_Transcript_7 (recording_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the recording_id foreign key because a transcript cannot exist without the original recording. 

  

CREATE TABLE Documented_Saved_Transcript_13 ( 

transcript_data VARCHAR[255] PRIMARY KEY, 

word_count INT, 

FOREIGN KEY (transcript_data) REFERENCES Documented_Saved_Transcript_10 (transcript_data) 

ON DELETE CASCADE) 

We used ON DELETE CASCADE for the transcript_data foreign key because a transcript cannot exist without the content of the transcript. 

  

CREATE TABLE Documented_Saved_Transcript_14 ( 

transcript_data VARCHAR[255] PRIMARY KEY, 

language VARCHAR[50], 

FOREIGN KEY (	transcript_data) REFERENCES Documented_Saved_Transcript1 (transcript_id) 

ON DELETE CASCADE) 

 

We used ON DELETE CASCADE for the transcript_data foreign key because a transcript cannot exist without the content of the transcript. 

 

CREATE TABLE Translated_Word_1 ( 

instance_id INT PRIMARY KEY,  

transcript_id INT, 

FOREIGN KEY (transcript_id) REFERENCES Documented_Saved_Transcript_1 		(transcript_id)  

ON DELETE CASCADE)  

 

ON DELETE CASCADE was used for transcript_id  as all words must belong in the specific transcript tied to the specific recording uploaded by the user. 

 

CREATE TABLE Translated_Word_2 ( 

instance_id INT PRIMARY KEY,  

handmark_id INT, 

FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark1 		(handmark_id)  

ON DELETE CASCADE, 

FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 

ON DELETE CASCADE) 

 

ON DELETE CASCADE was used for handmark_id as we cannot determine the translated word without being given a specific handmark from the specific recording, and it was used for translation as this relation cannot exist without the original translation key in Translated_Word_7. 

 

CREATE TABLE Translated_Word_3 ( 

instance_id INT PRIMARY KEY,  

character_length INT, 

FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 

ON DELETE CASCADE) 

 

ON DELETE CASCADE was used for translation and instance_id as this relation cannot exist without the original keys in Translated_Word_7 and Translated_Word_1. 

 

CREATE TABLE Translated_Word_4 ( 

instance_id INT PRIMARY KEY,  

translation_confidence INT, 

FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 

ON DELETE CASCADE) 

 

ON DELETE CASCADE was used for instance_id as this relation cannot exist without the original key in Translated_Word_1. 

 

CREATE TABLE Translated_Word_5 ( 

instance_id INT PRIMARY KEY,  

translation VARCHAR[255] NOT NULL, 

FOREIGN KEY (translation) REFERENCES Translated_Word_7 (translation)  

ON DELETE CASCADE, 

FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 

ON DELETE CASCADE, 

UNIQUE (translation)) 

 

ON DELETE CASCADE was used for translation and instance_id as this relation cannot exist without the original keys in Translated_Word_7 and Translated_Word_1. 

 

CREATE TABLE Translated_Word_6 ( 

instance_id INT PRIMARY KEY,  

model_id INT, 

FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) 

ON DELETE CASCADE, 

FOREIGN KEY (instance_id) REFERENCES Translated_Word_1 (instance_id) 

ON DELETE CASCADE) 

 

ON DELETE CASCADE was used for model_id as we cannot determine the translated word without using the specific model based on this specific user’s definitions, and it was used for instance_id as this relation cannot exist without the original key in Translated_Word_1. 

 

CREATE TABLE Translated_Word_7 ( 

Translation VARCHAR[255] PRIMARY KEY, 

character_length INT) 

 

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

ON DELETE CASCADE) 

 

ON DELETE CASCADE was used for handmark_id as we cannot determine the translated word without being given a specific handmark from the specific recording, and it was used for translation as this relation cannot exist without the original translation key in Translated_Word_7. 

 

CREATE TABLE Translated_Word_9 ( 

handmark_id INT PRIMARY KEY, 

word_timestamp TIMESTAMP NOT NULL, 

FOREIGN KEY (handmark_id) REFERENCES 							Predicted_Gesture_Handmark1(handmark_id) 

ON DELETE CASCADE) 

 

ON DELETE CASCADE was used for handmark_id as we cannot determine the translated word without being given a specific handmark from the specific recording. 

 

CREATE TABLE Predicted_Gesture_Handmark1( 

handmark_id INT PRIMARY KEY, 

def_id INT, 

model_id INT, 

FOREIGN KEY (model_id) REFERENCES Trained_Machine_Learning_Model (model_id) 

ON DELETE CASCADE, 

FOREIGN KEY (def_id) REFERENCES Predicted_Gesture_Handmark2(def_id) 

ON DELETE CASCADE) 

 

ON DELETE CASCADE was used for model_id and def_id as we cannot predict the gesture without the specific model and definitions unique to the user. 

 

CREATE TABLE Predicted_Gesture_Handmark2( 

def_id INT PRIMARY KEY, 

number_of_frames INT NOT NULL, 

x_position VARCHAR[255] NOT NULL, 

y_position VARCHAR[255] NOT NULL, 

UNIQUE(x_position, y_position)) 

 

CREATE TABLE Trained_Machine_Learning_Model( 

model_id INT PRIMARY KEY, 

handmark_id INT, 

accuracy INT, 

hyperparameter INT NOT NULL, 

model_type VARCHAR[255], 

FOREIGN KEY (handmark_id) REFERENCES Predicted_Gesture_Handmark 			(handmark_id)) 