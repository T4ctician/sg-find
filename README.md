# sg-find
SG-Find is a serverless solution for registering and locating missing family members using AWS services. This project demonstrates core AWS knowledge—building a complete serverless pipeline with Amazon API Gateway, AWS Lambda,Amazon Rekognition, Amazon Simple Email Service, Amazon Simple Queue Service, Amazon DynamoDB and Amazon S3.

# Table of Contents
[Overview](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#overview)

[Architecture](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#architecture)

[Features](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#features)

[Demo](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#demo)

[Getting Started](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#getting-started)

[Prerequisites](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#prerequisites)

[Setup & Deployment](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#setup--deployment)

[Usage](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#usage)

[Testing](https://github.com/T4ctician/sg-find/tree/main?tab=readme-ov-file#testing)

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
# Features

# Demo
# Getting Started
# Prerequisites
# Setup & Deployment
# Usage
# Testing
# Limitations & Future Improvements
# License
Licensed under the MIT License. Feel free to use, modify, and distribute this project.

If you have questions or suggestions, open an issue or PM!
