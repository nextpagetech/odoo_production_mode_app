from . import controllers
from . import models


def post_load():
    from . import http_patch

    http_patch.install()
