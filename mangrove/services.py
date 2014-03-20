from mangrove.pool import ServicePool


class Ec2Pool(ServicePool):
    service = 'ec2'


class S3Pool(ServicePool):
    service = 's3'


class EmrPool(ServicePool):
    service = 'emr'


class AutoscalePool(ServicePool):
    service = 'autoscale'


class DynamoDB2Pool(ServicePool):
    service = 'dynamodb2'


class DynamoDBPool(ServicePool):
    service = 'dynamodb'


class RdsPool(ServicePool):
    service = 'rds'


class ElasticachePool(ServicePool):
    service = 'elasticache'


class RedshiftPool(ServicePool):
    service = 'redshift'


class SimpleDBPool(ServicePool):
    service = 'sdb'


class CloudFormationPool(ServicePool):
    service = 'cloudformation'


class BeanstalkPool(ServicePool):
    service = 'beanstalk'


class IamPool(ServicePool):
    service = 'iam'


class StsPool(ServicePool):
    service = 'sts'


class CloudSearchPool(ServicePool):
    service = 'cloudsearch'


class ElasticTranscoderPool(ServicePool):
    service = 'elastictranscoder'


class SwfPool(ServicePool):
    service = 'swf'


class SqsPool(ServicePool):
    service = 'sqs'


class SimpleNotificationPool(ServicePool):
    service = 'sns'


class SimpleEmailPool(ServicePool):
    service = 'ses'


class VpcPool(ServicePool):
    service = 'vpc'


class ElbPool(ServicePool):
    service = 'elb'


class GlacierPool(ServicePool):
    service = 'glacier'


class MechanicalTurkPool(ServicePool):
    service = 'mturk'


class SupportPool(ServicePool):
    service = 'support'
