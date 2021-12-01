import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']

    print(key)
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, '/tmp/image.png')

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


import json
import base64
import os
import io
import boto3
import csv

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2021-11-29-18-16-35-165'
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    print("Received event: " + json.dumps(event, indent=2))
    
    data = json.loads(json.dumps(event))
    payload = base64.b64decode(data['image_data'])

    print(payload)

    # Make a prediction:
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT,
                                       ContentType='image/png',
                                       Body=payload)
    
        
    print(response)
    result = json.loads(response['Body'].read().decode('utf-8'))
    
    #pred = int(result['predictions'][0]['score'])
    #predicted_label = 'M' if pred == 1 else 'B'
    
    #inferences = predictor.predict(payload)

    # We return the data back to the Step Function    
    event["inferences"] = result
    
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

import json
import ast


THRESHOLD = .93


def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event["inferences"]

    print(inferences)
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any (i >= THRESHOLD for i in inferences)

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }