import inspect


def initialize_classes_from_dict(class_type, data: dict) -> list:
    """Initializes classes from the headers and contents of the provided dictionary."""
    # determine the init parameters of the given class
    init_signature = inspect.signature(class_type.__init__)
    class_params = [param_name for param_name in init_signature.parameters.keys() if param_name not in ('self', 'kwargs')]
    class_params_no_defaults = [param_name for param_name, param in init_signature.parameters.items() 
                           if param.default == inspect.Parameter.empty and param_name not in ('self', 'kwargs')]

    # check that data has at least keys for the required parameters
    if not all(param_name in data for param_name in class_params_no_defaults):
        missing_keys = [key for key in class_params_no_defaults if key not in data]
        raise ValueError(f'Input data dictionary for the {class_type.__name__} class is missing required keys: {", ".join(missing_keys)}')

    # Determine the length of the lists in data to iterate over
    num_items = len(next(iter(data.values())))

    params_with_values = [param_name for param_name in class_params if param_name in data.keys()]
    
    # Initialize a list to hold the created class instances
    instances = []

    for i in range(num_items):
        # Extract parameters and additional kwargs
        args = [data[param][i] for param in params_with_values]
        kwargs = {key: value[i] for key, value in data.items() if key not in params_with_values}
        
        # Initialize the class instance with *args and **kwargs
        instance = class_type(*args, **kwargs)
        instances.append(instance)
    
    return instances