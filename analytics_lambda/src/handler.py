import pandas as pd
import requests
import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


S3_BUCKET_NAME = os.getenv('BUCKET_ARN')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    arn_parts = S3_BUCKET_NAME.split(':')[-1]
    bucket_resource = s3.Bucket(arn_parts)

    url='https://datausa.io/api/data?drilldowns=Nation&measures=Population'

    response=requests.get(url)
    resp = response.json()

    df = pd.read_json(json.dumps(resp['data']))
    df['Year'].astype(int)

    print("Mean",df.loc[((df['Year']>=2013) & (df['Year']<=2018)), 'Population'].mean())
    print("Standard deviation",df.loc[((df['Year']>=2013) & (df['Year']<=2018)), 'Population'].std())
    logger.info("Mean results", df.loc[((df['Year']>=2013) & (df['Year']<=2018)), 'Population'].mean())
    logger.info("Standard Deviation", df.loc[((df['Year']>=2013) & (df['Year']<=2018)), 'Population'].std())
    print(df)
    response = requests.get(f'https://{bucket_resource}.s3.amazonaws.com/bls_data/pr.data.0.Current', verify=False)
    from io import StringIO
    data = StringIO(response.text)

    series = pd.read_csv(data, delimiter="\t")
    series.rename(columns={"series_id        ":"series_id","       value":'value'},inplace=True)
    temp_series=series

    series = series.groupby(["series_id", "year"], as_index=False)["value"].agg("sum")
    series.sort_values(by='value',ascending=False,inplace=True)
    series.drop_duplicates(subset=['series_id'],inplace=True)
    series.sort_values(by='series_id',inplace=True)

    print("Series", series)
    logger.info("Series", series)
    temp_series = temp_series.loc[temp_series["series_id"].str.contains("PRS30006032", case=False)]
    temp_series = temp_series[temp_series["period"].str.contains("Q01", case=False)]

    population_temp=df["Population"].astype(int)
    df["Year"] = df["Year"].astype(int)

    result = pd.merge(temp_series, df, left_on="year", right_on="Year", how="left")
    result[["series_id", "year", "period", "value", "Population"]]

    print(result)
    logger.info("results", result)
