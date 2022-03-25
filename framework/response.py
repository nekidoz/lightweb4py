from framework import settings

# Default response code, headers and body

RESP_DEF_CODE = settings.HTTP_CODE_NOTFOUND
RESP_DEF_HEADERS = {'Content-Type': 'text/html; charset=' + settings.HTML_ENCODING}
RESP_DEF_BODY = ""

# ATTRIBUTES:
# status_code - integer status code
# headers - dictionary of HTTP headers
# body - response body
class Response:

    def __init__(self, status_code=RESP_DEF_CODE, body: str = RESP_DEF_BODY):
        self.status_code = status_code
        self.headers = RESP_DEF_HEADERS
        self.body = body