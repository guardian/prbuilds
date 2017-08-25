import logging

class Metrics:

    TABLE_NAME = "prbuilds_metrics"
    
    def __init__(self, dyn):
        self.dynamo = dyn

    def init_tables(self):

        """ initialise dynamo tables, use existing if available """
        
        try:
            self._init_tables()
        except dynamodb_client.exceptions.ResourceInUseException:
            self.table = dynamodb.Table(self.TABLE_NAME)
            pass
    
    def _init_tables(self):

        """ create dynamo table for metrics data """
        
        self.table = self.dynamo.create_table(
            TableName=self.TABLE_NAME,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5
            },
            AttributeDefinitions=[
                { 'AttributeName': 'project','AttributeType': 'S' },
                { 'AttributeName': 'prnum','AttributeType': 'I' },
                { 'AttributeName': 'metric','AttributeType': 'S' },
                { 'AttributeName': 'type','AttributeType': 'S' },
                { 'AttributeName': 'value','AttributeType': 'S' }
            ],
            KeySchema=[
                { 'AttributeName': 'project', 'KeyType': 'HASH' },
                { 'AttributeName': 'prnum', 'KeyType': 'HASH' },
                { 'AttributeName': 'metric', 'KeyType': 'HASH' }
            ]
        )

        waiter = self.table.meta.client.get_waiter('table_exists')
        waiter.wait(TableName=self.TABLE_NAME)

    def put_metric(self, project, prnum, metric, typ, value):

        """ write a new metric to dynamodb """
        
        if not self.table:
            raise Exception("Put metric can not be called before init_tables")
        
        self.table.put_item(
            Item={
                'prjoject': project,
                'prnum': prnum,
                'metric': metric,
                'type': typ,
                'value': value,
            }
        )
        
