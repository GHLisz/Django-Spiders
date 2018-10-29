import unittest
from spiders.spider1 import web_show


suite = unittest.TestLoader().loadTestsFromModule(web_show)
unittest.TextTestRunner(verbosity=2).run(suite)
