import requests
from urllib.parse import urlencode
from fake_useragent import UserAgent

from utils import getAmazonDomain

REVIEWSURL = '{domain}/product-reviews/{asin}/ref=cm_cr_arp_d_viewopt_srt'

reviewParam = {
    'ie': 'UTF8',
    'reviewerType': 'all_reviews',
    'sortBy': 'recent',
    'pageNumber': ''
}


class AmazonRequests:
    def __init__(self, country, asin):
        self.session = requests.Session()
        self.ASIN = asin
        self.Country = country
        self.page = 1
        self.retryNum = 0
        self.referer = getAmazonDomain(self.Country)
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3',
            'user-agent': UserAgent().random,
            # 'Host': getAmazonDomain(self.Country),
            'referer': '',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'upgrade-insecure-requests': '1',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'Connection': 'keep-alive'
        }

    def getURL(self):
        return REVIEWSURL.format(domain=getAmazonDomain(self.Country), asin=self.ASIN)

    def nextPage(self):
        self.page += 1

    def getPage(self):
        return self.page

    def getAmaoznData(self, is_lang=False):
        try:
            reviewParam['pageNumber'] = str(self.getPage())
            if is_lang and self.Country == 'US':
                reviewParam['filterByLanguage'] = 'en_US'
            self.headers['referer'] = self.referer
            response = self.session.get(self.getURL(), params=reviewParam, headers=self.headers, timeout=(5, 10))
            response.encoding = 'utf-8'
            self.referer = '%s?%s' % (self.getURL(), urlencode(reviewParam))
            if response.status_code == 200:
                return response.text
            else:
                return response.status_code
        except requests.exceptions.RequestException as e:
            if self.retryNum == 2:
                print(e)
                return self.retryNum
            self.retryNum += 1
            return self.getAmaoznData()
