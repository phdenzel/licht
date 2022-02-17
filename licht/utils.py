"""
licht.utils

@author: phdenzel
"""


def str2bool_explicit(v):
    bstr = v.lower()
    if bstr in ('true', 't', 'yes', 'y', '1'):
        return True
    elif bstr in ('false', 'f', 'no', 'n', '0'):
        return False
    else:
        return None


def linear_transformation(x, lower, upper, a=0, b=1,
                          allow_out_of_bounds=True,
                          as_int=False):
    """
    Map a value in interval [lower, upper] to interval [a, b]
    """
    x_new = (b-a)/(upper-lower)*(x-lower) + a
    if not allow_out_of_bounds:
        if x_new < a:
            x_new = a
        elif x_new > b:
            x_new = b
    if as_int:
        x_new = int(x_new)
    return x_new


def mired_transformation(temperature_or_mired):
    """
    Converts from and to mired units

    Note:
        - warm light: 500 mired ~ 2000 K
        - cold light: 160 mired ~ 6250 K
        - this transformation is also its own inverse
    """
    t_1M_kelvin = 1e6
    return t_1M_kelvin / temperature_or_mired


def percentages(x, *limits, transformation='linear', as_int=False):
    lower, upper = min(limits), max(limits)
    perc_min, perc_max = 0, 100
    if transformation == 'linear':
        x_transf = linear_transformation(x, lower, upper, a=perc_min, b=perc_max)
    elif transformation == 'log':
        NotImplemented
    else:
        x_transf = linear_transformation(x, lower, upper, a=perc_min, b=perc_max)
    if as_int:
        x_transf = int(x_transf)
    return x_transf


def percentages_bit8(x, **kwargs):
    kwargs.setdefault('as_int', True)
    return percentages(x, 0, 255, **kwargs)


def percentages_bit16(x, **kwargs):
    kwargs.setdefault('as_int', True)
    return percentages(x, 0, 65535, **kwargs)


def bit8(x, lower=0, upper=100, transformation='linear', as_int=True):
    """
    Converts to 8-bit pixel values
    """
    bit8_min, bit8_max = 0, 255
    if transformation == 'linear':
        x_transf = linear_transformation(x, lower, upper, a=bit8_min, b=bit8_max)
    elif transformation == 'log':
        NotImplemented
    else:
        x_transf = linear_transformation(x, lower, upper, a=bit8_min, b=bit8_max)
    if as_int:
        x_transf = int(x_transf)
    return x_transf


def bit16(x, lower=0, upper=100, transformation='linear', as_int=True):
    """
    Converts to 16-bit numbers
    """
    bit16_min, bit16_max = 0, 65535
    if transformation == 'linear':
        x_transf = linear_transformation(x, lower, upper, a=bit16_min, b=bit16_max)
    elif transformation == 'log':
        NotImplemented
    else:
        x_transf = linear_transformation(x, lower, upper, a=bit16_min, b=bit16_max)
    if as_int:
        x_transf = int(x_transf)
    return x_transf


def blackbody(x, lower=153, upper=500, as_int=True):
    """
    Converts to blackbody temperature units (assumes mired units on default)
    """
    if x < lower:
        x = lower
    elif x > upper:
        x = upper
    x_transf = mired_transformation(x)
    if as_int:
        x_transf = int(x_transf)
    return x_transf


def mired(x, lower=2000, upper=6535.95, as_int=True):
    """
    Converts to blackbody temperature units (assumes mired units on default)
    """
    if x < lower:
        x = lower
    elif x > upper:
        x = upper
    x_transf = mired_transformation(x)
    if as_int:
        x_transf = int(x_transf)
    return x_transf


if __name__ == "__main__":
    print("linear_transformation(4, 0, 10, 0, 100)")
    print(linear_transformation(4, 0, 10, 0, 100))
    print("linear_transformation(4, 0, 10)")
    print(linear_transformation(4, 0, 10))
    print("linear_transformation(0, 0, 10)")
    print(linear_transformation(0, 0, 10))
    print("linear_transformation(10, 0, 10)")
    print(linear_transformation(10, 0, 10))
    print("percentages(131, 0, 254)")
    print(percentages(131, 0, 254))
    print("blackbody(258)")
    print(blackbody(258))
    print("blackbody(153)")
    print(blackbody(153))
    print("blackbody(500)")
    print(blackbody(500))
    print("mired(2000)")
    print(mired(2000))
    print("mired(2004)")
    print(mired(2001))
    print("mired(6535.95)")
    print(mired(6535.94))
    print("mired_transformation(160)")
    print(mired_transformation(160))
    print("mired_transformation(mired_transformation(160))")
    print(mired_transformation(mired_transformation(160)))
