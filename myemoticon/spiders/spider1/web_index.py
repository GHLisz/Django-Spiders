from .web_photo import WebPhoto
from .web_article import WebArticle
from spiders.utils import get_soup_from_url
from spiders.utils import error_list_logger
from emoticon.models import Photo, Article


def get_article_ids_in_page(page_num):
    soup = get_soup_from_url('article/list/?page={}'.format(page_num))
    article_ids = []
    for i in soup.select('a.list-group-item'):
        article_ids.append(i['href'].split('/')[-1])
    return article_ids


def get_max_page_num():
    soup = get_soup_from_url('article/list/')
    return int(soup.select('ul.pagination > li > a')[-2].get_text())


def update_articles():
    max_page_num = get_max_page_num()

    for i in range(max_page_num, 0, -1):
        article_ids = get_article_ids_in_page(i)
        print('len article_ids:', len(article_ids))
        for article_id in article_ids:
            article = WebArticle(article_id)
            article.save()

            photo_ids = article.photo_ids()
            for photo_id in photo_ids:
                photo = WebPhoto(old_id=photo_id, article_old_id=article.old_id)
                photo.save()


def update_articles_incremental():
    max_page_num = get_max_page_num()

    for i in range(1, max_page_num+1):
        article_ids = get_article_ids_in_page(i)

        at_least_one_article_in_db = False

        for article_id in article_ids:
            article = WebArticle(article_id)
            r = article.save()

            if not r:
                at_least_one_article_in_db = True

            photo_ids = article.photo_ids()
            print('photo ids: ', photo_ids)
            for photo_id in photo_ids:
                photo = WebPhoto(old_id=photo_id, article_old_id=article.old_id)
                photo.save()

        if at_least_one_article_in_db:
            print('This page contains cached articles, skip the rest pages')
            break
