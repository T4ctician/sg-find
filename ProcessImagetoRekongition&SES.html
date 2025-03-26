import json
import boto3
import urllib.parse
import logging
from botocore.exceptions import ClientError
import os
from datetime import datetime
from decimal import Decimal
import mimetypes
from email.message import EmailMessage

# Initialize AWS clients
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses', region_name='us-east-1')  # Replace with your SES region

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "Pets")
REKOGNITION_COLLECTION_ID = os.environ.get("REKOGNITION_COLLECTION_ID", "HumanFacesCollection")
SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", 80.0))  # Adjust as needed
SES_SENDER_EMAIL = os.environ.get("SES_SENDER_EMAIL", "kennytwk.api+petnotification@gmail.com")  # Verified SES email

def parse_s3_url(s3_url):
    """
    Parse the S3 URL to extract the bucket name and object key.
    """
    try:
        parsed_url = urllib.parse.urlparse(s3_url)
        bucket = parsed_url.netloc.split('.')[0]
        key = urllib.parse.unquote(parsed_url.path.lstrip('/'))
        logger.info(f"Parsed S3 URL. Bucket: {bucket}, Key: {key}")
        return bucket, key
    except Exception as e:
        logger.error(f"Error parsing S3 URL {s3_url}: {str(e)}")
        return None, None

def get_image_from_s3(bucket, key):
    """
    Retrieve the image bytes from the specified S3 bucket and key.
    """
    try:
        logger.info(f"Retrieving image from S3. Bucket: {bucket}, Key: {key}")
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except ClientError as e:
        logger.error(f"S3 ClientError: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving image from S3: {str(e)}")
        return None

def compare_faces(image_bytes, collection_id, similarity_threshold):
    """
    Use Rekognition to compare faces in the image against the specified collection.
    Returns a list of matches with similarity and pet_id.
    """
    try:
        logger.info(f"Comparing faces against collection: {collection_id} with threshold: {similarity_threshold}")
        response = rekognition.search_faces_by_image(
            CollectionId=collection_id,
            Image={'Bytes': image_bytes},
            FaceMatchThreshold=similarity_threshold,
            MaxFaces=5  # Adjust based on your needs
        )
        face_matches = response.get('FaceMatches', [])
        matches = []
        for match in face_matches:
            similarity = match['Similarity']
            external_image_id = match['Face'].get('ExternalImageId')  # Retrieve pet_id
            if external_image_id:
                matches.append({
                    'Similarity': Decimal(str(similarity)),  # Convert float to Decimal
                    'pet_id': external_image_id  # Include pet_id for owner retrieval
                })
            else:
                logger.warning("Match found without ExternalImageId.")
        logger.info(f"Found {len(matches)} matching face(s).")
        return matches
    except ClientError as e:
        logger.error(f"Rekognition ClientError (CompareFaces): {e.response['Error']['Message']}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in CompareFaces: {str(e)}")
        return []

def index_faces(bucket, key, collection_id, pet_id):
    """
    Index a new face into the Rekognition collection.
    """
    try:
        logger.info(f"Indexing face from S3. Bucket: {bucket}, Key: {key}")
        response = rekognition.index_faces(
            CollectionId=collection_id,
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            ExternalImageId=pet_id,  # Use registered pet_id
            DetectionAttributes=['ALL']
        )
        face_records = response.get('FaceRecords', [])
        if face_records:
            logger.info(f"Indexed {len(face_records)} face(s) for image {key}.")
            return True
        else:
            logger.warning(f"No faces indexed for image {key}.")
            return False
    except ClientError as e:
        logger.error(f"Rekognition ClientError (IndexFaces): {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in IndexFaces: {str(e)}")
        return False

def update_dynamodb(owner_id, pet_id, matches):
    """
    Update the DynamoDB table with the latest face matches and timestamp.
    """
    try:
        logger.info("Updating DynamoDB.")
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        response = table.update_item(
            Key={
                'owner_id': owner_id,
                'pet_id': pet_id
            },
            UpdateExpression="SET face_matches = :matches, updated_at = :updated_at",
            ExpressionAttributeValues={
                ':matches': matches,  # Ensure matches contain Decimal types
                ':updated_at': datetime.utcnow().isoformat()
            }
        )
        logger.info(f"DynamoDB update response: {response}")
    except ClientError as e:
        logger.error(f"DynamoDB ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        logger.error(f"Unexpected error updating DynamoDB: {str(e)}")

def send_email(recipient, owner_name, subject, body, attachment_bytes, attachment_filename):
    """
    Send an email via SES with the specified parameters and attachment.
    """
    try:
        # Create a multipart email message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SES_SENDER_EMAIL
        msg['To'] = recipient
        msg.set_content(body)

        # Determine the MIME type of the attachment
        mime_type, _ = mimetypes.guess_type(attachment_filename)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        maintype, subtype = mime_type.split('/', 1)

        # Add the attachment to the email
        msg.add_attachment(attachment_bytes, maintype=maintype, subtype=subtype, filename=attachment_filename)

        # Convert the EmailMessage to raw bytes
        raw_message = msg.as_bytes()

        # Send the email via SES
        response = ses.send_raw_email(
            Source=SES_SENDER_EMAIL,
            Destinations=[recipient],
            RawMessage={'Data': raw_message}
        )
        logger.info(f"Email sent to {recipient}. Message ID: {response['MessageId']}")
    except ClientError as e:
        logger.error(f"SES ClientError: {e.response['Error']['Message']}")
    except Exception as e:
        logger.error(f"Unexpected error sending email via SES: {str(e)}")

def get_owner_details(owner_id, pet_id):
    """
    Retrieve the owner's contact email and name from the Pets table based on owner_id and pet_id.
    For unregistered users (owner_id='unregistered'), use pet_id to find the registered owner.
    """
    try:
        pets_table = dynamodb.Table(DYNAMODB_TABLE_NAME)  # Should be 'Pets'
        
        if owner_id != "unregistered":
            # Registered user report
            response = pets_table.get_item(
                Key={
                    'owner_id': owner_id,
                    'pet_id': pet_id
                }
            )
        else:
            # Unregistered user report - find registered owner via pet_id using GSI
            response = pets_table.query(
                IndexName='pet_id-index',  # Ensure this matches your GSI name
                KeyConditionExpression=boto3.dynamodb.conditions.Key('pet_id').eq(pet_id)
            )
        
        if 'Item' in response:
            item = response['Item']
            owner_contact = item.get('owner_contact')
            owner_name = item.get('owner_name')
            if owner_contact and owner_name:
                logger.info(f"Retrieved owner_contact: {owner_contact} and owner_name: {owner_name} for owner_id: {owner_id}, pet_id: {pet_id}.")
                return {
                    'email': owner_contact,
                    'name': owner_name
                }
            else:
                logger.error(f"Missing owner_contact or owner_name for owner_id: {owner_id}, pet_id: {pet_id}")
                return None
        elif 'Items' in response and response['Items']:
            # Handling query response for unregistered user
            item = response['Items'][0]  # Assuming pet_id is unique
            owner_contact = item.get('owner_contact')
            owner_name = item.get('owner_name')
            if owner_contact and owner_name:
                logger.info(f"Retrieved owner_contact: {owner_contact} and owner_name: {owner_name} for pet_id: {pet_id}.")
                return {
                    'email': owner_contact,
                    'name': owner_name
                }
            else:
                logger.error(f"Missing owner_contact or owner_name for pet_id: {pet_id}")
                return None
        else:
            logger.error(f"No item found for owner_id: {owner_id}, pet_id: {pet_id}")
            return None
    except ClientError as e:
        logger.error(f"DynamoDB ClientError while retrieving owner details: {e.response['Error']['Message']}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving owner details: {str(e)}")
        return None

def lambda_handler(event, context):
    """
    The main Lambda handler function that processes incoming messages.
    """
    logger.info("Lambda function started processing.")
    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            logger.info(f"Processing message: {message_body}")
            owner_id = message_body.get('owner_id')
            pet_id = message_body.get('pet_id')
            image_url = message_body.get('image_url')
            purpose = message_body.get('purpose')
            pet_name = message_body.get('pet_name')

            # Validate required fields
            if not all([image_url, purpose]):
                logger.error("Missing required message fields. Skipping message.")
                continue  # Skip unprocessable messages

            # Parse S3 bucket and key
            bucket, key = parse_s3_url(image_url)
            if not bucket or not key:
                logger.error("Invalid S3 URL. Skipping message.")
                continue  # Skip unprocessable messages

            # Retrieve image from S3
            image_bytes = get_image_from_s3(bucket, key)
            if not image_bytes:
                logger.error("Failed to retrieve image from S3. Skipping message.")
                continue  # Skip unprocessable messages

            # Compare faces
            matches = compare_faces(image_bytes, REKOGNITION_COLLECTION_ID, SIMILARITY_THRESHOLD)

            if owner_id != "unregistered":
                # **Registered User Report**
                if not matches:
                    # **No Match Found:** Index the new face
                    logger.info("No matching faces found. Indexing the new face.")
                    indexing_success = index_faces(bucket, key, REKOGNITION_COLLECTION_ID, pet_id)
                    if indexing_success:
                        logger.info("Successfully indexed the new face.")
                        # **Notify Owner About Indexing**
                        owner_details = get_owner_details(owner_id, pet_id)
                        if owner_details:
                            send_email(
                                recipient=owner_details['email'],
                                owner_name=owner_details['name'],
                                subject="Pet Processing Update: New Face Indexed",
                                body=f"Dear {owner_details['name']},\n\nYour pet '{pet_name}' has been successfully processed. A new face has been indexed for future recognition.\n\nBest Regards,\nPetDetectives Team",
                                attachment_bytes=image_bytes,
                                attachment_filename=key.split('/')[-1]  # Extract filename from key
                            )
                    else:
                        logger.error("Failed to index the new face.")
                        # **Notify Owner About Error**
                        owner_details = get_owner_details(owner_id, pet_id)
                        if owner_details:
                            send_email(
                                recipient=owner_details['email'],
                                owner_name=owner_details['name'],
                                subject="Pet Processing Error: Face Indexing Failed",
                                body=f"Dear {owner_details['name']},\n\nThere was an error indexing your pet '{pet_name}'s face for future recognition.\n\nPlease try processing the image again.\n\nBest Regards,\nPetDetectives Team",
                                attachment_bytes=image_bytes,
                                attachment_filename=key.split('/')[-1]
                            )
                else:
                    # **Match Found:** Notify the owner
                    logger.info(f"Found {len(matches)} matching face(s). No indexing needed.")
                    for match in matches:
                        matched_pet_id = match.get('pet_id')
                        similarity = match.get('Similarity')
                        if not matched_pet_id:
                            logger.error("Matched pet_id is missing. Skipping this match.")
                            continue
                        owner_details = get_owner_details("unregistered", matched_pet_id)
                        if owner_details:
                            send_email(
                                recipient=owner_details['email'],
                                owner_name=owner_details['name'],
                                subject="Pet Processing Update: Pet Found",
                                body=f"Dear {owner_details['name']},\n\nGreat news! Your pet '{pet_name}' has been found with a confidence level of {similarity:.2f}%.\n\nBest Regards,\nPetDetectives Team",
                                attachment_bytes=image_bytes,
                                attachment_filename=key.split('/')[-1]
                            )
                        else:
                            logger.error(f"Could not retrieve owner details for matched_pet_id: {matched_pet_id}")
            else:
                # **Unregistered User Report**
                if matches:
                    # **Match Found:** Notify the registered owner
                    logger.info(f"Found {len(matches)} matching face(s). Notifying registered owners.")
                    for match in matches:
                        matched_pet_id = match.get('pet_id')
                        similarity = match.get('Similarity')
                        if not matched_pet_id:
                            logger.error("Matched pet_id is missing. Skipping this match.")
                            continue
                        owner_details = get_owner_details("unregistered", matched_pet_id)
                        if owner_details:
                            send_email(
                                recipient=owner_details['email'],
                                owner_name=owner_details['name'],
                                subject="Pet Processing Update: Pet Found",
                                body=f"Dear {owner_details['name']},\n\nA pet matching your missing pet '{pet_name}' has been found with a confidence level of {similarity:.2f}%.\n\nBest Regards,\nPetDetectives Team",
                                attachment_bytes=image_bytes,
                                attachment_filename=key.split('/')[-1]
                            )
                        else:
                            logger.error(f"Could not retrieve owner details for matched_pet_id: {matched_pet_id}")
                else:
                    # **No Match Found:** Do not index unregistered reports
                    logger.info("No matching faces found. No indexing for unregistered user report.")
                    # Optionally, notify admin or take other actions

            # **Update DynamoDB Regardless of Owner Type**
            update_dynamodb(owner_id, pet_id, matches)
            logger.info("Successfully processed and updated DynamoDB.")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            # Optionally, implement additional error handling or retry mechanisms
