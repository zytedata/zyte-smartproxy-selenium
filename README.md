# Zyte SmartProxy Selenium

Use [Selenium](https://www.selenium.dev/) and [Selenium Wire](https://github.com/wkeeling/selenium-wire) with
[Smart Proxy Manager](https://www.zyte.com/smart-proxy-manager/) easily!

A wrapper over Selenium Wire to provide Zyte Smart Proxy Manager specific functionalities.

## QuickStart

1. **Install using pip**

```
python3 -m pip install zyte-smartproxy-selenium
```

If you get an error about not being able to build cryptography you may be running an old version of pip. Try upgrading pip with `python -m pip install --upgrade pip` and then re-run the above command.

2. **Browser Setup**

No specific configuration should be necessary except to ensure that you have downloaded the [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) and [GeckoDriver](https://github.com/mozilla/geckodriver/releases) for Chrome and Firefox to be remotely controlled, the same as if you were using Selenium directly. Once downloaded, these executables should be placed somewhere on your PATH.

3. **Create a file `sample.py` with the following content and replace `<SPM_APIKEY>` with your SPM Apikey**

``` python
from zyte_smartproxy_selenium import webdriver

browser = webdriver.Chrome(spm_options={'spm_apikey': '<SPM_APIKEY>'})
browser.get('https://toscrape.com')
browser.save_screenshot('screenshot.png')
browser.close()
```

Make sure that you're able to make `https` requests using Smart Proxy Manager by following this guide [Fetching HTTPS pages with Zyte Smart Proxy Manager](https://docs.zyte.com/smart-proxy-manager/next-steps/fetching-https-pages-with-smart-proxy.html)

For sub-packages of webdriver, you should continue to import these directly from selenium or seleniumwire.

4. **Run `sample.py` using Python**

``` bash
python3 sample.py
```

## API

Zyte SmartProxy Selenium extends Selenium Wire. You author your code in the same way as you do with Selenium Wire and Selenium, but you get extra `spm_options` argument with options specific for Zyte Smart Proxy Manager:

| Argument | Default Value | Description |
|----------|---------------|-------------|
| `spm_apikey` | `undefined` | Zyte Smart Proxy Manager API key that can be found on your zyte.com account. |
| `spm_host` | `http://proxy.zyte.com:8011` | Zyte Smart Proxy Manager proxy host. |
| `static_bypass` | `true` | When `true` Zyte SmartProxy Selenium will skip proxy use for static assets defined by `static_bypass_regex` or pass `false` to use proxy. |
| `static_bypass_regex` | `/.*?\.(?:txt\|json\|css\|less\|gif\|ico\|jpe?g\|svg\|png\|webp\|mkv\|mp4\|mpe?g\|webm\|eot\|ttf\|woff2?)$/` | Regex to use filtering URLs for `static_bypass`. |
| `block_ads` | `true` | When `true` Zyte SmartProxy Selenium will block ads defined by `block_ads_lists`. |
| `block_ads_lists` | `['https://easylist.to/easylist/easylist.txt', 'https://easylist.to/easylist/easyprivacy.txt']` | [AdBlock lists](https://adblockplus.org/filter-cheatsheet) to be used by Zyte SmartProxy Selenium to block ads |
| `headers` | `{'X-Crawlera-No-Bancheck': '1', 'X-Crawlera-Profile': 'pass', 'X-Crawlera-Cookies': 'disable'}` | List of headers to be appended to requests |

### Notes
Some websites may not work with `block_ads` and `static_bypass` enabled (default). Try to disable them if you encounter any issues.