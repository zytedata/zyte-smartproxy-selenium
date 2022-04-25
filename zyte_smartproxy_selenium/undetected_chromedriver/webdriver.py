import seleniumwire.undetected_chromedriver as uc

from zyte_smartproxy_selenium.webdriver import ZyteModifyRequestsMixin


class Chrome(ZyteModifyRequestsMixin, uc.Chrome):
    def __init__(self, *args, **kwargs):
        self.zyte_init(super(), *args, **kwargs)


ChromeOptions = uc.ChromeOptions
