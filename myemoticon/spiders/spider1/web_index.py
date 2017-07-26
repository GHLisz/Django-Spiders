from .web_photo import WebPhoto
from .web_article import WebArticle
from spiders.utils import get_soup_from_url
from spiders.utils import error_list_logger


def get_article_ids_in_page(page_num):
    soup = get_soup_from_url('article/list/?page={}'.format(page_num))
    article_ids = []
    for i in soup.select('a.list-group-item'):
        article_ids.append(i['href'].split('/')[-1])
    return article_ids


def update_articles():
    soup = get_soup_from_url('article/list/')
    max_page_num = int(soup.select('ul.pagination > li > a')[-2].get_text())

    for i in range(max_page_num, 0, -1):
        article_ids = get_article_ids_in_page(i)
        for article_id in article_ids:
            article = WebArticle(article_id)
            article.save()
            photo_ids = article.photo_ids()
            for photo_id in photo_ids:
                try:
                    photo = WebPhoto(old_id=photo_id, article_old_id=article.old_id)
                    photo.save()
                except:
                    error_list_logger.info('Error occurred processing photo: {} in article {}'.
                                           format(photo_id + article_id, '; update_articles'))
