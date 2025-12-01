#!/bin/bash

# Set Oracle environment
if [ -d /opt/oracle/instantclient_23_7 ]; then
    export ORACLE_HOME=/opt/oracle/instantclient_23_7
    export LD_LIBRARY_PATH=$ORACLE_HOME
elif [ -d /usr/lib/oracle/19.6/client64/lib ]; then
    export ORACLE_HOME=/usr/lib/oracle/19.6/client64
    # 19.* libraries will be already configured by ldconfig
    #export LD_LIBRARY_PATH=$ORACLE_HOME/lib
elif [ -d /usr/lib/oracle/12.2/client64/lib ]; then
    export ORACLE_HOME=/usr/lib/oracle/12.2/client64
    export LD_LIBRARY_PATH=$ORACLE_HOME/lib
else
    echo "Oracle not found..."
    exit 1
fi


# Configure the shared Node library on the undergrad server.
export NODE_PATH=/cs/local/generic/lib/cs304/node_modules

# File path
ENV_SERVER_PATH="./.env"

# Check the database host name and port
sed -i "/^ORACLE_HOST=/c\ORACLE_HOST=dbhost.students.cs.ubc.ca" $ENV_SERVER_PATH
sed -i "/^ORACLE_PORT=/c\ORACLE_PORT=1522" $ENV_SERVER_PATH

# Define starting port
START=49152
TEAM_NUMBER= # PUT YOUR TEAM NUMBER HERE!!!
MAX_PORT=65535

# Check if TEAM_NUMBER is set
if [ -z "$TEAM_NUMBER" ]; then
    echo "TEAM_NUMBER needs to be set in remote-start.sh script"
    exit 1
fi

# Loop through ports, incrementing by 200 until an available port is found
PORT=$((START + TEAM_NUMBER))
while [ $PORT -le $MAX_PORT ]; do
    # Check if the port is in use
    if ! ss -tuln | grep :$PORT > /dev/null; then
        # Bind to the port using a temporary process
        nc -l -p $PORT &
        TEMP_PID=$!

        # Update the port number in the .env file
        sed -i "/^PORT=/c\PORT=$PORT" $ENV_SERVER_PATH
        echo "Updated $ENV_SERVER_PATH with PORT=$PORT."

        # Kill the temporary process
        kill $TEMP_PID

        # Replace the bash process with the Node process
        exec node server.js
        break
    fi
    
    # Increment port by 200 and try again
    PORT=$((PORT + 200))
done

# If no available port was found
if [ $PORT -gt $MAX_PORT ]; then
    echo "No available port found between $START and $MAX_PORT"
    exit 1
fi

