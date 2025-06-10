TARGET_ARN="LAMBDA_ARN"
ROLE_ARN="ROLE_REQUIRED_FOR_SCHEDULER"

HOURS=(7 9 11 13 15 17 19 21 23)
END_DATE="2025-06-30T23:59:59Z" # Adjust the end date as needed

for HOUR in "${HOURS[@]}"; do
  SCHEDULE_NAME="monitoring-grades-${HOUR}h10"

  echo "Scheduling: $SCHEDULE_NAME"

  aws scheduler create-schedule \
    --name "$SCHEDULE_NAME" \
    --schedule-expression "cron(10 $HOUR ? * * *)" \
    --schedule-expression-timezone "America/Sao_Paulo" \
    --end-date "$END_DATE" \
    --flexible-time-window Mode=OFF \
    --target Arn="$TARGET_ARN",RoleArn="$ROLE_ARN",RetryPolicy={MaximumRetryAttempts=0} \
    --state ENABLED
done