
class MobileAction:

    def __init__(self, display_name, url):
        assert type(display_name) is str
        assert type(url) is str

        self.display_name = display_name
        self.url = url
