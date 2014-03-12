# mangrove

## What


Mangrove is a set of classes on top of the boto library providing aws services connexion pools.
It is shipped with both abstract classes allowing you to build your own pools and pre-existing helpers class to get started immediatly with pools handling the various regions supported by amazon aws services.

## Why

Out the box boto's clients are attached to specific individual regions through the ``connect_to_region`` method.
We needed a way to connect to multiple regions and services at once in elegant way.


## Installation

it's as simple as:

```bash
$ pip install pymangrove
```

## How to use it


### Helpers

Mangrove is shipped with services helpers classes to help you getting started immediately.
They provide a transparent access to the boto classes through regions specific attributes. 

For example:

```python
>>> from mangrove.services import Ec2Pool, S3Pool, SqsPool

>>> ec2_pool = Ec2Pool(connect=True)  # As a default every regions will be connected
>>> s3_pool = S3Pool(connect=True, regions=['us-east-1', 'us-west-1'])  # But you can specify the one you're interested in
>>> sqs_pool = SqsPool(connect=True, default_region='us-east-1')  # And, you can set a default region to be used later on


# Once your pool is created you can access the various regions specific
# client through the .regions property.
>>> ec2_pool.regions['us_west_1'].get_all_instances()
[Reservation:i7291b6,
 Reservation:i2e435a,
 ...
]
>>> ec2_pool.regions['us_east_1'].get_all_images()
[]

# If you've set a default_region, you might access it directly.
>>> sqs_pool.regions.default.get_all_queues()
[]

# Any time, you're able to add a region connection to the pool
>>> s3_pool.add_region('us-east-2')
>>> s3_pool.regions['us_east_2']
<S3Pool us_east_2>
```

### Create your own service pool

If you can't find your amazon aws service client pool listed in the ``mangrove.services`` module.
Creating your own should be as easy as subclassing ``mangrove.pool.ServicePool``:

```python
>>> from mangrove.pool import ServicePool

>>> class MySupperDupperPool(ServicePool):
        # Subclassing ServicePool is as easy as setting a class
        # attribute to the name of the related boto service class
        # name
        service = 'mysupperdupperservice'
```

Then you can instantiate it and use it as any other mangrove ServicePool subclasses:

```python
>>> p = MySupperDupperPool(connect=True, regions=['eu-west-1', 'us-west-1'])
>>> p.regions['us_west_1'].get_all_buckets()  # in this example, a S3 pool
```

Note that as ServicePool is the base class for helpers, you can of course dynamically add a region to the pool at anytime

```python
>>> p.add.regions['ap-southeast-1']
>>> p.regions['ap_southeast_1']
<MySupperDupperPool ap_southeast_1>
```

If the boto service you're trying to expose as a pool has a custom way to connect to a region, or
to list regions, feel free to override the ``_connect_module_to_region`` and ``_get_module_regions`` ServicePool methods to.
For an example please take a look to the abstract ServicePool class implementation in ``mangrove.pool`` module.


### Creating your own multi-services pool

You might find usefull to create a custom pool exposing multiple services at once: *ec2*, *s3* and *sqs* for example.
Mangrove provides a ``ServiceMixinPool`` abstract class to help you creating one. It's as simple as subclassing
and setting a class attribute:

```python
>>> from mangrove.pool import ServiceMixinPool

>>> class WebRelatedServicesPool(ServiceMixinPool):
        services = {
            'ec2': {
                'regions': ['us-east-1', 'eu-west-1'],
                'default_region': 'eu-west-1',
            },
            's3': {
                'regions': '*',
                'default_region': 'eu-west-1',
            },
            'sqs': {}
        ]
```

Once you instantiate your mixin pool, services you've specified will be exposed as ServicePool instance attributes.

```python
>>> mixin_pool = WebRelatedServicesPool(connect=True, regions=['us_west_1', 'eu_west_1'])
>>> mixin_pool.s3
<ServicePool S3>
>>> mixin_pool.ec2.regions['us_west_1'].get_all_instances()
[Reservation:i76f98b,
 Reservation:i23d4f8,
 ...
]
```


