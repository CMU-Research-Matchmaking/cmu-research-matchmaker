#!/usr/bin/env bash
# Deploy the research-matchmaker container to ECS Fargate in the AWS Academy
# Learner Lab sandbox. Read deploy/README.md before the first run.
#
# Learner Lab constraints baked into this script:
#   - Region must be us-east-1 (the lab restricts to us-east-1/us-west-2).
#   - No IAM role creation: the pre-provisioned LabRole is BOTH the task role
#     and the execution role (per the lab's own ECS guidance), substituted
#     into deploy/task-definition.json.
#   - The whole script runs under the per-session credentials pasted into
#     ~/.aws/credentials. The ECR push MUST run under those credentials:
#     LabRole is read-only on ECR (pulls only). Never assume LabRole here.
#   - Fargate is available in the lab; App Runner is not.
#
# When done: run deploy/teardown.sh IN THE SAME SITTING. See deploy/README.md.

set -euo pipefail

REGION="us-east-1"
export AWS_DEFAULT_REGION="$REGION"
REPO_NAME="research-matchmaker"
IMAGE_TAG="latest"
CLUSTER="matchmaker-cluster"
SERVICE="matchmaker-service"
LOG_GROUP="/ecs/research-matchmaker"
SG_NAME="matchmaker-8000"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CURRENT_STEP="startup"
step() { CURRENT_STEP="$1"; printf '\n==> %s\n' "$1"; }
trap 'printf "\nDEPLOY FAILED at step: %s\n" "$CURRENT_STEP" >&2' ERR

step "Verify AWS credentials (aws sts get-caller-identity)"
if ! ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null); then
  cat >&2 <<'EOF'
Could not verify AWS credentials.

Start the Learner Lab, open the "AWS Details" panel, click "Show" next to
"AWS CLI", and paste the whole [default] block (aws_access_key_id,
aws_secret_access_key, aws_session_token) into ~/.aws/credentials.
Credentials are per-session and expire when the lab session ends.
EOF
  exit 1
fi
echo "Authenticated to account: $ACCOUNT_ID"

ECR_REGISTRY="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
IMAGE_URI="$ECR_REGISTRY/$REPO_NAME:$IMAGE_TAG"

step "Ensure ECR repository '$REPO_NAME'"
if aws ecr describe-repositories --repository-names "$REPO_NAME" >/dev/null 2>&1; then
  echo "ECR repository already exists."
else
  aws ecr create-repository --repository-name "$REPO_NAME" >/dev/null
  echo "Created ECR repository."
fi

step "Build image for linux/amd64"
docker build --platform linux/amd64 -t "$REPO_NAME:$IMAGE_TAG" "$REPO_ROOT"

step "Log in to ECR and push (under session credentials — LabRole cannot push)"
aws ecr get-login-password | docker login --username AWS --password-stdin "$ECR_REGISTRY"
docker tag "$REPO_NAME:$IMAGE_TAG" "$IMAGE_URI"
docker push "$IMAGE_URI"

step "Ensure CloudWatch log group '$LOG_GROUP'"
if aws logs create-log-group --log-group-name "$LOG_GROUP" 2>/dev/null; then
  echo "Created log group."
else
  echo "Log group already exists."
fi

step "Register task definition (LabRole as task AND execution role)"
TASK_DEF_TMP="$SCRIPT_DIR/task-definition.rendered.json"
sed -e "s|__ACCOUNT_ID__|$ACCOUNT_ID|g" -e "s|__IMAGE_URI__|$IMAGE_URI|g" \
  "$SCRIPT_DIR/task-definition.json" > "$TASK_DEF_TMP"
command -v cygpath >/dev/null && TASK_DEF_TMP="$(cygpath -m "$TASK_DEF_TMP")"
TASK_DEF_ARN=$(aws ecs register-task-definition --cli-input-json "file://$TASK_DEF_TMP" \
  --query 'taskDefinition.taskDefinitionArn' --output text)
rm -f "$TASK_DEF_TMP"
echo "Registered: $TASK_DEF_ARN"

step "Ensure ECS cluster '$CLUSTER'"
CLUSTER_STATUS=$(aws ecs describe-clusters --clusters "$CLUSTER" \
  --query 'clusters[0].status' --output text 2>/dev/null || echo "NONE")
if [ "$CLUSTER_STATUS" = "ACTIVE" ]; then
  echo "Cluster already exists."
else
  aws ecs create-cluster --cluster-name "$CLUSTER" >/dev/null
  echo "Created cluster."
fi

step "Resolve default VPC, subnets, and security group"
VPC_ID=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' --output text)
if [ -z "$VPC_ID" ] || [ "$VPC_ID" = "None" ]; then
  echo "No default VPC found in $REGION." >&2
  exit 1
fi
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[0:2].SubnetId' --output text | tr '\t' ',')
if [ -z "$SUBNET_IDS" ] || [ "$SUBNET_IDS" = "None" ]; then
  echo "No subnets found in default VPC $VPC_ID." >&2
  exit 1
fi
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=$SG_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "None")
if [ -z "$SG_ID" ] || [ "$SG_ID" = "None" ]; then
  SG_ID=$(aws ec2 create-security-group --group-name "$SG_NAME" \
    --description "research-matchmaker: inbound 8000" --vpc-id "$VPC_ID" \
    --query 'GroupId' --output text)
  echo "Created security group $SG_ID."
fi
if aws ec2 authorize-security-group-ingress --group-id "$SG_ID" \
  --protocol tcp --port 8000 --cidr 0.0.0.0/0 >/dev/null 2>&1; then
  echo "Opened inbound 8000."
else
  echo "Inbound 8000 rule already present."
fi
echo "VPC: $VPC_ID  Subnets: $SUBNET_IDS  SG: $SG_ID"

NETWORK_CONFIG="awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}"

step "Create or update Fargate service '$SERVICE' (1 task, public IP)"
create_service() {
  aws ecs create-service --cluster "$CLUSTER" --service-name "$SERVICE" \
    --task-definition "$TASK_DEF_ARN" --desired-count 1 --launch-type FARGATE \
    --network-configuration "$NETWORK_CONFIG" >/dev/null
}
SERVICE_STATUS=$(aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" \
  --query 'services[0].status' --output text 2>/dev/null || echo "NONE")
if [ "$SERVICE_STATUS" = "ACTIVE" ]; then
  aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" \
    --task-definition "$TASK_DEF_ARN" --desired-count 1 \
    --force-new-deployment >/dev/null
  echo "Updated existing service with the new task definition."
else
  if CREATE_ERR=$(create_service 2>&1); then
    echo "Created service."
  elif echo "$CREATE_ERR" | grep -qiE "service.?linked role"; then
    # Documented transient lab error: the ECS service-linked role may not
    # exist yet the first time ECS is used in a fresh account.
    echo "Transient service-linked-role error; retrying once in 20s..."
    sleep 20
    create_service
    echo "Created service on retry."
  else
    echo "$CREATE_ERR" >&2
    exit 1
  fi
fi

step "Wait for the service to stabilize (task RUNNING)"
aws ecs wait services-stable --cluster "$CLUSTER" --services "$SERVICE"
echo "Service is stable."

step "Fetch the task's public IP"
TASK_ARN=$(aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" \
  --query 'taskArns[0]' --output text)
ENI_ID=$(aws ecs describe-tasks --cluster "$CLUSTER" --tasks "$TASK_ARN" \
  --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value | [0]" \
  --output text)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids "$ENI_ID" \
  --query 'NetworkInterfaces[0].Association.PublicIp' --output text)

printf '\n================================================================\n'
echo "Deployed. Task is RUNNING at public IP: $PUBLIC_IP"
echo
echo "Health check:"
echo "  curl http://$PUBLIC_IP:8000/health"
echo
echo "Try a match:"
echo "  curl -X POST http://$PUBLIC_IP:8000/match -H 'Content-Type: application/json' -d '{\"question\": \"who works on machine learning systems?\"}'"
printf '================================================================\n'
echo "REMINDER: capture evidence (docs/evidence/README.md), then run"
echo "  bash deploy/teardown.sh"
echo "in this same sitting. A forgotten service burns the lab budget."
