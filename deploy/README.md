# Deploying to the AWS Academy Learner Lab

This walks you through deploying the matchmaker to ECS Fargate in the
Learner Lab sandbox, assuming you have never done it before.

> **⚠️ Deploy, capture evidence, then run `teardown.sh` — all in the same
> sitting.** A forgotten running service burns the shared budget around the
> clock, and a blown budget doesn't just cost money: **the lab disables the
> entire account and deletes all our resources.** The budget display lags
> 8–12 hours behind real spend, so "the meter looks fine" proves nothing.
> Ending the lab session is only documented to stop EC2 instances — assume a
> running Fargate service keeps billing between sessions.

## What you need

- Docker running locally (or the repo's devcontainer, which has the AWS CLI
  preinstalled).
- The AWS CLI (`aws --version` to check) if you're not in the devcontainer.
- Access to the course's AWS Academy Learner Lab.

## Step 1 — Start the lab and get credentials

1. In AWS Academy, open the Learner Lab and click **Start Lab**. Wait for
   the circle next to "AWS" to turn green.
2. Click **AWS Details**, then **Show** next to "AWS CLI". You'll see a
   `[default]` block with three lines.
3. Paste that whole block into `~/.aws/credentials` (create the file if it
   doesn't exist), replacing any previous block:

   ```ini
   [default]
   aws_access_key_id = ASIA...
   aws_secret_access_key = ...
   aws_session_token = ...
   ```

   **All three lines are required** — the `aws_session_token` line is easy
   to miss and nothing works without it. These credentials are temporary:
   they die when the lab session ends, and every new session issues new
   ones, so this paste step happens every session.

## Step 2 — Deploy

From the repo root:

```bash
bash deploy/deploy.sh
```

The script echoes each step and stops loudly at the first failure. It:

1. Verifies credentials (`aws sts get-caller-identity`) — if this fails,
   redo Step 1.
2. Creates the ECR repo `research-matchmaker` if it doesn't exist.
3. Builds the image for `linux/amd64` and pushes it to ECR. **The first
   push uploads ~2.2 GB and takes several minutes** — later pushes only
   upload changed layers, so subsequent deploys are much faster.
4. Registers the Fargate task definition with **LabRole as both the task
   role and the execution role** (the lab forbids creating IAM roles; this
   is the lab's own documented ECS setup).
5. Creates the cluster `matchmaker-cluster` if needed, then creates or
   updates a 1-task Fargate service in the default VPC with a public IP
   and a security group allowing inbound port 8000.
6. Waits for the task to reach RUNNING, then prints the public IP and a
   ready-to-run `curl` for `POST /match`.

Everything runs under your pasted session credentials on purpose: ECR
access in the lab is asymmetric — LabRole can only *pull* images, while
your session user can *push*. The push must never run as LabRole.

## Step 3 — Capture evidence

While the service is up, work through the checklist in
[`docs/evidence/README.md`](../docs/evidence/README.md). Do it now — after
teardown there is nothing left to screenshot.

## Step 4 — Tear down (same sitting, always)

```bash
bash deploy/teardown.sh              # removes service + cluster
bash deploy/teardown.sh --delete-ecr # also removes the ECR repo/images
```

Keeping the ECR repo (default) is fine — stored images cost little and make
the next deploy's push fast. The running service is the thing that burns
budget.

## Resource sizing

The task runs at 0.5 vCPU / 1 GB (`deploy/task-definition.json`). **Do not
shrink memory below 1 GB**: the image contains PyTorch, and smaller tasks
get OOM-killed silently — the task just flaps between PENDING and STOPPED
with no useful error.

## Troubleshooting

**"Could not verify AWS credentials" / `ExpiredToken` / `InvalidClientTokenId`**
Your session token has expired (they die with the lab session, and mid-lab
timeouts happen too). Symptom: every `aws` call fails with an auth error,
even though it worked earlier. Fix: AWS Details → Show → repaste the whole
three-line block into `~/.aws/credentials`, rerun the script. Scripts are
idempotent; rerunning is safe.

**"The ECS service linked role could not be assumed"**
Documented transient lab error — the service-linked role may not exist yet
the first time ECS is used in a fresh account. `deploy.sh` already retries
once after 20 seconds. If it still fails, wait a minute and rerun the
script.

**Budget**
Check the budget shown at the top of the Learner Lab page every session,
and remember it lags 8–12 hours behind real spend — a service you forgot
yesterday may not show up in the number you're looking at now. The lab's
own guidance names ECS clusters among the fastest budget-burners. If the
budget is exceeded, the account is disabled and everything in it is
deleted. Teardown in the same sitting is the only reliable protection.

**Fargate misbehaving?**
There is no App Runner and no Bedrock in this lab (both absent from the
lab's service list), so there is nothing to fall back to among managed
runtimes. The fallback is plain EC2: launch an instance with the
`LabInstanceProfile` instance profile, install Docker, `docker pull` the
image from ECR (LabRole can pull), and `docker run -p 8000:8000` it — the
container is the unit of truth, so the same image runs unchanged.
