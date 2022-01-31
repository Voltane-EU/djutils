# djutils
## Tools for use within the django framework

djutils provides tools for common actions within the django framework.

It includes tools for:
- Administration interface
- Cryptographics
- Database interaction
- Exceptions
- HTTP Handling
- IP-Address handling
- Mixins for Classes

## Installation
Use the python package manager pip to install djutils.

```bash
pip install djutils
```

## Usage
Just an example how you could use the exceptions_to_http decorator.
Each method defined in djutils has a small documentation with it.
```python
from djutils import http, exceptions

@http.exceptions_to_http(exceptions.Error)
def my_route(request):
    if request.POST:
        raise exceptions.Error("POST is not allowed", code="no_post", status_code=403)

    return "Hello World"
```

## License
GNU LGPLv2.1, see LICENSE

## Maintainer
This package is maintained by Manuel Stingl.
