#!/usr/bin/env python3
"""AWS CDK App for Habit Tracker RPG."""
import os
import aws_cdk as cdk
from stacks.main_stack import HabitTrackerRpgStack


app = cdk.App()

# Get environment from context or default
env_name = app.node.try_get_context("env") or "dev"

# Define environment
env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION", "ap-northeast-1"),
)

HabitTrackerRpgStack(
    app,
    f"HabitTrackerRpg-{env_name}",
    env=env,
    env_name=env_name,
)

app.synth()
