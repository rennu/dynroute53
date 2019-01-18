#!/usr/bin/python

import boto3, yaml, os, argparse, urllib2, sys, socket

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
      fp = open(path, "r")
      config = yaml.load(fp)
      fp.close()
    except:
      print "Could not open or parse config file."
      return False
    return True
  else:
    return False

def getMyIp():
  ip = urllib2.urlopen(config["IPSource"]).read().strip()
  isOk = False
  try:
    socket.inet_aton(ip)
    return ip
  except:
    print "Could not get your IP."
    sys.exit(1)

config = {}
parser = createParser()
args = parser.parse_args()

if loadConfig(args.config):
  session = boto3.Session(profile_name = config["AWSProfileName"])
  client = session.client("route53")

  if len(config["zones"]) > 0:
    myip = getMyIp()
    for zone in config["zones"]:
      changes = []
      for hostname in zone["hostnames"]:
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
      try:
        client.change_resource_record_sets(
          HostedZoneId = zone["zoneId"],
          ChangeBatch = { "Changes": changes }
        )
        print "Updated zone {0} A records using IP {1} for records: {2}." . format(zone["zone"], myip, ', '.join(zone["hostnames"]))
      except:
        print "Could not update zone: {0}" . format(zone["name"])

  else:
    print "Could not find any zone definitions."

else:
  print "Could not load config."
