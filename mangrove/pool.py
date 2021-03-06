from abc import ABCMeta
from multiprocessing import cpu_count

from concurrent.futures import ThreadPoolExecutor

from boto import ec2

from mangrove.declarative import ServiceDeclaration, ServicePoolDeclaration
from mangrove.mappings import ConnectionsMapping
from mangrove.utils import get_boto_module
from mangrove.exceptions import (
    MissingMethodError,
    DoesNotExistError,
    NotConnectedError
)


class ServicePool(object):
    """Aws service connection pool wrapper

    ServicePool class should be subclassed to provide
    an amazon aws service connection pool. To do so,
    creating a brand new class subclassing this one and
    setting the services class attribute to an
    existing boto module class should be enough.

    * *Examples*: please take a look to mangrove.services
    modules.

    * *Nota*: To be as efficient as possible, every selected
    regions connections will be made asynchronously using the
    backported python3.2 concurrent.futures module.

    :param  regions: AWS regions to connect the service to as
                     a default every regions will be used.
    :type   regions: list of strings

    :param  default_region: region to be used as a default
    :type   default_region: string

    :param  aws_access_key_id: aws access key token (if not provided
                               AWS_ACCESS_KEY_ID will be fetched from
                               environment)
    :type   aws_access_key_id: string

    :param  aws_secret_access_key: aws secret access key (if not provided
                                   AWS_SECRET_ACCESS_KEY will be fetched from
                                   environment)
    :type   aws_secret_access_key: string
    """
    __meta__ = ABCMeta

    # Name of the boto python module to be used. Just in case
    # you'd wanna use a fork instead.
    _boto_module_name = 'boto'

    # Boto aws service name to bind the regionalized
    # pool to.
    service = None

    def __init__(self, connect=False, regions=None, default_region=None,
                 aws_access_key_id=None, aws_secret_access_key=None):
        self._service_declaration = ServiceDeclaration(self.service)
        self._service_declaration.regions = regions
        self._service_declaration.default_region = default_region
        self.module = self._service_declaration.module

        self._executor = ThreadPoolExecutor(max_workers=cpu_count())
        self._connections = ConnectionsMapping()

        # _default_region private property setting should
        # always be called after the _regions_names is set
        self._regions_names = regions
        self._default_region = default_region

        if connect is True:
            self.connect(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

    def connect(self, aws_access_key_id=None, aws_secret_access_key=None):
        """Starts connections to pool's services

        :param  aws_access_key_id: aws access key token (if not provided
                                AWS_ACCESS_KEY_ID will be fetched from
                                environment)
        :type   aws_access_key_id: string

        :param  aws_secret_access_key: aws secret access key (if not provided
                                    AWS_SECRET_ACCESS_KEY will be fetched from
                                    environment)
        :type   aws_secret_access_key: string
        """
        # For performances reasons, every regions connections are
        # made concurrently through the concurent.futures library.
        for region in self._service_declaration.regions:
            self._connections[region] = self._executor.submit(
                self._connect_module_to_region,
                region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

        if self._default_region is not None:
            self._connections.default = self._service_declaration.default_region

    def _connect_module_to_region(self, region, aws_access_key_id=None,
                                  aws_secret_access_key=None):
        """Calls the connect_to_region method over the service's
        module

        :param  region: AWS region to connect the service to.
        :type   region: list of strings

        :param  aws_access_key_id: aws access key token (if not provided
                                AWS_ACCESS_KEY_ID will be fetched from
                                environment)
        :type   aws_access_key_id: string

        :param  aws_secret_access_key: aws secret access key (if not provided
                                    AWS_SECRET_ACCESS_KEY will be fetched from
                                    environment)
        :type   aws_secret_access_key: string
        """
        return self.module.connect_to_region(region)

    @property
    def regions(self):
        return self._connections

    def region(self, region_name):
        """Access a pools specific region connections 
        :param  region_name: region connection to be accessed
        :type   region_name: string
        """
        if not region_name in self._connections:
            raise NotConnectedError(
                "No active connexion found for {} region, "
                "please use .connect() method to proceed.".format(region_name)
            )
        return self._connections[region_name]

    def add_region(self, region_name):
        """Connect the pool to a new region

        :param  region_name: Name of the region to connect to
        :type   region_name: string
        """
        region_client = self._connect_module_to_region(region_name)
        self._connections[region_name] = region_client
        self._service_declaration.regions.append(region_name)

class ServiceMixinPool(object):
    """Multiple AWS services connection pool wrapper class

    ServiceMixinPool mixes the ServicePool subclasses instances
    into independent pool. It can be pretty usefull when you need
    to build your own custom pool exposing multiple services in
    multiples regions.

    For example, insteading of instanciating different pools for each
    and every services you want to use, subclassing ServiceMixinPool
    would allow you to create a pool exposing them transparently like
    so:

    ::code-block: python
        class MyPool(ServiceMixinPool):
            services = {
                'ec2': {
                    'regions': '*',  # Wildcard for "every regions"
                    'default_region': 'eu-west-1'
                },
                'sqs': {
                    'regions': ['us-east-1', 'us-west-1', 'eu-west-1'],
                    'default_region': 'us-west-1',
                },
            }

        pool = MyPool()
        pool.ec2.eu_west_1.get_all_instances()
        pool.s3.bucket('test')
        ...

    :param  connect: Should the pool init services regions connections
                     on instanciation.
    :type   connect: bool

    :param  aws_access_key_id: aws access key token (if not provided
                               AWS_ACCESS_KEY_ID will be fetched from
                               environment)
    :type   aws_access_key_id: string

    :param  aws_secret_access_key: aws secret access key (if not provided
                                   AWS_SECRET_ACCESS_KEY will be fetched from
                                   environment)
    :type   aws_secret_access_key: string
    """
    __meta__ = ABCMeta

    # aws services to be added to the mixin pool. To add one, please
    # respect the following pattern: 
    # 'service_name': {'regions': [], 'default_region'}
    # * regions parameter should be whether a list of aws regions names,
    # or the '*' wildcard (['*'])
    # * default_region parameter should be an aws region part of
    # the provided regions parameters 
    services = {}

    def __init__(self, connect=False,
                 aws_access_key_id=None, aws_secret_access_key=None):
        self._executor = ThreadPoolExecutor(max_workers=cpu_count())
        self._services_declaration = ServicePoolDeclaration(self.services)
        self._services_store = {}

        self._load_services(connect)

    def _load_services(self, connect=None, aws_access_key_id=None,
                           aws_secret_access_key=None):
        """Helper private method adding every services referenced services
        to mixin pool

        :param  connect: Should the pool being connected to remote services
                         at startup.
        :type   connect: boolean

        :param  aws_access_key_id: aws access key token (if not provided
                                AWS_ACCESS_KEY_ID will be fetched from
                                environment)
        :type   aws_access_key_id: string

        :param  aws_secret_access_key: aws secret access key (if not provided
                                    AWS_SECRET_ACCESS_KEY will be fetched from
                                    environment)
        :type   aws_secret_access_key: string
        """
        for service_name, localisation in self._services_declaration.iteritems():
            self.add_service(
                service_name,
                connect=connect,
                regions=localisation.regions,
                default_region=localisation.default_region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

    def connect(self):
        """Connects every services in the pool"""
        for name, pool in self._services_store.iteritems():
            pool.connect()

    def add_service(self, service_name, connect=False,
                    regions=None, default_region=None,
                    aws_access_key_id=None, aws_secret_access_key=None):
        """Adds a service connection to the services pool

        :param  service_name: name of the AWS service to add
        :type   service_name: string

        :param  regions: AWS regions to connect the service to.
        :type   regions: list of strings

        :param  aws_access_key_id: aws access key token (if not provided
                                AWS_ACCESS_KEY_ID will be fetched from
                                environment)
        :type   aws_access_key_id: string

        :param  aws_secret_access_key: aws secret access key (if not provided
                                    AWS_SECRET_ACCESS_KEY will be fetched from
                                    environment)
        :type   aws_secret_access_key: string
        """
        service_pool_kls = type(service_name.capitalize(), (ServicePool,), {})
        service_pool_kls.service = service_name

        service_pool_instance = service_pool_kls(
            connect=False,
            regions=regions,
            default_region=default_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        setattr(self, service_name, service_pool_instance)

        if service_name not in self._services_store:
            self._services_store[service_name] = service_pool_instance
        if service_name not in self._services_declaration:
            self._services_declaration[service_name].regions = regions or '*'
            if default_region is not None:
                self._services_declaration[service_name].default_region = default_region

        return service_pool_instance

