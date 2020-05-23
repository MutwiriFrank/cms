from django.http import HttpResponse
from django.shortcuts import redirect

# to be placed on top of login and register, to send already authenticated users to a specific page


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # print('working', allowed_roles)
            group = None

            # if returns all available groups
            if request.user.groups.exists():
                # returns admin or customer depending with the user. 0 means we are grabbing the first group.
                # there can be more than 1 group. o selects first group
                # in our case we only have one group
                group = request.user.groups.all()[0].name

                # we then check if that group s allowed to perform certain roles
                if group in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse("You are not authorized to view this page")

        return wrapper_func
    return decorator


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == 'customer':
            return redirect('user')

        if group == 'admin':
            return view_func(request, *args, **kwargs)
    return wrapper_function
