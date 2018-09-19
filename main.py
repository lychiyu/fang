# coding: utf-8

"""
 Created by liuying on 2018/9/19.
"""

import sys, os
from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'fang_tx'])