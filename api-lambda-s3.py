import json
import boto3
import uuid
from datetime import datetime
import logging
import os
import base64
from boto3.dynamodb.conditions import Attr  # Import Attr for scan filters

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
s3 = boto3.client("s3")
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

# Configuration: Environment Variables
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "api-gateway-uploaded-image")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "Pets")
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/640168445668/PetProcessingQueue")  # Replace with your SQS queue URL

def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        # Determine HTTP method
        http_method = event.get("httpMethod", "").upper()
        
        if http_method == "POST":
            return handle_post(event)
        elif http_method == "PUT":
            return handle_put(event)
        else:
            return response(405, {"error": "Method Not Allowed"})
        
    except Exception as e:
        logger.error("Error processing request: %s", str(e), exc_info=True)
        return response(500, {"error": "Internal Server Error", "message": str(e)})

def handle_put(event):
    try:
        logger.info("handle_put invoked.")
        logger.info("Event Data: %s", json.dumps(event))
        
        # Extract the binary data
        body = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
        if not is_base64:
            raise ValueError("Expected 'isBase64Encoded' to be true for binary data.")
        image_data = base64.b64decode(body)
        
        # Extract user-id and petname from query parameters
        query_params = event.get("queryStringParameters") or {}
        user_id = query_params.get("user_id")
        pet_name = query_params.get("pet_name")
        
        logger.info(f"User ID: {user_id}, Pet Name: {pet_name}")

        if not user_id or not pet_name:
            raise ValueError("Missing 'user_id' or 'pet_name' in query parameters.")
        
        # For unregistered users, set pet_name to 'unknown' if not provided
        if user_id.lower() == "unregistered":
            if not pet_name:
                pet_name = "unknown"
                logger.info("Set pet_name to 'unknown' for unregistered user.")
        else:
            if not pet_name:
                raise ValueError("Missing 'pet_name' in query parameters for registered user.")

        # Generate filename as user-id-petname with proper sanitization
        sanitized_pet_name = ''.join(e for e in pet_name if e.isalnum() or e in ('-', '_')).replace(' ', '_')

        filename = f"{user_id}-{sanitized_pet_name}"

        # Generate a unique suffix if the user is unregistered to ensure unique filenames
        if user_id.lower() == "unregistered":
            unique_suffix = str(uuid.uuid4())
            filename += f"-{unique_suffix}"
            logger.info("Appended UUID to filename for unregistered user: %s", unique_suffix)
        
        # Add file extension based on headers
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        if content_type:
            extension = content_type.split('/')[-1]
            if extension in ['jpeg', 'jpg', 'png', 'gif', 'bmp']:
                filename += f".{extension}"
            else:
                filename += ".jpg"  # Default extension
        else:
            filename += ".jpg"  # Default extension
        
        logger.info(f"Final filename: {filename}")

        # Upload to S3 without ACL
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=filename,
            Body=image_data,
            ContentType=content_type if content_type else 'image/jpeg'
            # Removed ACL parameter
        )
        
        # Construct the S3 URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{filename}"
        
        logger.info("Image uploaded successfully: %s", s3_url)
        
        return response(200, {"message": "Image uploaded successfully", "file_url": s3_url})
    
    except Exception as e:
        logger.error("Error uploading image: %s", str(e), exc_info=True)
        return response(500, {"error": "Failed to upload image", "message": str(e)})

def handle_post(event):
    try:
        logger.info("Processing POST request.")
        
        # Parse JSON body
        body = event.get("body", "")
        is_base64 = event.get("isBase64Encoded", False)
        if is_base64:
            body = base64.b64decode(body).decode('utf-8')
        try:
            data = json.loads(body)
            logger.info("Parsed JSON body successfully.")
        except json.JSONDecodeError as jde:
            raise ValueError("Invalid JSON format.") from jde
        
        # Extract required fields
        purpose = data.get("purpose")
        pet_name = data.get("pet_name")
        owner_id = data.get("owner_id", "unregistered")
        owner_name = data.get("owner_name", "")
        owner_contact = data.get("owner_contact", "")
        image_url = data.get("image_url")
        
        logger.info(f"Received data - Purpose: {purpose}, Pet Name: {pet_name}, Owner ID: {owner_id}")
        
        if not purpose:
            raise ValueError("Missing 'purpose' field.")
        if not pet_name:
            raise ValueError("Missing 'pet_name' field.")
        if not image_url:
            raise ValueError("Missing 'image_url' field.")
        
        # Initialize DynamoDB table
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Check for existing entry if owner is registered
        existing_item = None
        if owner_id != "unregistered":
            logger.info("Owner is registered. Attempting to find existing pet entry.")
            scan_response = table.scan(
                FilterExpression=Attr('owner_id').eq(owner_id) & Attr('pet_name').eq(pet_name)
            )
            items = scan_response.get("Items", [])
            if items:
                existing_item = items[0]
                logger.info("Existing pet entry found.")
            else:
                logger.info("No existing pet entry found.")
        
        # Generate or reuse pet_id
        pet_id = existing_item.get("pet_id") if existing_item else str(uuid.uuid4())
        if not pet_id:
            pet_id = str(uuid.uuid4())
            logger.info("Generated new pet_id.")
        else:
            logger.info(f"Reusing existing pet_id: {pet_id}")
        
        # Current timestamp
        updated_at = datetime.utcnow().isoformat()
        
        # Prepare item for DynamoDB
        item = {
            "owner_id": owner_id,
            "pet_id": pet_id,
            "owner_name": owner_name,
            "owner_contact": owner_contact,
            "pet_name": pet_name,
            "image_url": image_url,
            "updated_at": updated_at
        }
        
        # Add created_at only for new entries
        if not existing_item:
            item["created_at"] = updated_at
            logger.info("Adding 'created_at' to new DynamoDB item.")
        
        # Save or update the item in DynamoDB
        table.put_item(Item=item)
        logger.info("Metadata saved successfully in DynamoDB.")
        
        # Determine if a message should be sent to SQS
        send_sqs = False
        message_purpose = ""
        
        if (owner_id != "unregistered" and purpose == "report_missing_pet") or \
           (owner_id == "unregistered" and purpose == "report_found_pet"):
            send_sqs = True
            message_purpose = "process_pet_status"
            logger.info("Conditions met for sending message to SQS.")
        
        if send_sqs:
            # Prepare message
            message = {
                "owner_id": owner_id,
                "pet_id": pet_id,
                "pet_name": pet_name,
                "image_url": image_url,
                "purpose": message_purpose
            }
            
            # Send message to SQS
            sqs_response = sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message)
            )
            
            logger.info("Message sent to SQS with MessageId: %s", sqs_response.get("MessageId"))
            
            return response(200, {
                "message": "Metadata saved and message sent to SQS successfully",
                "dynamodb_data": item,
                "sqs_message_id": sqs_response.get("MessageId")
            })
        else:
            logger.info("No SQS message sent as conditions were not met.")
            return response(200, {
                "message": "Metadata saved successfully (No SQS message sent)",
                "dynamodb_data": item
            })
    
    except Exception as e:
        logger.error("Error saving metadata: %s", str(e), exc_info=True)
        return response(500, {"error": "Failed to save metadata", "message": str(e)})

def response(status_code, body):
    """
    Formats the HTTP response for API Gateway.
    """
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  # Adjust as needed for CORS
            "Access-Control-Allow-Methods": "OPTIONS,POST,PUT",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    }
