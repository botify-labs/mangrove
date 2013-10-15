from mangrove.pool import ServicePool


class Ec2Pool(ServicePool):
    _aws_module_name = 'ec2'


class S3Pool(ServicePool):
    _aws_module_name = 's3'


class EmrPool(ServicePool):
    _aws_module_name = 'emr'


class AutoscalePool(ServicePool):
    _aws_module_name = 'autoscale'


class DynamoDB2Pool(ServicePool):
    _aws_module_name = 'dynamodb2'


class DynamoDBPool(ServicePool):
    _aws_module_name = 'dynamodb'


class RdsPool(ServicePool):
    _aws_module_name = 'rds'


class ElasticachePool(ServicePool):
    _aws_module_name = 'elasticache'


class RedshiftPool(ServicePool):
    _aws_module_name = 'redshift'


class SimpleDBPool(ServicePool):
    _aws_module_name = 'sdb'


class CloudFormationPool(ServicePool):
    _aws_module_name = 'cloudformation'


class BeanstalkPool(ServicePool):
    _aws_module_name = 'beanstalk'


class IamPool(ServicePool):
    _aws_module_name = 'iam'


class StsPool(ServicePool):
    _aws_module_name = 'sts'


class CloudSearchPool(ServicePool):
    _aws_module_name = 'cloudsearch'


class ElasticTranscoderPool(ServicePool):
    _aws_module_name = 'elastictranscoder'


class SwfPool(ServicePool):
    _aws_module_name = 'swf'


class SqsPool(ServicePool):
    _aws_module_name = 'sqs'


class SimpleNotificationPool(ServicePool):
    _aws_module_name = 'sns'


class SimpleEmailPool(ServicePool):
    _aws_module_name = 'ses'


class VpcPool(ServicePool):
    _aws_module_name = 'vpc'


class ElbPool(ServicePool):
    _aws_module_name = 'elb'


class GlacierPool(ServicePool):
    _aws_module_name = 'glacier'


class MechanicalTurkPool(ServicePool):
    _aws_module_name = 'mturk'


class SupportPool(ServicePool):
    _aws_module_name = 'support'
