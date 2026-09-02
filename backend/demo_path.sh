#!/bin/bash
set -e
echo "1. POST /dev/auth/token"
TOKEN=$(curl -s -X POST http://localhost:8000/dev/auth/token -H "Content-Type: application/json" -d '{"email": "demo@sarathi.app"}' | jq -r .access_token)
echo "Token: ${TOKEN:0:10}..."

echo -e "\n2. GET /api/v1/me"
curl -s -X GET http://localhost:8000/api/v1/me -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n2b. PATCH /api/v1/profile/learner"
PROFILE_RES=$(curl -s -X PATCH http://localhost:8000/api/v1/profile/learner -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"learning_style": "visual", "difficulty_preference": "adaptive"}')
echo "$PROFILE_RES" | jq .

echo -e "\n3. POST /api/v1/goals"
GOAL_RES=$(curl -s -X POST http://localhost:8000/api/v1/goals -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"raw_input": "Master Arrays and Strings for tech interviews"}')
echo "$GOAL_RES" | jq .
GOAL_ID=$(echo "$GOAL_RES" | jq -r .id)

echo -e "\n4. POST /api/v1/goals/${GOAL_ID}/plan"
PLAN_RES=$(curl -s -X POST http://localhost:8000/api/v1/goals/${GOAL_ID}/plan -H "Authorization: Bearer $TOKEN")
echo "$PLAN_RES" | jq .
JOB_ID=$(echo "$PLAN_RES" | jq -r .job_id)

echo -e "\n5. GET /api/v1/jobs/${JOB_ID} (polling up to 60 times)"
for i in {1..60}; do
  JOB_STATUS=$(curl -s -X GET http://localhost:8000/api/v1/jobs/${JOB_ID} -H "Authorization: Bearer $TOKEN")
  STATUS=$(echo "$JOB_STATUS" | jq -r .status)
  if [ "$STATUS" = "succeeded" ]; then
    echo "$JOB_STATUS" | jq .
    PLAN_ID=$(echo "$JOB_STATUS" | jq -r .result.plan_id)
    break
  fi
  if [ "$STATUS" = "failed" ]; then
    echo "$JOB_STATUS" | jq .
    exit 1
  fi
  sleep 1
done

echo -e "\n6. GET /api/v1/plans/${PLAN_ID}"
PLAN_DATA=$(curl -s -X GET http://localhost:8000/api/v1/plans/${PLAN_ID} -H "Authorization: Bearer $TOKEN")
echo "$PLAN_DATA" | jq .
LESSON_ID=$(echo "$PLAN_DATA" | jq -r '.modules[0].lessons[0].id')

echo -e "\n7. GET /api/v1/lessons/${LESSON_ID}/content (stream)"
curl -N -s -X GET http://localhost:8000/api/v1/lessons/${LESSON_ID}/content -H "Authorization: Bearer $TOKEN"

