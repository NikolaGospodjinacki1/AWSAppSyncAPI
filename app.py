#!/usr/bin/env python3
import os
import aws_cdk as cdk
from dotenv import load_dotenv
from stacks.api_stack import AwsAppSyncApiStack

load_dotenv()

app = cdk.App()
AwsAppSyncApiStack(
    app,
    "AwsAppSyncApiStack",
    env=cdk.Environment(
        account=os.getenv("PERSONALACCOUNTID"), region=os.getenv("REGION")
    ),
)

app.synth()
