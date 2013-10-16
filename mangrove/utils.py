def get_boto_module(module_name, boto_module_name="boto"):
    module_path = '{}.{}'.format(boto_module_name, module_name)
    module = __import__(module_path, module_name)
    return getattr(module, module_name)


