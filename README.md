# FEI Grades Monitor Lambda

This project is an AWS Lambda function that periodically (via EventBridge) scrapes grades from the University Center of FEI portal, stores the data in a DynamoDB database, and sends email notifications if there are any grade changes.

## Project Structure

```
fei-grades-monitor-lambda
├── src
│   ├── lambda_function.py      # AWS Lambda entry point
│   ├── scraper.py              # InterageScraper class for web scraping
│   ├── db.py                   # Manages database interactions
│   └── notifier.py             # Manages email notifications
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
└── README.md                   # Project documentation
```

## Setup and Deployment

### 1. Prerequisites
- Python 3.9
- AWS account (Free Tier)

### 2. Installing Dependencies

Install the dependencies:

```bash
pip3 install -r requirements.txt
```

### 3. AWS Resource Configuration

You will need to configure AWS Lambda, AWS DynamoDB, and AWS CloudWatch resources.

#### 3.1 AWS Lambda

1. Create a Lambda Function with a **30s timeout** (Configuration > General configuration > Timeout).
2. Zip the files in the `fei-grades-monitor-lambda/src` directory and upload them to the Code Source.
3. Set the environment variables (Configuration > Environment Variables):

```bash
PORTAL_USERNAME=fei_portal_username
PORTAL_PASSWORD=fei_portal_password
GRADES_TABLE=dynamo_table_name
EMAIL_SENDER=your_email@example.com
EMAIL_RECEIVER=recipient_email@example.com
EMAIL_PASSWORD=your_email_password
```

> **Tip:** For Gmail, use an [app password](https://myaccount.google.com/apppasswords).

4. Run the following command to zip the project dependencies:

```bash
pip3 install -r requirements.txt -t ./python && zip -r python.zip python && rm -rf python
```

5. Create a Lambda Layer with the zipped file and attach it to the Function.

6. In the Function, go to `Configuration > Permissions`, click the created IAM role, and add read and write permissions for DynamoDB tables.

#### 3.2 AWS DynamoDB

7. Create a table with the Partition Key as `nome` (String).

> **Note:** The table name must match the value of the `GRADES_TABLE` environment variable.

#### 3.3 AWS EventBridge

8. Create a recurring Schedule in the GMT-3 timezone with the CRON expression `10 7 ? * * *`. This will schedule the lambda to run at 07:10 - Grades usually take a few minutes to be processed on the portal.
9. Validate the days and times the event will trigger. Disable the flexible time window. It is recommended to set an _end date and time_. Set the created Lambda as the target. It is recommended to disable the retry policy.
10. Create a role with the necessary permissions to invoke the Lambda.

12. Repeat steps 8 and 9 to schedule the remaining grade update times:
- 09h: `10 9 ? * * *`
- 11h: `10 11 ? * * *`
- 13h: `10 13 ? * * *`
- 15h: `10 15 ? * * *`
- 17h: `10 17 ? * * *`
- 19h: `10 19 ? * * *`
- 21h: `10 21 ? * * *`
- 23h: `10 23 ? * * *`

Yes, this process is tedious. I created a script in `scripts/build_scheduler.sh` to speed up the process. Just install and configure the AWS CLI, fill in the Lambda ARN and IAM Role, and run it.

## Notes
- Scraping depends on the structure of the FEI portal web page, which may change.
