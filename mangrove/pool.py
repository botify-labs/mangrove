from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

from boto import ec2


class ServicePool(object):
    _boto_module_name = 'boto'
    _aws_module_name = None

    def __init__(self, regions=None, aws_access_key_id=None, aws_secret_access_key=None):
        self.regions = regions or self._get_module_regions()

        future_connections = {}
        executor = ThreadPoolExecutor(max_workers=cpu_count())
        for region in self.regions:
            future_connections[region] = executor.submit(
                self._connect_module_to_region,
                region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

        for region, future in future_connections.iteritems():
            setattr(self, region.replace("-", "_"), future.result())

    def _connect_module_to_region(self, region, aws_access_key_id=None,
                                  aws_secret_access_key=None):
        return self.module.connect_to_region(
            region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    def _get_module_regions(self):
        return [region.name for region in self.module.regions()]

    @property
    def module(self):
        module_name = '{}.{}'.format(self._boto_module_name, self._aws_module_name)
        module = __import__(module_name, self._aws_module_name)
        return getattr(module, self._aws_module_name)


class ServiceMixinPool(object):
    _services = []

    def __init__(self, services=None, regions=None,
                 aws_access_key_id=None, aws_secret_access_key=None):
        services = services or self._services

        for service in services:
            service_pool_kls = ServicePool
            service_pool_kls._aws_module_name = service
            service_pool_instance = service_pool_kls(
                regions=regions,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )

            setattr(self, service, service_pool_instance)

