import boto3

def create_s3_bucket(bucket_name, region='us-west-1'):
    s3 = boto3.client('s3', region_name=region)
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})

if __name__ == "__main__":
    bucket_name = "transcribe-youtube-distinct-speakers"
    region = 'us-west-1'  # Change this if you want to use another region
    create_s3_bucket(bucket_name, region)
    print(f"S3 bucket created: {bucket_name}")

