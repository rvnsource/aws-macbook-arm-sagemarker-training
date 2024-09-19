import boto3
import sagemaker
from sagemaker.sklearn import SKLearn
from sagemaker.local import LocalSession
import pandas as pd
from sklearn.datasets import load_iris  # Import load_iris
from sklearn.model_selection import train_test_split  # Import train_test_split

# Step 1: Initialize a session with the base credentials (using 'demouser' profile)
session = boto3.Session(profile_name='demouser')  # Ensure this profile has permission to assume the role

# Step 2: Use STS client to assume the role and get temporary credentials
sts_client = session.client('sts')

assumed_role_object = sts_client.assume_role(
    RoleArn="arn:aws:iam::378703906039:role/demouser-role",  # Your target role ARN
    RoleSessionName="demo-session"
)

# Step 3: Extract temporary credentials
credentials = assumed_role_object['Credentials']
aws_access_key_id = credentials['AccessKeyId']
aws_secret_access_key = credentials['SecretAccessKey']
aws_session_token = credentials['SessionToken']

# Step 4: Print credentials (optional)
print("AWS Access Key ID:", aws_access_key_id)
print("AWS Secret Access Key:", aws_secret_access_key)
print("AWS Session Token:", aws_session_token)

# Step 5: Create a new session using these temporary credentials
temp_session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    aws_session_token=aws_session_token,
    region_name='us-east-1'
)

# Step 6: Use the new session for SageMaker operations
sagemaker_session = LocalSession(boto_session=temp_session)
sagemaker_session.config = {'local': {'local_code': True}}

# Verify the temporary credentials
identity = temp_session.client('sts').get_caller_identity()
print(f"Running as: {identity['Arn']}")

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Save the training data locally
train_data = pd.DataFrame(X_train, columns=iris.feature_names)
train_data['target'] = y_train
train_data.to_csv('iris_train.csv', index=False)

# Set up the SageMaker SKLearn estimator
role = "arn:aws:iam::378703906039:role/demouser-role"  # Replace with your actual role ARN

sklearn_estimator = SKLearn(
    entry_point='train.py',  # Your local training script
    role=role,
    instance_count=1,
    instance_type='local',  # Use local mode
    framework_version='0.23-1',
    py_version='py3',
    sagemaker_session=sagemaker_session  # Corrected variable name to use the right session
)

# Train the model locally
sklearn_estimator.fit({'train': 'file://iris_train.csv'})


