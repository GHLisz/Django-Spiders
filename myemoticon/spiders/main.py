from spiders.spider1.web_photo import *
from spiders.spider1.web_index import *
import unittest
import sys
from spiders.spider1.down_pic import *


if __name__ == '__main__':
    # unittest.main()
    # get_article_ids_in_page(2)
    update_standalone_photos()
    save_pic_job_multi()
