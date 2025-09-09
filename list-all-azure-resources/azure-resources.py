# pip install azure-identity azure-mgmt-resource

import csv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient

credential = DefaultAzureCredential()
subscription_client = SubscriptionClient(credential)

with open("azure_resources.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Resource Name", "Resource Type", "Subscription"])

    for sub in subscription_client.subscriptions.list():
        subscription_id = sub.subscription_id
        subscription_name = sub.display_name

        resource_client = ResourceManagementClient(credential, subscription_id)

        for resource in resource_client.resources.list():
            writer.writerow([resource.name, resource.type, subscription_name])

print("✅ Exported to azure_resources.csv")
