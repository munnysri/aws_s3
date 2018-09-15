#! /usr/bin/env python
try:
    import boto3
except ImportError:
    print ("python boto3 not supported.")
    sys.exit(1)

import     time
import     csv
import     sys
import     os
import     subprocess
from       argparse import ArgumentParser
from       datetime import datetime, timedelta
import     getpass
import     sqsmsg
import     awscontext

# init globals
version='1.0'
msgErrPrefix='>>> Error: '
msgInfoPrefix='>>> Info: '
debugPrefix='>>> Debug: '

try:
    import boto3
except ImportError:
    print (__file__ + ": python boto3 not supported.")
    sys.exit(1)

def pInfo(msg):
    tmsg=time.asctime()
    print(msgInfoPrefix+tmsg+": "+msg)

def pError(msg):
    tmsg=time.asctime()
    print(msgErrPrefix+tmsg+": "+msg)

def pDebug(msg):
    if debug:
        tmsg=time.asctime()
        print(debugPrefix+tmsg+": "+msg)
def Summary(hdr):
    print(hdr)
    print( '\tVersion: ' + version)
    print( '\tSQS URL: ' + url)
    print( '\tPurge message queue: ' + str(purgequeue))
    print( '\tSend message: ' + str(sendmsg))
    print( '\tMessage: ' + message)
    tmsg=time.asctime()
    print( '\tTime: ' + tmsg)

# defaults
defSqsUrl = 'https://sqs.us-east-1.amazonaws.com/591206506624/nhlbi-uw-s3'
defMsg = "Test message from " + __file__
defCtxFile = 'awscontext.json'
defAwsCtx = 'default'

# parse input
parser = ArgumentParser( description = "script to copy local files to s3 and send an sqs msg" )
parser.add_argument( "-C", "--ctxfile", default = defCtxFile,
                     help = "Contexts json file [default: " + defCtxFile + "]" )
parser.add_argument( "-a", "--awsctx", default = defAwsCtx,
                     help = "Contexts json file [default: " + defAwsCtx + "]" )
parser.add_argument( "-P", "--purgequeue", action="store_true", default = False,
                     help = "Purge sqs queue [default: False]" )
parser.add_argument( "-l", "--listmsgs", action="store_true", default = False,
                     help = "Send test message to sqs [default: False]" )
parser.add_argument( "-s", "--sendmsg", action="store_true", default = False,
                     help = "Send test message to sqs [default: False]" )
parser.add_argument( "-m", "--message", default = defMsg,
                     help = "test message to send to sqs [default: " + defMsg + "]" )
parser.add_argument( "--version", action="store_true", default = False,
                     help = "Print version of " + __file__ )
args = parser.parse_args()
# set result of arg parse_args
ctxfile = args.ctxfile
awsctx = args.awsctx
message = args.message
purgequeue = args.purgequeue
sendmsg = args.sendmsg
listmsgs = args.listmsgs

# create the awscontext object
allctx = awscontext.awscontext(ctx_file = ctxfile, verbose = debug)

url = allctx.getsqsurl(awsctx)
if url == None:
    pError('SQS url not found in ' + awsctx)
    sys.exit(2)
profile = allctx.getprofile(awsctx)
if profile == None:
    pError('Profile not found in ' + awsctx)
    sys.exit(2)

# version
if args.version:
    print(__file__ + " version: " + version)
    sys.exit()
# get the sqs client
session = boto3.Session(profile_name=profile)
sqs = session.client('sqs')
# send message
if sendmsg:
    sqsmsg = sqsmsg.encode(message, typemsg = 'test')
    pInfo("Sending message: " + sqsmsg)
    # send it
    sqs.send_message(QueueUrl=url,MessageBody=sqsmsg)

# purge sqs
elif purgequeue:
    pInfo("Purging queue: " + url)
    sqs.purge_queue(QueueUrl=url)
elif listmsgs:
    msgKey = "Messages"
    while True:
        msg = sqs.receive_message(QueueUrl=url,WaitTimeSeconds=1)
        if msgKey in msg.keys():
            theMsg = msg[msgKey][0]['Body']
            rHandle = msg[msgKey][0]['ReceiptHandle']
            pInfo("Message: " + theMsg + "\n\tHandle: " + str(rHandle))
        else:
            break
else:
    parser.print_help(sys.stderr)
