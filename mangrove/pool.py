from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

from boto import ec2


class ServicePool(object):
    """Aws service connection pool wrapper

    ServicePool class should be subclassed to provide
    an amazon aws service connection pool. To do so,
    creating a brand new class subclassing this one and
    setting the _aws_module_name class attribute to an
    existing boto module class should be enough.

    * *Examples*: please take a look to mangrove.services
    modules.

    * *Nota*: To be as efficient as possible, every selected
    regions connections will be made asynchronously using the
    backported python3.2 concurrent.futures module.

    :param  regions: AWS regions to connect the service to as
                     a default every regions will be used.
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
    _boto_module_name = 'boto'
    _aws_module_name = None

    def __init__(self, regions=None, aws_access_key_id=None, aws_secret_access_key=None):
        self.regions = regions or self._get_module_regions()

        # For performances reasons, every regions connections are
        # made concurrently through the concurent.futures library.
        future_connections = {}
        executor = ThreadPoolExecutor(max_workers=cpu_count())
        for region in self.regions:
            future_connections[region] = executor.submit(
                self._connect_module_to_region,
                region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

        # Once every connection futures have been spawned, let's
        # eval them.
        for region, future in future_connections.iteritems():
            setattr(self, region.replace("-", "_"), future.result())

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
        return self.module.connect_to_region(
            region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def _get_module_regions(self):
        """Retrieves the service's module allowed regions"""
        return [region.name for region in self.module.regions()]

    @property
    def module(self):
        """Services boto module as property"""
        module_name = '{}.{}'.format(self._boto_module_name, self._aws_module_name)
        module = __import__(module_name, self._aws_module_name)
        return getattr(module, self._aws_module_name)


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
            _services = ['ec2', 's3', 'sqs']

        pool = MyPool(regions=['eu-west-1'])
        pool.ec2.eu_west_1.get_all_instances()
        pool.s3.bucket('test')
        ...

    :param  services: services to add to the mixin connection pool
    :type   services: list of strings

    :param  regions: AWS regions to connect the service to as
                     a default every regions will be used.
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
    _service_names = []

    def __init__(self, services=None, regions=None,
                 aws_access_key_id=None, aws_secret_access_key=None):
        services = services or self._service_names

        for service in services:
            self.add_service(
                service,
                regions=regions,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

    @property
    def services(self):
        """Registered pool services list"""
        return self._service_names

    def add_service(self, service_name, regions=None,
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
        service_pool_kls = ServicePool
        service_pool_kls._aws_module_name = service_name

        service_pool_instance = service_pool_kls(
            regions=regions,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        setattr(self, service_name, service_pool_instance)
        self._service_names.append(service_name)

        return service_pool_instance


