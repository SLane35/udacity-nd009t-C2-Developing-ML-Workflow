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