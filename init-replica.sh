#!/bin/bash

RETRIES=10

until docker exec mongo1 mongosh --host 172.20.0.2 --eval "print(\"waited for connection\")"
do
  echo "waiting for MongoDB to be ready..."
  sleep 5
  RETRIES=$((RETRIES-1))
  if [ $RETRIES -lt 1 ]
  then
    echo "Giving up!"
    exit 1
  fi
done

echo "Connected. Initializing replica set..."

docker exec mongo1 mongosh --host 172.20.0.2 <<EOF
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "172.20.0.2:27017" },
    { _id: 1, host: "172.20.0.3:27017" },
    { _id: 2, host: "172.20.0.4:27017" }
  ]
})
EOF

echo "Replica set initialized."

echo "Setup complete."