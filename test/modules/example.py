from muapi.Module import Module

m = Module('users', __name__, url_prefix='/hello', no_version=True)

def hello():
    return "hello"

m.add_url_rule('', view_func=hello, methods=['GET'])

