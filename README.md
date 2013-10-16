# mangrove

## What


Mangrove is a set of classes on top of the boto library providing aws services connexion pools.
It is shipped with both abstract classes allowing you to build your own pools and pre-existing helpers class to get started immediatly with pools handling the various regions supported by amazon aws services.

## Why

Out the box boto's clients are attached to specific individual regions through the ``connect_to_region`` method.
We needed a way to connect to multiple regions and services at once in elegant way.


## How to use it


### Helpers

Mangrove is shipped with services helpers classes to help you getting started immediately.
They provide a transparent access to the boto classes through regions specific attributes. 

For example:

```python
from mangrove.services import Ec2Pool, S3Pool

ec2_pool = Ec2Pool()  # As a default every regions will be connected
s3_pool = S3Pool(regions=['us-east-1', 'us-west-1'])  # Or you can specify the one you're interested in


# Once your pool is created you can access the various regions specific
# client through their related instance attributes. 
ec2_pool.us_west_1.get_all_instances()
[Reservation:i7291b6,
 Reservation:i2e435a,
 ...
]

ec2_pool.us_east_1.get_all_images()
[]
```

### Create your own service pool

If you can't find your amazon aws service client pool listed in the ``mangrove.services`` module.
Creating your own should be as easy as subclassing ``mangrove.pool.ServicePool``:

```python
from mangrove.pool import ServicePool

class MySupperDupperPool(ServicePool):
    # Subclassing ServicePool is as easy as setting a class
    # attribute to the name of the related boto service class
    # name
    _aws_module_name = 'mysupperdupperservice'
    
# Then you can instantiate it and use it as any other mangrove ServicePool
# subclasses
p = MySupperDupperPool(regions=['eu-west-1', 'us-west-1'])
p.us_west_1.botoservice_method()
```

If the boto service you're trying to expose as a pool has a custom way to connect to a region, or
to list regions, feel free to override the ``_connect_module_to_region`` and ``_get_module_regions`` ServicePool methods to.
For an example please take a look to the abstract ServicePool class implementation in ``mangrove.pool`` module.


### Creating your own multi-services pool


