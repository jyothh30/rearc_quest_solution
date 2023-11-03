import boto3
import requests
from bs4 import BeautifulSoup
import os

FOLDER_NAME_BLS = 'bls_data'
FOLDER_NAME_POPULATION = 'api'
S3_BUCKET_NAME = os.getenv('BUCKET_ARN')
DATA_SOURCE_1 = "https://download.bls.gov/pub/time.series/pr/"
DATA_SOURCE_2 = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"

HEADERS = {
    'User-Agent': '+19206260',
    'Referer': 'xyz@gmail.com'
}

s3 = boto3.resource('s3')
arn_parts = S3_BUCKET_NAME.split(':')[-1]
bucket_resource = s3.Bucket(arn_parts)


def get_deleted_list(bucket_resource):
    
    collections = bucket_resource.objects.all()
    objectList = []
    for collect in collections:
        objectList.append(collect.key)
    return objectList

def call_api(objectList, removed_list, bucket_resource):
    response = requests.get(DATA_SOURCE_1, headers=HEADERS)
    scrap = BeautifulSoup(response.text, 'html.parser')

    for path in scrap.find_all("a"):
        file_name = path.get_text()
        s3_object_key = f"{FOLDER_NAME_BLS}/{file_name}"
        if file_name == "[To Parent Directory]":
            continue

        received_file = requests.get(DATA_SOURCE_1 + file_name, headers=HEADERS)
        print(received_file)
        if file_name not in objectList:
            bucket_resource.put_object(Key=s3_object_key, Body=received_file.content)
        elif file_name in objectList:
            s3_response = bucket_resource.Object(file_name).get()
            s3_file_content = s3_response['Body'].read()
            if received_file.content != s3_file_content:
                bucket_resource.put_object(Key=s3_object_key, Body=received_file.content)
            removed_list.remove(file_name)
    for file in removed_list:
        bucket_resource.Object(file).delete()
    

def part_1_data_source():
    objectList = get_deleted_list(bucket_resource)
    removed_list = objectList.copy()
    call_api(objectList, removed_list, bucket_resource)

def upload_data_to_s3(bucket_name, folder, file_name, data):
    s3_object_key = f"{folder}/{file_name}"
    bucket_name.put_object(Key=s3_object_key, Body=data)

def part_2_data_source():
    response = requests.get(DATA_SOURCE_2)
    data = response.text

    upload_data_to_s3(bucket_resource, FOLDER_NAME_POPULATION, "population.json", data)

def lambda_handler(event,context):
    
    
    part_1_data_source()
    part_2_data_source()
    
    response = {
        "statusCode": 200,
        "body": "Execution completed successfully",
        "message": "Data sources processed successfully",
    }

    return response
    
