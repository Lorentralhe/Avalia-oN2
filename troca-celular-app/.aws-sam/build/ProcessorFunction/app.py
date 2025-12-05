import os, json, boto3
from time import sleep

sns = boto3.client('sns')
ddb = boto3.resource('dynamodb')
TABLE = ddb.Table(os.environ.get('DDB_TABLE'))
TOPIC_ARN = os.environ.get('TOPIC_ARN')

def handler(event, context):
    for record in event.get('Records', []):
        try:
            payload = json.loads(record['body'])
            result = process_exchange(payload)

            TABLE.update_item(
                Key={'id': payload['id']},
                UpdateExpression="SET #s = :s, detalhes = :d",
                ExpressionAttributeNames={"#s":"status"},
                ExpressionAttributeValues={":s":"PROCESSADO",":d":result}
            )

            # Notifica via SNS
            sns.publish(TopicArn=TOPIC_ARN, Message=json.dumps({'id':payload['id'],'status':'PROCESSADO'}))
        except Exception as e:
            print('Erro:', e)

def process_exchange(payload):
    sleep(0.2)
    problema = (payload.get("problema") or "").lower()
    action = "troca" if "não liga" in problema or "nao liga" in problema or "nao" in problema else "reparo"
    return {"acao": action}
