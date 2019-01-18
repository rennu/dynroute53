# Hostname A Record (IP) Updater for AWS Route53

This simple python script can be used to update Route53 A record sets automatically. It supports multiple zones.

## Installation

1. Create a new IAM user that is able to edit Route53 zones (The user has AmazonRoute53FullAccess permission)
2. Create a new access key for the user
3. Configure AWS Credentials on your host. The script assumes to find credentials under profile name "dyndns" (ie. using aws-cli: aws configure --profile dyndns)
4. Install required python modules (boto3): pip install -r requirements.txt
5. Configure the client (config.yml). If you wish to use some other source for your external IP, the site should return only your IP in plain text and nothing else.
6. Run the script: ./client.py --config /path/to/config.yml
7. Optional: Add script to crontab

## TODO
* Maybe add support for other record types ie. MX?
* Maybe send error messages over email?
* Maybe run script as a service and do update when network interface goes up?
