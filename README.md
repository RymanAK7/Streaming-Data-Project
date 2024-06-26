# Streaming Data Project

## Overview
This project implements an application to retrieve articles from the Guardian API based on a search term and an optional `from_date` field, process them, and post details of up to ten hits to the message broker, the AWS Kinesis stream where the data will have a retention period of 3 days. The application is built using Python, AWS services, Terraform for infrastructure management, and a Makefile for automation.

## Components
- **AWS Secrets Manager**: Used to securely store the Guardian API key.
- **AWS API Gateway**: Provides a RESTful interface for invoking the Lambda function.
- **AWS Lambda**: Implements the main functionality of the application.
- **AWS CloudWatch**: Used for logging and monitoring Lambda function execution.
- **Terraform**: Used for infrastructure provisioning and management.
- **Makefile**: Provides automation for common tasks such as environment setup and running tests.

## Functionality
The Lambda function consists of four main components:
1. **retrieve_api_key.py**: Retrieves the Guardian API key from AWS Secrets Manager.
2. **fetch_article_content.py**: Retrieves a preview of the article content, up to 1000 characters.
3. **retrieve_articles.py**: Queries the Guardian API based on search terms and optional date to retrieve the 10 most relevant articles.
4. **publish_to_kinesis.py**: Publishes the article information to an AWS Kinesis stream in the following format:
    ```json
    {
        "webPublicationDate": "2024-03-31T12:39:41Z",
        "webTitle": "Title",
        "webUrl": "https://www.theguardian.com/info",
        "contentPreview": "Content preview up to 1000 characters..."
    }
    ```

## Deployment
- **Terraform**: Automates the provisioning of AWS resources such as API Gateway, Lambda function, Kinesis stream creation and associated configurations.
- **AWS Secrets Manager**: Stores the Guardian API key securely.
- **AWS API Gateway**: Provides a public-facing endpoint for invoking the Lambda function.
- **AWS Kinesis**: Receives and stores the published article information for further processing by downstream applications.
- **AWS CloudWatch**: Captures logs from the Lambda function for monitoring and debugging purposes.

## Usage
To set up and use the project, follow these steps:

1. **Clone the project repository:**
    ```bash
    git clone https://github.com/RymanAK7/Streaming-Data-Project.git
    cd streaming-data-project
    ```

2. **Create Environment, Install requirements, and Run tests:**
    ```bash
    make all
    ```

3. **Install dependencies and create a deployment package:**
    ```bash
    pip install --target ./infrastructure/package -r requirements.txt
    cd infrastructure/package
    zip -r ../my-deployment-package.zip .
    cd ..
    zip -r my-deployment-package.zip ../src  
    ```

4. **Ensure your AWS credentials are configured:**
    Make sure you have your AWS credentials set up in your .aws folder (typically `~/.aws/credentials` and `~/.aws/config`). If these are properly configured, Terraform and AWS CLI will use them automatically. Alternatively, you can export your AWS environment variables:
    ```bash
    export AWS_ACCESS_KEY_ID=put_your_key_here
    export AWS_SECRET_ACCESS_KEY=put_your_secret_here
    ```

5. **Create Secret in AWS Secrets Manager:**
    - **Using AWS Management Console:**
        - Navigate to the AWS Management Console and open the Secrets Manager service.
        - Click on the "Store a new secret" button.
        - Choose "Other type of secrets" and then "Plaintext" as the secret type.
        - Enter `guardian/api-key` as the name for the secret.
        - Input the Guardian API key in the secret value field.
        - Review the configuration and click "Next".
        - Review again and click "Store".
    
    - **Using AWS Command Line Interface (CLI):**
        - Run the following command, replacing `<your-api-key>` with your Guardian API key:
            ```bash
            aws secretsmanager create-secret --name guardian/api-key --secret-string <your-api-key>
            ```
        - This command creates a secret named `guardian/api-key` with the specified Guardian API key.

6. **Initialize Terraform:**
    Make sure you're inside the `infrastructure` folder.
    ```bash
    cd infrastructure
    terraform init
    ```

7. **Populate the AccountId and Kinesis Stream Name:**
    In the terraform.tfvars file, provide your AWS Account ID and specify the desired name for the Kinesis stream where article information will be published. You can find your Account ID by navigating to the top right corner of the AWS Management Console. Ensure the Kinesis stream name aligns with your project's naming conventions and requirements. This stream will be created by Terraform during deployment.

8. **Plan Terraform:**
    ```bash
    terraform plan
    ```

9. **Apply Terraform:**
    ```bash
    terraform apply
    ```
    Upon running the `terraform apply` command, Terraform will prompt you with the actions it intends to perform. Only 'yes' will be accepted to approve. Enter 'yes' to proceed with the deployment.

10. **Invoke the API:**
    Go to the URL output by Terraform. The default query is:
    ```
    ?search_term=Python&kinesis_stream=test_stream&from_date=2024-01-01
    ```
    You can change the `search_term`, `kinesis_stream`, and `from_date` parameters as needed.

    You can also use query operators in the search term. For example:
    ```
    search_term=Football AND Chelsea
    ```
    This query will give you articles about Chelsea Football Club.

    The `search_term` parameter supports AND, OR, and NOT operators. For example:

    - `debate AND economy`: Returns only content that contains both "debate" and "economy".
    - `debate AND NOT immigration`: Returns only content that contains "debate" but does not contain "immigration".
     
    The AND operator has a higher precedence than OR, but you can use parentheses to override this behavior. For example:

    - `debate AND (economy OR immigration OR education)`: Returns only content that contains both "debate" and at least one of the following: "economy", "immigration", "education".

    Note that OR is the default operator, so you can omit it if you like. `debate AND (economy immigration education)` will behave the same as the above query.

11. **Check the API response:**
    The response from the API Gateway will show the article information that was added to the Kinesis stream.

12. **Monitor logs:**
    You can monitor the execution logs of the Lambda function in AWS CloudWatch to ensure the function is running correctly and to debug any issues.

13. **Clean up resources:**
    ```bash
    terraform destroy
    ```
    