import logging

class Metrics:

    TABLE_NAME = "prbuilds_metrics"
    
    def __init__(self, dyn):
        self.dynamo = dyn

    def init_tables(self):

        """ initialise dynamo tables, use existing if available """

        try:
            self.create_tables()
            logging.info("creating tables")
        except:
            self.table = self.dynamo.Table(self.TABLE_NAME)
            logging.info("reusing existing table")
    
    def create_tables(self):

        """ create dynamo table for metrics data """
        
        self.table = self.dynamo.create_table(
            TableName=self.TABLE_NAME,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5
            },
            AttributeDefinitions=[
                { 'AttributeName': 'project','AttributeType': 'S' },
                { 'AttributeName': 'rid','AttributeType': 'S' },
            ],
            KeySchema=[
                { 'AttributeName': 'project', 'KeyType': 'HASH' },
                { 'AttributeName': 'rid', 'KeyType': 'RANGE' }
            ]
        )

        waiter = self.table.meta.client.get_waiter('table_exists')
        waiter.wait(TableName=self.TABLE_NAME)

    def put_metric(self, project, prnum, metric, typ, value):

        """ write a new metric to dynamodb """
        
        if not self.table:
            raise Exception("Put metric can not be called before init_tables")

        rid = "%s|%s" % (prnum, metric)
        
        self.table.put_item(
            Item={
                'project': project,
                'rid': rid,
                'prnum': prnum,
                'metric': metric,
                'type': typ,
                'value': value,
            }
        )
        
