def kw(*args, **kwargs):
    for val in args:
        if val is None:
            continue
        elif isinstance(val, dict):
            kwargs.update(val)
        else:
            raise ValueError(f'Unrecognized kwargs: {val}')
    return kwargs
