#!/bin/bash
# minimal_chaos_test.sh
# Run this from the root of your Styx project where docker-compose.yml lives.
# This script kills and restarts containers randomly while traffic is flowing.

echo "🔥 Starting Minimal Chaos Test 🔥"
echo "Make sure docker-compose up -d and python backend/scripts/traffic_loop.py are already running in another terminal."
echo "Press Ctrl+C to stop."

CONTAINERS=("styx-nginx-1" "styx-mock-services-1" "styx-db-1")

while true; do
    # Sleep between 5 and 15 seconds
    SLEEP_TIME=$((5 + RANDOM % 11))
    echo "[*] Waiting for ${SLEEP_TIME} seconds before next chaos event..."
    sleep $SLEEP_TIME

    # Pick a random container
    TARGET=${CONTAINERS[$RANDOM % ${#CONTAINERS[@]}]}

    echo "⚠️  Killing container: $TARGET"
    docker kill $TARGET

    # Wait briefly while it's down
    DOWN_TIME=$((2 + RANDOM % 4))
    echo "[*] Container $TARGET is down for ${DOWN_TIME} seconds."
    sleep $DOWN_TIME

    echo "✅ Restarting container: $TARGET"
    docker start $TARGET

    # If we killed Postgres, the ingestor or API might complain briefly,
    # but SQLAlchemy's pool (with pre-ping) should recover automatically.
done
