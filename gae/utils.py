from google.appengine.api import users


def login_required(message=None):
    """
    You can use the @login_required decorator to disallow access to specific
    BaseRequestHandler methods (eg. get(), post()).
    """
    def wrap(func):
        def wrapped(request, *args, **kwargs):
            if users.get_current_user():
                return func(request, *args, **kwargs)
            else:
                if message:
                    return request.response.out.write(message)
                else:
                    return request.redirect(
                        users.create_login_url(request.request.uri)
                    )
        return wrapped
    return wrap
