from rest_framework.throttling import SimpleRateThrottle


class PersonRequestThrottle(SimpleRateThrottle):
    """
    To validate user can send three request in minute.
    """

    scope = "person"
