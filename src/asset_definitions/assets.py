# muninn_dagster/src/example/assets.py
import requests
from dagster import asset


@asset
def example_request_taxi_data():
  month_to_fetch = "2023-03"
  raw_trips = requests.get(
    f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
  )
  with open("data/example/raw/taxi.parquet", "wb") as output_file:
    output_file.write(raw_trips.content)


@asset
def example_request_taxi_zone_data():
  raw_zones = requests.get(
    "https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv"
  )
  with open("data/example/raw/taxi_zones.csv", "wb") as output_file:
    output_file.write(raw_zones.content)
