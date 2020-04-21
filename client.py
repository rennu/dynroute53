#!/usr/bin/python

import boto3, yaml, os, argparse, urllib, sys, socket, logging
from botocore.exceptions import ClientError

logging.basicConfig(format='%(message)s')

def createParser():
  parser = argparse.ArgumentParser(description = "Dynamic DNS Client for Route 53")
  parser._action_groups.pop()
  args = parser.add_argument_group("Available arguments")
  args.add_argument("--config",
    help = "Path to configuration file",
    required = True)
  return parser

def loadConfig(path):
  global config
  if os.path.exists(path):
    try:
      with open(path, "r") as file:
        config = yaml.load(file, Loader = yaml.FullLoader)
      return config
    except:
      logging.error("Could not read or parse config.")
      sys.exit(1)
  else:
    logging.error("Could not find config file.")
    sys.exit(1)

def getMyIp():
  try:
    ip = urllib.request.urlopen(config["IPSource"]).read().decode('utf-8').strip()
    socket.inet_aton(ip)
    return ip
  except:
    logging.error(("Could not get IP from {0} or failed to parse result.".format(config["IPSource"])))
    sys.exit(1)

def getZones(client):
  try:
    zonesList = client.list_hosted_zones()
  except ClientError as e:
    logging.error("Could not list zones")
    logging.error(e)
  zones = {}
  for zone in zonesList["HostedZones"]:
    zoneName = zone["Name"][0:len(zone["Name"]) - 1].lower()
    zoneValue = zone["Id"]
    zones[zoneName] = zoneValue
  return zones

config = {}
parser = createParser()
args = parser.parse_args()
config = loadConfig(args.config)

session = boto3.Session(profile_name = config["AWSProfileName"])
client = session.client("route53")
myip = getMyIp()
zones = getZones(client)

if len(config["zones"]) > 0:
  for zone in config["zones"]:
    if zone["zone"] in zones:
      changes = []
      for hostname in zone["hostnames"]:
        currentIp = ""
        try:
          currentIp = socket.gethostbyname(hostname)
        except:
          ""
        if currentIp != myip:
          changes.append({
            "Action": "UPSERT",
            "ResourceRecordSet": {
              "Name": hostname,
              "Type": "A",
              "TTL": config["TTL"],
              "ResourceRecords": [
                { "Value": myip }
              ]
            }
          })
      if len(changes) > 0:
        try:
          client.change_resource_record_sets(
            HostedZoneId = zones[zone["zone"].lower()],
            ChangeBatch = { "Changes": changes }
          )
          print("Updated zone {0} A records for {1} using IP {2}." . format(zone["zone"], ', '.join(map(lambda c: c["ResourceRecordSet"]["Name"], changes)), myip))
        except ClientError as e:
          logging.error("Could not update zone: {0}." . format(zone["zone"])) 
          logging.error(e)
      else:
        print("No changes detected.")
    else:
      logging.error("Could not find zone {0} in Route53.".format(zone["zone"]))
else:
  logging.error("Could not find any zone definitions.")
