import boto3
import requests
from bs4 import BeautifulSoup

FOLDER_NAME = 'bls_data'
S3_BUCKET_NAME = 'mysources3bucket-rzox97pp'
DATA_SOURCE = "https://download.bls.gov/pub/time.series/pr/"
HEADERS = {
    'User-Agent': '+19206268696',
    'Referer': 'xyz@gmail.com'
}

def get_deleted_list(bucket_resource):
    
    collections = bucket_resource.objects.all()
    objectList = []
    for collect in collections:
        objectList.append(collect.key)
    return objectList

def call_api(objectList, removed_list, bucket_resource):
    response = requests.get(DATA_SOURCE, headers=HEADERS)
    scrap = BeautifulSoup(response.text, 'html.parser')

    for path in scrap.find_all("a"):
        file_name = path.get_text()
        s3_object_key = f"{FOLDER_NAME}/{file_name}"
        if file_name == "[To Parent Directory]":
            continue

        received_file = requests.get(DATA_SOURCE + file_name, headers=HEADERS)
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
    

def main():
    s3 = boto3.resource('s3')
    bucket_resource = s3.Bucket(S3_BUCKET_NAME)

    objectList = get_deleted_list(bucket_resource)
    removed_list = objectList.copy()
    call_api(objectList, removed_list, bucket_resource)


if __name__ == "__main__":
    main()
