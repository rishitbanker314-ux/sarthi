#!/bin/bash
set -e

BASE="http://127.0.0.1:8000"

echo "=== Fetching token ==="
TOKEN_RES=$(curl -s -X POST "$BASE/dev/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com"}')
TOKEN=$(echo "$TOKEN_RES" | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "FAILED to get token. Response:"
    echo "$TOKEN_RES"
    exit 1
fi
echo "Token acquired ✓"

echo ""
echo "=== Starting diagnostic session ==="
SESSION_RES=$(curl -s -X POST "$BASE/api/v1/diagnostic/sessions" \
  -H "Authorization: Bearer $TOKEN")
SESSION_ID=$(echo "$SESSION_RES" | jq -r '.id')

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo "FAILED to create session. Response:"
    echo "$SESSION_RES" | jq .
    exit 1
fi
echo "Session created: $SESSION_ID ✓"

# Pre-defined answers to cycle through
ANSWERS=(
  "I am a frontend developer who wants to learn backend development."
  "I prefer project-based learning with real examples."
  "I have about 2 years of experience with JavaScript and React."
  "I want to learn Python and system design."
  "I can dedicate about 10 hours per week."
  "I learn best through hands-on coding exercises."
  "I prefer to understand theory before practicing."
  "My goal is to become a full-stack developer."
  "I find databases and APIs most interesting."
  "I struggle most with understanding distributed systems."
  "I have some experience with REST APIs."
  "I prefer structured courses over free-form exploration."
)

# Loop: answer questions until session is complete
STEP=0
MAX_STEPS=15

while [ $STEP -lt $MAX_STEPS ]; do
  STEP=$((STEP + 1))
  ANSWER_IDX=$(( (STEP - 1) % ${#ANSWERS[@]} ))
  ANSWER="${ANSWERS[$ANSWER_IDX]}"

  echo ""
  echo "=== Answering question $STEP ==="
  ANSWER_RES=$(curl -s -X POST "$BASE/api/v1/diagnostic/sessions/$SESSION_ID/answer" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"answer\": \"$ANSWER\"}")

  STATUS=$(echo "$ANSWER_RES" | jq -r '.status')
  COMPLETE=$(echo "$ANSWER_RES" | jq -r '.complete')
  ANSWERED=$(echo "$ANSWER_RES" | jq -r '.progress.answered')
  TOTAL=$(echo "$ANSWER_RES" | jq -r '.progress.estimated_total')

  echo "  Status: $STATUS | Complete: $COMPLETE | Progress: $ANSWERED/$TOTAL"

  if [ "$COMPLETE" = "true" ]; then
    echo ""
    echo "=== Session marked complete by agent ==="
    break
  fi

  # Check for errors
  ERROR=$(echo "$ANSWER_RES" | jq -r '.error.code // empty')
  if [ -n "$ERROR" ]; then
    echo "  ERROR: $ERROR"
    echo "$ANSWER_RES" | jq .
    break
  fi
done

echo ""
echo "=== Completing session ==="
COMPLETE_RES=$(curl -s -X POST "$BASE/api/v1/diagnostic/sessions/$SESSION_ID/complete" \
  -H "Authorization: Bearer $TOKEN")
echo "$COMPLETE_RES" | jq .

echo ""
echo "=== Done! ==="
