# Deployment Evidence Checklist

Capture all of this **while the service is running** — after teardown there
is nothing left to screenshot. Save files in this directory with the exact
names below so the narrative can reference them.

- [ ] **(a) `01-deploy-transcript.txt`** — the full `deploy.sh` terminal
      transcript, from credential verification through the printed public
      IP.
- [ ] **(b) `02-ecs-task-running.png`** — ECS console screenshot showing
      the `matchmaker-service` task in **RUNNING** state (cluster
      `matchmaker-cluster`, task detail or service task list visible).
- [ ] **(c) `03-ecr-image.png`** (or `03-ecr-image.txt`) — ECR console
      screenshot of the `research-matchmaker` repo showing the pushed image
      and tag, or a transcript of
      `aws ecr describe-images --repository-name research-matchmaker`.
- [ ] **(d) `04-match-curl.txt`** — transcript of
      `curl -X POST http://<public-ip>:8000/match ...` against the task's
      public IP returning a contract-shaped `RankedAnswer`
      (see `docs/contracts.md`).
- [ ] **(e) `05-empty-question-curl.txt`** — transcript of the same
      endpoint called with `{"question": ""}` returning
      `400 {"error": "empty_question", ...}` — proves the error contract
      remotely, not just locally.
- [ ] **(f) `06-size-and-resources.txt`** — the image size (`docker image
      ls research-matchmaker`) and the task's CPU/memory settings (from
      `deploy/task-definition.json` or the console task definition view).
- [ ] **(g) `07-teardown-transcript.txt`** — the full `teardown.sh`
      transcript showing the service and cluster deleted and no tasks
      remaining: proof the loop was closed and nothing was left billing.
