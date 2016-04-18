from scrapy import cmdline
from scrapy import signals
import logging
from twisted.internet import reactor
from scrapy.crawler import Crawler
from reflected_xss_scanner.spiders.crawlerrule import CrawlerRule
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from reflected_xss_scanner.spiders.config import config
from reflected_xss_scanner.spiders.crawler import crawler
from reflected_xss_scanner.spiders.json_file_writer import json_file_writer
from reflected_xss_scanner.spiders.result_db import result_db
import json
import sys

logger = logging.getLogger(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')
process = CrawlerProcess(get_project_settings())
configure_logging()
Config = config()
websites = Config.getConfig().items('crawler')
for domain,website_list in websites:
    print("site list info: "+website_list)
    website_list_json = json.loads(website_list)
    for website in website_list_json:
        print("--------------------------------------------------------")
        print("crawling websites: " + domain)
        print("-----------------------starting-------------------------")
        rule = CrawlerRule()
        rule.name = domain
        rule.allowed_domains = [domain]
        rule.start_urls = website[0]
        if len(website) > 2:
            print("start login crawler...")
            rule.login_url = website[1]
            rule.user = website[2]
            rule.password = website[3]
        process.crawl(crawler(rule),rule)

process.start()

print("-----------------------exporting-------------------------")

json_file_writer.write_json("JSON_1.txt", result_db.get_result())

print("-----------------------finished-------------------------")