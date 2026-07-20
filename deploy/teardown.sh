#!/usr/bin/env bash
# Tear down the Fargate deployment. RUN THIS IN THE SAME SITTING AS deploy.sh.
#
# This is not optional hygiene. The Learner Lab disables the ENTIRE account
# and deletes all resources if the budget is exceeded, and the budget display
# lags 8-12 hours behind real spend. Ending the lab session is only
# documented to stop EC2 instances — assume a running Fargate service keeps
# billing between sessions.
#
# Usage:
#   bash teardown.sh                # delete service + cluster
#   bash teardown.sh --delete-ecr   # also delete the ECR repo and its images

set -euo pipefail

REGION="us-east-1"
export AWS_DEFAULT_REGION="$REGION"
REPO_NAME="research-matchmaker"
CLUSTER="matchmaker-cluster"
SERVICE="matchmaker-service"
SG_NAME="matchmaker-8000"

DELETE_ECR=false
if [ "${1:-}" = "--delete-ecr" ]; then
  DELETE_ECR=true
fi

CURRENT_STEP="startup"
step() { CURRENT_STEP="$1"; printf '\n==> %s\n' "$1"; }
trap 'printf "\nTEARDOWN FAILED at step: %s\n" "$CURRENT_STEP" >&2' ERR

step "Verify AWS credentials"
if ! aws sts get-caller-identity --query Account --output text >/dev/null 2>&1; then
  echo "Could not verify AWS credentials. Paste fresh session credentials" >&2
  echo "from the lab's AWS Details panel into ~/.aws/credentials and rerun." >&2
  exit 1
fi

step "Scale service '$SERVICE' to 0 and delete it"
SERVICE_STATUS=$(aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --query 'services[0].status' --output text 2>/dev/null || echo "NONE")
if [ "$SERVICE_STATUS" = "ACTIVE" ] || [ "$SERVICE_STATUS" = "DRAINING" ]; then
  aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" \
    --desired-count 0 >/dev/null 2>&1 || true
  aws ecs delete-service --cluster "$CLUSTER" --service "$SERVICE" --force >/dev/null
  echo "Service deleted (tasks are stopping)."
else
  echo "No active service found — nothing to delete."
fi

step "Wait for tasks to stop"
aws ecs wait services-inactive --cluster "$CLUSTER" --services "$SERVICE" 2>/dev/null || true
REMAINING=$(aws ecs list-tasks --cluster "$CLUSTER" --query 'taskArns' --output text 2>/dev/null || echo "")
if [ -n "$REMAINING" ] && [ "$REMAINING" != "None" ]; then
  echo "WARNING: tasks still listed in cluster: $REMAINING" >&2
  echo "Verify in the ECS console that they reach STOPPED." >&2
else
  echo "No tasks remain in the cluster."
fi

step "Delete cluster '$CLUSTER'"
if aws ecs delete-cluster --cluster "$CLUSTER" >/dev/null 2>&1; then
  echo "Cluster deleted."
else
  echo "Cluster not found or already deleted."
fi

if [ "$DELETE_ECR" = true ]; then
  step "Delete ECR repository '$REPO_NAME' (--delete-ecr)"
  if aws ecr delete-repository --repository-name "$REPO_NAME" --force >/dev/null 2>&1; then
    echo "ECR repository and images deleted."
  else
    echo "ECR repository not found or already deleted."
  fi
else
  echo
  echo "ECR repository '$REPO_NAME' kept (stored images cost little and speed"
  echo "up the next deploy). Pass --delete-ecr to remove it too."
fi

printf '\n================================================================\n'
echo "Teardown complete. Double-check in the console that the ECS cluster"
echo "shows no running tasks. The '$SG_NAME' security group and the"
echo "CloudWatch log group are retained; neither accrues meaningful cost."
printf '================================================================\n'
