# mangrove

## What


Mangrove is a set of classes on top of the boto library providing aws services connexion pools.
It is shipped with both abstract classes allowing you to build your own pools and pre-existing helpers class to get started immediatly with pools handling the various regions supported by amazon aws services.

## Why

Out the box boto's clients are attached to specific individual regions through the ``connect_to_region`` method.
We needed a way to connect to multiple regions and services at once in elegant way.


## How to use it


### Using the services helpers class

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
