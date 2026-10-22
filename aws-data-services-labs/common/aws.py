"""Shared boto3 helpers. Set AWS_REGION (default ap-south-1) and optionally AWS_ENDPOINT_URL for local emulators."""
import os
import boto3

REGION = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "ap-south-1"))


def client(service: str):
    return boto3.client(service, region_name=REGION)


def resource(service: str):
    return boto3.resource(service, region_name=REGION)
