#!/bin/bash

# ------------------------------
# Script to send HTTP requests with optional delay between requests
#
# Usage:
#   ./loadtest.sh <function> [args...]
#
# Example:
#   ./loadtest.sh send_basic_requests 5 250
#     -> sends 5 requests with 250ms delay between each
#

# werkzeug -> 5000
# nginx    -> 8080
PORT=8080

send_basic_requests() {
  COUNT=$1
  SLEEP_MS=${2:-250}  # Default 250 ms if not provided

  if [ -z "$COUNT" ]; then
    echo "Usage: send_basic_requests <number_of_requests> [sleep_ms]"
    return 1
  fi

  for i in $(seq 1 "$COUNT"); do
    echo "Request #$i"
    curl -s http://localhost:$PORT
    echo -e "\n---"
    # Convert ms to seconds for sleep command (e.g. 250ms = 0.25s)
    sleep_sec=$(awk "BEGIN {print $SLEEP_MS/1000}")
    sleep $sleep_sec
  done
}

COMMAND=$1
shift # remove the command name from arguments

case "$COMMAND" in
  send_basic_requests)
    send_basic_requests "$@"
    ;;
  ""|help)
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Available commands:"
    echo "  send_basic_requests <count> [sleep_ms]  Send multiple GET requests with optional delay in ms"
    ;;
  *)
    echo "Unknown command: $COMMAND"
    echo "Run '$0 help' for usage."
    exit 1
    ;;
esac