import boto3
import requests

S3_BUCKET_NAME = "zombalifeiscool"
DATA_SOURCE = "https://datausa.io/api/data?drilldowns=Nation&measures=Population"
S3_FOLDER = "api"  

s3 = boto3.resource('s3')
bucket = s3.Bucket(S3_BUCKET_NAME)

def upload_data_to_s3(bucket_name, folder, file_name, data):
    s3_object_key = f"{folder}/{file_name}"
    bucket.put_object(Key=s3_object_key, Body=data)

def main():
    response = requests.get(DATA_SOURCE)
    data = response.text

    upload_data_to_s3(S3_BUCKET_NAME, S3_FOLDER, "population.json", data)

if __name__ == "__main__":
    main()



