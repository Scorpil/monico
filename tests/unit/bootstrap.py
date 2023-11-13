def build_app():
    """Builds monic app with test dependencies"""
    storage = LocalStorage()
    return App(storage)
