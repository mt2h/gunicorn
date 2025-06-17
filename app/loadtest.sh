#!/bin/bash

requests() {
  COUNT=$1
  SLEEP=15

  if [ -z "$COUNT" ]; then
    echo "Usage: requests <number_of_requests>"
    return 1
  fi

  for i in $(seq 1 "$COUNT"); do
    echo "Request #$i"
    TIMESTAMP=$(date +%s)
    curl -s "http://localhost:8080/quotation?sleep=${SLEEP}&timestamp=${TIMESTAMP}"
    echo -e "\n---"
  done
}

COMMAND=$1
shift # remove the command name from arguments

case "$COMMAND" in
  requests)
    requests "$@"
    ;;
  ""|help)
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Available commands:"
    echo "  requests <count>    Send multiple GET requests to /quotation with sleep"
    ;;
  *)
    echo "Unknown command: $COMMAND"
    echo "Run '$0 help' for usage."
    exit 1
    ;;
esac
