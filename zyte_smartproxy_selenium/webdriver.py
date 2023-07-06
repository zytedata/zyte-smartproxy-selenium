from adblockparser import AdblockRules
from seleniumwire.webdriver import Chrome as _Chrome
from seleniumwire.webdriver import Edge as _Edge
from seleniumwire.webdriver import Firefox as _Firefox
from seleniumwire.webdriver import Remote as _Remote
from seleniumwire.webdriver import Safari as _Safari
from seleniumwire.webdriver import ActionChains  # noqa
from seleniumwire.webdriver import FirefoxOptions  # noqa
from seleniumwire.webdriver import FirefoxProfile  # noqa
from seleniumwire.webdriver import Proxy  # noqa
from seleniumwire.webdriver import ChromeOptions, DesiredCapabilities  # noqa
from zyte_smartproxy_selenium import __version__

try:
    # TouchActions does not exist in Selenium 4.1.1
    from selenium.webdriver import TouchActions  # noqa
except ImportError:
    pass

import inspect
import re
import requests

DEFAULT_SPM_HOST = 'http://proxy.zyte.com:8011'
DEFAULT_STATIC_BYPASS = True
DEFAULT_STATIC_BYPASS_REGEX = r'.*?\.(?:txt|json|css|less|gif|ico|jpe?g|svg|png|webp|mkv|mp4|mpe?g|webm|eot|ttf|woff2?)$'
DEFAULT_STATIC_DOMAINS = True
DEFAULT_STATIC_DOMAINS_LIST = []
DEFAULT_STATIC_DOMAINS_BLOCK = False
DEFAULT_BLOCK_ADS = True
DEFAULT_BLOCK_ADS_LISTS = [
    'https://secure.fanboy.co.nz/easylist.txt',
    'https://secure.fanboy.co.nz/easyprivacy.txt',
]
DEFAULT_HEADERS = {
    'X-Crawlera-Profile': 'pass',
    'X-Crawlera-Cookies': 'disable',
    'X-Crawlera-No-Bancheck': '1',
}
ZYTE_SPM_SELENIUM_VERSION = 'zyte-smartproxy-selenium/'+__version__


class ZyteModifyRequestsMixin:
    def zyte_init(self, super_obj, *args, **kwargs):

        def put_proxy_into_kwargs_seleniumwire_options(kwargs, spm_apikey, spm_host):
            if spm_apikey is not None:
                [scheme, host] = spm_host.split('//')
                spm_proxy = f'{scheme}//{spm_apikey}:@{host}'
                seleniumwire_options = kwargs.get('seleniumwire_options', {})
                seleniumwire_options['proxy'] = {
                    'http': spm_proxy,
                    'https': spm_proxy,
                    'no_proxy': 'localhost,127.0.0.1',
                }
                kwargs['seleniumwire_options'] = seleniumwire_options

        def fetch_adblock_rules(block_ads_lists):
            def remove_comments_and_html_elements(lines):
                for line in lines:
                    if not line.startswith('!') and not line.startswith('##'):
                        yield line

            raw_rules = []
            for url in block_ads_lists:
                raw_rules.extend(requests.get(url).text.splitlines())
            raw_rules = remove_comments_and_html_elements(raw_rules)
            raw_rules = list(set(raw_rules))
            return AdblockRules(raw_rules)

        spm_options = kwargs.pop('spm_options', {})

        self.spm_host = spm_options.get('spm_host', DEFAULT_SPM_HOST)
        self.spm_apikey = spm_options.get('spm_apikey', None)
        put_proxy_into_kwargs_seleniumwire_options(kwargs, self.spm_apikey, self.spm_host)

        self.static_bypass = spm_options.get('static_bypass', DEFAULT_STATIC_BYPASS)
        static_bypass_regex = spm_options.get('static_bypass_regex', DEFAULT_STATIC_BYPASS_REGEX)
        self.static_bypass_regexobj = re.compile(static_bypass_regex)

        self.static_domains = spm_options.get('static_domains', DEFAULT_STATIC_DOMAINS)
        self.static_domains_list = spm_options.get('static_domains_list', DEFAULT_STATIC_DOMAINS_LIST)
        self.static_domains_block = spm_options.get('static_domains_block', DEFAULT_STATIC_DOMAINS_BLOCK)

        self.block_ads = spm_options.get('block_ads', DEFAULT_BLOCK_ADS)
        block_ads_lists = spm_options.get('block_ads_lists', DEFAULT_BLOCK_ADS_LISTS)
        self.block_ads_rules = fetch_adblock_rules(block_ads_lists)

        self.spm_headers = spm_options.get('headers', DEFAULT_HEADERS)

        self.spm_session_id = self.create_spm_session()

        super_obj.__init__(*args, **kwargs)

        self.user_request_interceptor = None
        self.user_response_interceptor = None
        self.backend.request_interceptor = self.zyte_request_interceptor
        self.backend.response_interceptor = self.zyte_response_interceptor

    def zyte_request_interceptor(self, request):
        if self.user_request_interceptor is not None:
            self.user_request_interceptor(request)

        if self.block_ads and self.block_ads_rules.should_block(request.url):
            request.abort()

        if self.static_domains_list > 0:

            for _domain in self.static_domains_list:

                if self.static_domains_block and (_domain in request.url):
                    request.abort()

                if self.static_domains and (_domain in request.url):

                    try:
                        r = requests.get(request.url, headers=request.headers)
                        if r.status_code == 200:
                            request.create_response(
                                status_code=r.status_code,
                                headers=r.headers.items(),
                                body=r.content
                            )
                    except Exception:
                        pass

        if (
            self.static_bypass and
            self.static_bypass_regexobj.match(request.url)
        ):
            try:
                r = requests.get(request.url, headers=request.headers)
                if r.status_code == 200:
                    request.create_response(
                        status_code=r.status_code,
                        headers=r.headers.items(),
                        body=r.content
                    )
            except Exception:
                pass

        for key, value in self.spm_headers.items():
            del request.headers[key]
            request.headers[key] = value
        request.headers['X-Crawlera-Session'] = self.spm_session_id
        request.headers['X-Crawlera-Client'] = ZYTE_SPM_SELENIUM_VERSION

    def zyte_response_interceptor(self, request, response):
        if response.headers.get('X-Crawlera-Error', '') == 'bad_session_id':
            self.spm_session_id = self.create_spm_session()

        if self.user_response_interceptor is not None:
            self.user_response_interceptor(request, response)

    def create_spm_session(self):
        r = requests.post(
            f'{self.spm_host}/sessions',
            auth=(self.spm_apikey, ''),
            headers={'X-Crawlera-Client': ZYTE_SPM_SELENIUM_VERSION}
        )
        return r.text

    @property
    def request_interceptor(self) -> callable:
        """A callable that will be used to intercept/modify requests.
        The callable must accept a single argument for the request
        being intercepted.
        """
        return self.user_request_interceptor

    @request_interceptor.setter
    def request_interceptor(self, interceptor: callable):
        self.user_request_interceptor = interceptor

    @request_interceptor.deleter
    def request_interceptor(self):
        self.user_request_interceptor = None

    @property
    def response_interceptor(self) -> callable:
        """A callable that will be used to intercept/modify responses.
        The callable must accept two arguments: the response being
        intercepted and the originating request.
        """
        return self.user_response_interceptor

    @response_interceptor.setter
    def response_interceptor(self, interceptor: callable):
        if len(inspect.signature(interceptor).parameters) != 2:
            raise RuntimeError('A response interceptor takes two parameters: the request and response')
        self.user_response_interceptor = interceptor

    @response_interceptor.deleter
    def response_interceptor(self):
        self.user_response_interceptor = None


class Firefox(ZyteModifyRequestsMixin, _Firefox):
    def __init__(self, *args, **kwargs):
        self.zyte_init(super(), *args, **kwargs)


class Chrome(ZyteModifyRequestsMixin, _Chrome):
    def __init__(self, *args, **kwargs):
        self.zyte_init(super(), *args, **kwargs)


class Safari(ZyteModifyRequestsMixin, _Safari):
    def __init__(self, *args, **kwargs):
        self.zyte_init(super(), *args, **kwargs)


class Edge(ZyteModifyRequestsMixin, _Edge):
    def __init__(self, *args, **kwargs):
        self.zyte_init(super(), *args, **kwargs)


class Remote(ZyteModifyRequestsMixin, _Remote):
    def __init__(self, *args, **kwargs):
        self.zyte_init(super(), *args, **kwargs)
