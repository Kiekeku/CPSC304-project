# Node Project Setup

Please refer to the [sample project setup instructions here](https://www.students.cs.ubc.ca/~cs-304/resources/javascript-oracle-resources/node-setup.html#remote-deploy-item) for more in-depth instructions.

## Prerequisites

- Access to UBC CS undergrad server

## Setup Instructions (Remote)

### 1. Create Environment File

Create a `.env` file in the root directory of the project with the following contents:

```
# TODO: Edit the values below this line according to the given placeholders
# Replace 'ora_YOUR-CWL-USERNAME' with "ora_" (no quotation marks) followed by your CWL username.
ORACLE_USER=ora_YOUR-CWL-USERNAME
# Replace 'YOUR-STUDENT-NUMBER' with your actual student number.
ORACLE_PASS=aYOUR-STUDENT-NUMBER


#Adjust the PORT if needed (e.g., if you encounter a "port already occupied" error)
PORT=65535

# -------------- The three lines below should be left unaltered --------------
ORACLE_HOST=dbhost.students.cs.ubc.ca
ORACLE_PORT=1522
ORACLE_DBNAME=stu

```

### 2. Configure Team Number
**Only perform this step if you want to run the project on the remote servers**

Open the `remote-start.sh` script and set your team number:

```bash
TEAM_NUMBER=... # Replace ... with your actual team number here
```

### 3. Run the Application

Execute the remote start script:

```bash
./remote-start.sh
```
