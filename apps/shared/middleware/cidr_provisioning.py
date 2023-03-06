import ipaddress

try:
    from packaging.version import Version
except ImportError:
    from distutils.version import StrictVersion as Version  # pylint: disable=W4901

import django
from django.conf import settings
from django.core.exceptions import DisallowedHost, MiddlewareNotUsed
from django.http.request import split_domain_port, validate_host


class AllowCIDRAndProvisioningMiddleware:
    """
    Copyright (c) 2018, Paul McLanahan
    Author: Paul McLanahan <pmac@mozilla.com>
    Home Page: https://github.com/mozmeao/django-allow-cidr
    Thanks for Paul McLanahan <pmac@mozilla.com>

    Customize:
        Author: NTT <iamdev.top>
        Content: Adding allow IP request from some path. (There was called 'provisioning')
        Config settings:
            - PROVISIONING_PATH_PREFIX (str)
            - ALLOWED_IP_PROVISIONING (list str ip)
    """

    ORIG_ALLOWED_HOSTS = []
    allowed_cidr_nets = []
    allowed_provisioning_nets = []
    provisioning_path_prefix = settings.PROVISIONING_PATH_PREFIX
    provisioning_access_key = settings.PROVISIONING_ACCESS_KEY
    provisioning_access_value = settings.PROVISIONING_ACCESS_VALUE

    def __init__(self, get_response, *args, **kwargs):
        self.get_response = get_response
        if Version(django.get_version()) < Version("2.2"):
            raise NotImplementedError(
                "This version of django-allow-cidr requires at least Django 2.2"
            )

        super().__init__(*args, **kwargs)

        allowed_cidr_nets = getattr(settings, "ALLOWED_CIDR_NETS", None)
        allowed_provisioning_nets = getattr(settings, 'ALLOWED_IP_PROVISIONING', None)

        if not allowed_cidr_nets:
            raise MiddlewareNotUsed()

        self.allowed_cidr_nets = [ipaddress.ip_network(net) for net in allowed_cidr_nets]
        self.allowed_provisioning_nets = [ipaddress.ip_network(net) for net in allowed_provisioning_nets]

        if settings.ALLOWED_HOSTS != ["*"]:
            # add them to a global so that we keep the original setting
            # for multiple instances of the middleware.
            self.ORIG_ALLOWED_HOSTS.extend(settings.ALLOWED_HOSTS)
            settings.ALLOWED_HOSTS = ["*"]
        elif not self.ORIG_ALLOWED_HOSTS:
            # ALLOWED_HOSTS was originally set to '*' so no checking is necessary
            raise MiddlewareNotUsed()

    def __call__(self, request):
        # Processing the request before we generate the response
        host = request.get_host()
        domain, _port = split_domain_port(host)

        # Split path and navigate request go to check provisioning or other.
        if request.path.startswith(self.provisioning_path_prefix):
            should_raise = True
            for net in self.allowed_provisioning_nets:
                try:
                    if ipaddress.ip_address(domain) in net:
                        should_raise = False
                        break
                except ValueError:
                    # not an IP
                    break
            if should_raise:
                raise DisallowedHost(f"Access Denied for host: {host}.")
            valid_data = request.META.get("HTTP_" + self.provisioning_access_key, None)
            if valid_data != self.provisioning_access_value:
                raise DisallowedHost(f"Access Denied for host: {host}.")
        else:
            # valid range IP CIDR and global allowed host
            if not domain or not validate_host(domain, self.ORIG_ALLOWED_HOSTS):
                should_raise = True
                for net in self.allowed_cidr_nets:
                    try:
                        if ipaddress.ip_address(domain) in net:
                            should_raise = False
                            break
                    except ValueError:
                        # not an IP
                        break

                if should_raise:
                    raise DisallowedHost(f"Invalid HTTP_HOST header: {str(host)}.")
        response = self.get_response(request)

        return response
