from mangrove.pool import ConnexionPool


class Ec2Pool(ConnexionPool):
    _aws_module_name = 'ec2'


class S3Pool(ConnexionPool):
    _aws_module_name = 's3'


class EmrPool(ConnexionPool):
    _aws_module_name = 'emr'


class AutoscalePool(ConnexionPool):
    _aws_module_name = 'autoscale'


class DynamoDB2Pool(ConnexionPool):
    _aws_module_name = 'dynamodb2'


class DynamoDBPool(ConnexionPool):
    _aws_module_name = 'dynamodb'


class RdsPool(ConnexionPool):
    _aws_module_name = 'rds'


class ElasticachePool(ConnexionPool):
    _aws_module_name = 'elasticache'


class RedshiftPool(ConnexionPool):
    _aws_module_name = 'redshift'


class SimpleDBPool(ConnexionPool):
    _aws_module_name = 'sdb'


class CloudFormationPool(ConnexionPool):
    _aws_module_name = 'cloudformation'


class BeanstalkPool(ConnexionPool):
    _aws_module_name = 'beanstalk'


class IamPool(ConnexionPool):
    _aws_module_name = 'iam'


class StsPool(ConnexionPool):
    _aws_module_name = 'sts'


class CloudSearchPool(ConnexionPool):
    _aws_module_name = 'cloudsearch'


class ElasticTranscoderPool(ConnexionPool):
    _aws_module_name = 'elastictranscoder'


class SwfPool(ConnexionPool):
    _aws_module_name = 'swf'


class SqsPool(ConnexionPool):
    _aws_module_name = 'sqs'


class SimpleNotificationPool(ConnexionPool):
    _aws_module_name = 'sns'


class SimpleEmailPool(ConnexionPool):
    _aws_module_name = 'ses'


class VpcPool(ConnexionPool):
    _aws_module_name = 'vpc'


class ElbPool(ConnexionPool):
    _aws_module_name = 'elb'


class GlacierPool(ConnexionPool):
    _aws_module_name = 'glacier'


class MechanicalTurkPool(ConnexionPool):
    _aws_module_name = 'mturk'


class SupportPool(ConnexionPool):
    _aws_module_name = 'support'
