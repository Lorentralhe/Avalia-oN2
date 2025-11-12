import os, json, uuid, boto3
from datetime import datetime

sqs = boto3.client('sqs')
ddb = boto3.resource('dynamodb')
QUEUE_URL = os.environ.get('QUEUE_URL')
TABLE = ddb.Table(os.environ.get('DDB_TABLE'))

def handler(event, context):
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)

        required = ['cliente','telefone','modelo','problema']
        if not all(k in body for k in required):
            return _response(400, {'error':'dados incompletos'})

        item = {
            'id': str(uuid.uuid4()),
            'cliente': body['cliente'],
            'telefone': body['telefone'],
            'modelo': body['modelo'],
            'problema': body['problema'],
            'status': 'RECEBIDO',
            'criado_em': datetime.utcnow().isoformat()+'Z'
        }

        # Salva no DynamoDB
        TABLE.put_item(Item=item)

        # Enfileira para processamento
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(item))

        return _response(202, {'message':'solicitação recebida','id': item['id']})
    except Exception as e:
        return _response(500, {'error': str(e)})

def _response(status, body):
    return {'statusCode':status,'headers':{'Content-Type':'application/json'},'body':json.dumps(body)}
