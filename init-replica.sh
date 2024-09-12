#!/bin/bash
# Wait for other MongoDB instances to be up and running
sleep 10

# Run the MongoDB shell command to initiate the replica set
mongo -- "$MONGO_INITDB_DATABASE" <<EOF
var config = {
    "_id": "rs0",
    "members": [
        { "_id": 0, "host": "mongo1:27017" },
        { "_id": 1, "host": "mongo2:27017" },
        { "_id": 2, "host": "mongo3:27017" }
    ]
};
rs.initiate(config);
rs.status();
EOF