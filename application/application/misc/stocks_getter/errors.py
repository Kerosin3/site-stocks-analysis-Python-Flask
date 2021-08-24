class ServerExeption(Exception):
    """
    base exception
    """
    pass


class NoSuchStock(ServerExeption):
    """no such stock"""
    pass


class SomethingBadHappened(ServerExeption):
    """unknown"""
    pass
