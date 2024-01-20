import azure.functions as func
from os import getenv
import boto3
import ipaddress
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="UpdateDynamicIP")
def UpdateDynamicIP(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Got update request for Dynamic IP")

    try:
        IPv4 = ipaddress.IPv4Address(req.params.get('IPv4'))
    except ipaddress.AddressValueError:
        logging.error(f"Got a non-valid IPv4 address: {req.params.get('IPv4')}")
    try:
        IPv6 = ipaddress.IPv6Address(req.params.get('IPv6'))
    except ipaddress.AddressValueError:
        logging.error(f"Got a non-valid IPv6 address: {req.params.get('IPv6')}")

    client = boto3.client(
        'route53',
        aws_access_key_id=getenv("ACCESS_KEY"),
        aws_secret_access_key=getenv("SECRET_KEY"),
    )
    try:
        client.change_resource_record_sets(
            HostedZoneId=getenv("ZONE_ID"),
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": getenv("HOST"),
                            "Type": "A",
                            "TTL":  3600,
                            "ResourceRecords": [
                                {
                                    "Value": IPv4
                                }
                            ]
                        }
                    }
                ]
            }
        )
        logging.info(f"Updated IPv4 to {IPv4}")

        client.change_resource_record_sets(
            HostedZoneId=getenv("ZONE_ID"),
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": getenv("HOST"),
                            "Type": "AAAA",
                            "TTL":  3600,
                            "ResourceRecords": [
                                {
                                    "Value": IPv6
                                }
                            ]
                        }
                    }
                ]
            }
        )
        logging.info(f"Updated IPv6 to {IPv6}")
        returnBody = {"status": "ok", "message": "DNS records updated"}
        return func.HttpResponse(
             json.dumps(returnBody),
             status_code=200,
             mimetype="application/json",
        )
    except Exception as e:
        logging.error(e)
        returnBody = {"status": "error", "message": "Error updating DNS record"}
        return func.HttpResponse(
             json.dumps(returnBody),
             status_code=500,
             mimetype="application/json",
        )
