# sg-find
SG-Find is a serverless solution for registering and locating missing family members using AWS services. This project demonstrates core AWS knowledge—building a complete serverless pipeline with Amazon API Gateway, AWS Lambda, Amazon Rekognition, Amazon Simple Email Service, Amazon Simple Queue Service, Amazon DynamoDB and Amazon S3.

# Table of Contents
[Overview](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#overview)

[Architecture](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#architecture)

[Getting Started](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#getting-started)

[Usage](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#usage)

[Limitations & Future Improvements](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#limitations--future-improvements)

[License](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#license)

# Overview
SG-Find is designed to help users upload and track missing or found family members. It demonstrates:

- Static website hosted on Amazon S3 for a simple HTML/CSS/JavaScript frontend.

- API Gateway endpoints (PUT/POST) that communicate with AWS Lambda.

- DynamoDB for fast and scalable data storage.

- Integration with Amazon SQS or Amazon Rekognition for additional processing and face recognition.

This project primarily aims to showcase AWS knowledge in a small, production-like environment with minimal operational overhead.
# Architecture
![Architecture drawio](https://github.com/user-attachments/assets/9302fc5a-6eb7-4d61-9fd3-55ae6f4e8c20)

1. Amazon S3

  - Static Web Hosting: Serves the HTML, JavaScript, and CSS for the SG-Find front end.

  - Image Storage: Also stores uploaded family member images (uploaded via Lambda).

2. Amazon API Gateway

  - Single Entry Point: Provides public endpoints for clients.

  - Methods:

    - PUT /upload_image – Receives binary image data and passes it to Lambda for S3 upload.

    - POST /insertuser – Stores metadata about a family member in DynamoDB.

3. AWS Lambda (Python)

  - Core Backend Logic:

    - Handles image uploads from API Gateway, compresses (if needed), and writes them to S3.

    - Accepts metadata (owner_id, family_member_name, etc.) and writes it to DynamoDB.

4. Amazon DynamoDB

  - Metadata Storage: Saves attributes such as owner_id, family_member_name, purpose, image_url, timestamps, etc.

  - Key-Value / NoSQL: Enables high performance, scalable reads and writes for the serverless application.

5. Amazon SQS

  - Asynchronous Task Queue: Ensures at-least-once message delivery for operations that need background processing (e.g., triggering face recognition or sending notifications).

  - Decoupling: Keeps the system responsive by offloading longer-running tasks from the main request flow.

6. Amazon Rekognition

  - Face Recognition: If enabled, images can be sent to Rekognition to identify or match family member faces.

  - Integration: Typically triggered via SQS, allowing real-time or near-real-time face matching without blocking the user upload process.

7. Amazon SES

  - Email Notifications: Can send automated emails to owners when a missing family member is matched or found.

  - Integration: Invoked by Lambda (or via SQS), allowing for confirmations, status updates, or other custom alerts.

# Getting Started
- Prerequisites
  1. AWS Account
     - Ensure you have credentials with sufficient permissions for Amazon S3, AWS Lambda, API Gateway, Amazon DynamoDB, Amazon SQS, Amazon Rekognition and Amazon SES.
  2. Python
     - For writing or editing your Lambda functions.

- Setup & Deployment
  1. Clone or Download This Repository
     ```git
     git clone https://github.com/your-account/sg-find.git
     cd sg-find
     ```
  3. Create an S3 Bucket
    1. Enable Static Website Hosting on the bucket.
    2. Upload index.html to this bucket.
    3. Restrict public access / configure your bucket policy as needed.
  3. Configure API Gateway
    1. In API Gateway, create an API and define two resources/methods:
       - PUT: /upload_image (for image uploads)
       - POST: /insertuser (for storing metadata)
    2. Point each method to your AWS Lambda function.
    3. Enable CORS:
       - Restrict it to https://<your-s3-bucket>.s3.amazonaws.com (or your custom domain) if you want to limit usage.
    4. Create a DynamoDB Table
       1. For example, name it e.g. "missingfm".
       2. Use a primary key setup that suits your design (e.g., owner_id as the partition key and family_member_id as the sort key).
       3. Confirm your Lambda execution role has dynamodb:PutItem, dynamodb:GetItem.
    5. Deploy Your Lambda Code
       1. Ensure your Lambda has the correct environment variables (e.g., S3_BUCKET_NAME, DYNAMODB_TABLE_NAME, SQS_ARN).
       2. Give the Lambda execution role permissions to:
          - Write to S3 (s3:PutObject, s3:GetObject)
          - Write to DynamoDB (dynamodb:PutItem etc.)
          - Access SQS for asynchronous tasks (e.g., sqs:SendMessage, sqs:ReceiveMessage etc.)
          - Access SES to send personalized emails once a missing person is found (ses:SendEmail etc.)
          - Access Rekognition to detect and compare faces using deep learning (rekognition:IndexFaces, rekognition:SearchFaces etc.)
    6. Ensure Each Service Has Necessary IAM Permissions
       - S3 Bucket Policy or Lambda execution role must allow uploading, reading objects.
       - API Gateway resource policy, if used, should allow invocation by your account or certain IPs.
       - Lambda Execution Role must include policies that let the function interact with S3, DynamoDB, SQS etc. as needed.
    7. (Future Implementation) Use CloudFormation/Terraform
        - For an automated approach, define resources in a template and deploy them as a stack.

# Usage
1. Open the Web Page
   - Navigate to your S3 bucket’s static hosting URL, e.g.:
     ```html
     https://your-bucket.s3.amazonaws.com/index.html
     ```
2. Select Purpose
   - register_family_member, report_missing_family_member, or report_found_family_member.
3. Fill Out the Form
   - Provide necessary details (owner contact for certain purposes, family member name, etc.).
   - Select an image ≤ 7 MB.
4. Click “Upload and Save”
   - Javascript will compresses if images > 4 MB.
   - PUT request to upload the image to S3.
   - POST request to store metadata in DynamoDB.
5. The combined JSON from S3 + DynamoDB appears, indicating success or error.

# Demo
<img width="2850" height="1328" alt="Demo-static-website" src="https://github.com/user-attachments/assets/b54d5a6f-5a8c-4881-a352-bf64c466a8ad" />

# Limitations & Future Improvements
- 10 MB Payload Limit in API Gateway: big images may fail unless further compressed or using presigned URLs.
- Security: CORS policy helps, but for real DDoS protection, consider AWS WAF or AWS Shield.
# License
Licensed under the MIT License. Feel free to use, modify, and distribute this project.

If you have questions or suggestions, open an issue or PM!
