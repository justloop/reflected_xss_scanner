import urllib

import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.http import FormRequest, Request
from reflected_xss_scanner.spiders.crawlerrule import CrawlerRule
from urlparse import urlparse, urlsplit,parse_qs,urljoin
from os.path import splitext
from reflected_xss_scanner.spiders.process_login import fill_login_form
import lxml.etree
import time
from reflected_xss_scanner.spiders.result_db import result_db
from reflected_xss_scanner.spiders.swf_parser import swf_parser
from reflected_xss_scanner.spiders.config import config
from BeautifulSoup import BeautifulSoup
import json
from ConfigParser import NoOptionError



class crawler(scrapy.Spider):
    name = 'crawler'
    handle_httpstatus_list = [500]
    link_extractor = LinkExtractor()
    rules = (Rule(link_extractor, callback='parse', follow=True),)
    not_allowed = [".css"]
    allowed_domains=[]

    def __init__(self, rule=CrawlerRule()):
        super(crawler, self).__init__(self)
        self.urls_visited = []
        self.post_urls_visited = []
        self.rule = rule
        self.name = rule.name
        self.allowed_domains = rule.allowed_domains
        self.start_urls = rule.start_urls
        self.login_url = rule.login_url
        self.put_headers = False

        # Login details
        self.login_user = self.rule.user
        if self.login_user == 'None':
            self.login_user = None
        else:
            self.login_pass = self.rule.password
        self.http_user = self.login_user
        self.http_pass = self.login_pass
        Config = config()
        try:
            ignore_string = Config.getConfig().get('forward_ignore', self.allowed_domains[0])
            self.ignore_params = False
        except NoOptionError:
            self.ignore_params = True
            ignore_string = "[]"

        self.ignore_fields = json.loads(ignore_string)
        self.log(ignore_string)


    def start_requests(self):
        if self.login_user and self.login_pass:
                yield Request(url=self.login_url, callback=self.login)
        else:
            for start_url in self.start_urls:
                if (";" in start_url):
                    split_arr = start_url.split(';')
                    validated_url = split_arr[0]
                    yield Request(url=validated_url, dont_filter=True, callback=self.parse_res)
                    time.sleep(int(split_arr[1]))

                else:
                    validated_url = start_url
                    yield Request(url=validated_url, dont_filter=True, callback=self.parse_res)

                real_url = urlsplit(validated_url)
                if len(real_url.query) > 0 and self.get_ext(real_url.path) not in self.not_allowed:
                    # only add to result if have parameters
                    param_dict = parse_qs(real_url.query, keep_blank_values=True)
                    result_db.add_to_result("GET", real_url.path, list(param_dict.keys()))
                if self.ignore_params:
                    tag_url = real_url.scheme + "://" + real_url.hostname + real_url.path
                else:
                    tag_url = validated_url
                    for param in self.ignore_fields:
                        if param in real_url.query:
                            tag_url = real_url.path
                if tag_url not in self.urls_visited and self.get_ext(real_url.path) not in self.not_allowed:
                    self.urls_visited.append(tag_url)


    def login(self, response):
        self.log('Logging in...')
        try:
            full_args, args, url, method, params = fill_login_form(response.url, response.body, self.login_user, self.login_pass)
            validated_url = self.url_valid(url, response.url)
            real_url = urlsplit(validated_url)
            result_db.add_to_result(method.upper(), real_url.scheme + "://" + real_url.hostname + real_url.path,
                                    list(dict(full_args).keys()))
            yield FormRequest(validated_url,
                               method=method,
                               formdata=args,
                               callback=self.confirm_login,
                               dont_filter=True)
        except Exception as e:
            print(e)
            self.log('Login failed')
            for start_url in self.start_urls:
                if (";" in start_url):
                    split_arr = start_url.split(';')
                    validated_url = split_arr[0]
                    yield Request(url=validated_url, dont_filter=True, callback=self.parse_res)
                    time.sleep(int(split_arr[1]))

                else:
                    validated_url = start_url
                    yield Request(url=validated_url, dont_filter=True, callback=self.parse_res)

                real_url = urlsplit(validated_url)
                if len(real_url.query) > 0 and self.get_ext(real_url.path) not in self.not_allowed:
                    # only add to result if have parameters
                    param_dict = parse_qs(real_url.query, keep_blank_values=True)
                    result_db.add_to_result("GET", real_url.path, list(param_dict.keys()))
                if self.ignore_params:
                    tag_url = real_url.scheme + "://" + real_url.hostname + real_url.path
                else:
                    tag_url = validated_url
                    for param in self.ignore_fields:
                        if param in real_url.query:
                            tag_url = real_url.path
                if tag_url not in self.urls_visited and self.get_ext(real_url.path) not in self.not_allowed:
                    self.urls_visited.append(tag_url)

    def confirm_login(self, response):
        ''' Check that the username showed up in the response page '''
        for start_url in self.start_urls:
            if(";" in start_url):
                for start_url in self.start_urls:
                    if (";" in start_url):
                        split_arr = start_url.split(';')
                        validated_url = split_arr[0]
                        yield Request(url=validated_url, dont_filter=True, callback=self.parse_res)
                        time.sleep(int(split_arr[1]))

                    else:
                        validated_url = start_url
                        yield Request(url=validated_url, dont_filter=True, callback=self.parse_res)

                    real_url = urlsplit(validated_url)
                    if len(real_url.query) > 0 and self.get_ext(real_url.path) not in self.not_allowed:
                        # only add to result if have parameters
                        param_dict = parse_qs(real_url.query, keep_blank_values=True)
                        result_db.add_to_result("GET", real_url.path, list(param_dict.keys()))
                    if self.ignore_params:
                        tag_url = real_url.scheme + "://" + real_url.hostname + real_url.path
                    else:
                        tag_url = validated_url
                        for param in self.ignore_fields:
                            if param in real_url.query:
                                tag_url = real_url.path
                    if tag_url not in self.urls_visited and self.get_ext(real_url.path) not in self.not_allowed:
                        self.urls_visited.append(tag_url)
            else:
                yield Request(url=start_url, dont_filter=True, callback=self.parse_res)
        if self.login_user.lower() in response.body.lower():
            self.log('Successfully logged in...')
            yield Request(url=response.url, dont_filter=True, callback=self.parse_res)
        else:
            self.log('login failed')

    def parse(self, response):
        start_url = urlparse(response.url)
        self.base_url = start_url.scheme + '://' + start_url.netloc
        self.parse_res(response)

    def url_processor(self, url):
        try:
            parsed_url = urlparse(url)
            path = parsed_url.path
            protocol = parsed_url.scheme + '://'
            hostname = parsed_url.hostname
            netloc = parsed_url.netloc
            doc_domain = '.'.join(hostname.split('.')[-2:])
        except:
            self.log('Could not parse url: ' + url)
            return

        return (netloc, protocol, doc_domain, path)

    def http_normalize_repeat_domain(self, url):
        url = str(url)
        match = re.search("^http.*?\/\/([^/]+)/([^/]+)/.*?$", url)
        if match is not None and match.group(1) == match.group(2):
            return url.replace(match.group(1), "", 1)
        else:
            return url

    def http_normalize_slashes(self,url):
        normalized_url = url.replace("///","//")
        return normalized_url

    def url_valid(self, url, orig_url):
        if url.startswith("http"):
            url = self.http_normalize_slashes(self.http_normalize_repeat_domain(url))

            (netloc1, protocol1, doc_domain1, path1) = self.url_processor(url)
            (netloc2, protocol2, doc_domain2, path2) = self.url_processor(orig_url)
            if doc_domain1 != doc_domain1:
                return
        return_url = urljoin(orig_url,url)
        if return_url.startswith("http"):
            return return_url

    def parse_res(self, response):
        response_url = urlparse(response.url)
        try:
            doc = lxml.html.fromstring(response.body, base_url=response.url)
        except Exception:
            return

        normalized_page = BeautifulSoup(unicode(response.body, errors='replace'))

        #get all the forms
        forms = normalized_page.findAll('form')
        if forms:
           self.extract_forms(response_url, forms)

        #get all src url
        for src_tag in normalized_page.findAll(src=True):
            src_url = src_tag['src']
            if src_url:
                validated_url = self.url_valid(src_url, response.url)
                if validated_url and self.get_ext(validated_url) == '.swf':
                    yield Request(url=validated_url, callback=self.parse_swf)
                elif validated_url and self.get_ext(validated_url) == '.js':
                    yield Request(url=validated_url, callback=self.get_forms)
                elif validated_url and self.get_ext(validated_url) in ['.php','.jsp','']:
                    yield Request(url=validated_url, callback=self.parse_res)


        # extract all the get urls
        for anchor in normalized_page.findAll(href=True):
            validated_url = self.url_valid(anchor['href'],response.url)
            if validated_url is not None:
                real_url = urlsplit(validated_url)
                if real_url.scheme == 'mailto':
                    continue
                if len(real_url.query) > 0 and self.get_ext(real_url.path) not in self.not_allowed:
                    # only add to result if have parameters
                    param_dict = parse_qs(real_url.query, keep_blank_values=True)
                    result_db.add_to_result("GET", self.url_valid(real_url.path,response.url),
                                            list(param_dict.keys()))
                if self.ignore_params:
                    tag_url = real_url.scheme+"://"+real_url.hostname+real_url.path
                else:
                    tag_url = validated_url
                    for param in self.ignore_fields:
                        if param in real_url.query:
                            tag_url = real_url.path
                if tag_url not in self.urls_visited and self.get_ext(real_url.path) not in self.not_allowed:
                    self.urls_visited.append(tag_url)
                    if "logout" not in validated_url:
                        yield Request(validated_url, callback=self.parse_res)

        #get forms from javascript
        self.get_forms(response)

        #get headers
        if not self.put_headers:
            headers = []
            for headerName, headerValue in response.headers.iteritems():
                headers.append(headerName)
            result_db.add_to_result("HEADERS",response.url,list(headers))
            self.put_headers = True

    def get_urls(self,response):
        # find get urls:
        urls = re.search("^http.*?\/\/.*?$", response)
        return urls


    def get_forms(self,response):
        """ Extracting the forms from the website """
        #pattern 1
        forms = re.findall(
            """<form.*?action=('(.*?)'|"(.*?)").*?method=('(.*?)'|"(.*?)").*?>(.*?)</form>""", response.body,
            re.DOTALL)  # Parse forms
        for form in forms:  # Scan each form
            params = self.scan(form)
            if len(form[1]) > 0:
                action = re.sub('[ +\'"]', '', form[1])
            else:
                action = re.sub('[ +\'"]', '', form[2])

            if len(form[4]) > 0:
                method = re.sub('[ +\'"]', '', form[4])
            else:
                method = re.sub('[ +\'"]', '', form[5])

            validated_url = self.url_valid(action, response.url)

            if validated_url and (validated_url not in self.post_urls_visited):
                self.post_urls_visited.append(validated_url)

                result_db.add_to_result(method.upper(), validated_url, params)

        # pattern 2
        forms2 = re.findall(
            """<form.*?method=('(.*?)'|"(.*?)").*?action=('(.*?)'|"(.*?)").*?>(.*?)</form>""", response.body,
            re.DOTALL)  # Parse forms
        for form in forms2:  # Scan each form
            params = self.scan(form)
            if len(form[1]) > 0:
                method = re.sub('[ +\'"]', '', form[1])
            else:
                method = re.sub('[ +\'"]', '', form[2])

            if len(form[4]) > 0:
                action = re.sub('[ +\'"]', '', form[4])
            else:
                action = re.sub('[ +\'"]', '', form[5])

            validated_url = self.url_valid(action, response.url)
            if validated_url is not None and (validated_url not in self.post_urls_visited):
                self.post_urls_visited.append(validated_url)

                result_db.add_to_result(method.upper(), validated_url, params)




    def scan(self, form):
        """ Gather all the data required and send it to the website """
        inputs = re.findall("""<input.*?name=['|"](.*?)['|"].*?>""", form[6])  # Extract all the required parameters from the webpage
        textareas = re.findall("""<textarea.*?name=['|"](.*?)['|"].*?>""",form[6])
        selects = re.findall("""<select.*?name=['|"](.*?)['|"].*?>""",form[6])
        params = set()
        for input in inputs:
            params.add(input)
        for textarea in textareas:
            params.add(textarea)
        for select in selects:
            params.add(select)

        return list(params)

    def get_ext(self,url):
        parsed = urlparse(self.http_normalize_slashes(url))
        root, ext = splitext(parsed.path)
        return ext

    def parse_swf(self,response):
        flash_parser = swf_parser(response.body)
        swf_links = flash_parser.getLinks()
        for link in swf_links:
            validated_url = self.url_valid(link, response.url)
            if validated_url is not None:
                real_url = urlsplit(validated_url)
                if self.ignore_params:
                    tag_url = real_url.scheme+"://"+real_url.hostname+real_url.path
                else:
                    tag_url = validated_url
                    for param in self.ignore_fields:
                        if param in real_url.query:
                            tag_url = real_url.path
                if tag_url not in self.urls_visited and self.get_ext(real_url.path) not in self.not_allowed:
                    self.urls_visited.append(tag_url)
                    if len(real_url.query) > 0:
                        # only add to result if have parameters
                        param_dict = parse_qs(real_url.query, keep_blank_values=True)
                        result_db.add_to_result("GET", self.url_valid(real_url.path,response.url),
                                                param_dict.keys())
                    if "logout" not in validated_url:
                        yield Request(validated_url, callback=self.parse_res)

    def extract_forms(self,response_url,forms):
        for form in forms:
            #special case when table is the parent, because part of table is not allowed to be inside form
            method = form.get('method')
            form_url = form.get('action')
            if form.parent and form.parent.name == 'table':
                params = self.extract_form_fields(form.parent)
            else:
                params = self.extract_form_fields(form)
            if params:
                if method and form_url:
                    validated_url = self.url_valid(form_url, response_url.geturl())
                    if validated_url and (validated_url not in self.post_urls_visited):
                        self.post_urls_visited.append(validated_url)

                        result_db.add_to_result(method.upper(),validated_url, params)
            #else:
            #   validated_url = self.url_valid(form_url, response_url.geturl())
            #   real_url = urlsplit(validated_url)
            #   if len(real_url.query) > 0:
            #       # only add to result if have parameters
            #       param_dict = parse_qs(real_url.query, keep_blank_values=True)
            #       result_db.add_to_result("GET", self.url_valid(real_url.path, response_url.geturl()),
            #                              list(param_dict.keys()))

    def extract_form_fields(self, soup):
        params = set()
        for input in soup.findAll('input'):
            if not input.has_key('type'):
                continue
            if input['type'] in ('submit', 'image') and not input.has_key('name'):
                continue

            if input['type'] in ('text', 'hidden', 'password', 'submit', 'image', 'file','checkbox', 'radio'):
                if input.has_key('name'):
                    params.add(input['name'])
                continue

        for textarea in soup.findAll('textarea'):
            if textarea.has_key('name'):
                params.add(textarea['name'])

        for select in soup.findAll('select'):
            if select.has_key('name'):
                params.add(select['name'])

        return list(params)