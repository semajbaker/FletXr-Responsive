from fletx.utils import get_page
from fletx.core.http import HTTPResponse

def get_storage():
    """Return Running Page's Client Storage"""

    return get_page().client_storage

def get_http_error_message(res: HTTPResponse):
    """Return HTTP Error Message based on status code"""

    data = res.json() if res.is_json else {}
    error_msg = data.get('message').get('en')

    if res.status == 400:
        return f"Bad Request, {error_msg}\nplease check your input."
    
    if res.status == 401:
        return f"Unauthorized, {error_msg}\nplease log in again."
    
    if res.status == 403:
        return "Forbidden, you don't have permission to access this resource."
    
    if res.status == 404:
        return "The resource you were looking for could not be found."
    
    if res.status == 500:
        return "Internal Server Error, please try again later."
    
    return "An unexpected error occurred, please try again later."
