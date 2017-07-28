from .web_photo import WebPhoto
from .web_article import WebArticle
from spiders.utils import get_soup_from_url


def get_article_ids_in_page(page_num):
    soup = get_soup_from_url('article/list/?page={}'.format(page_num))
    article_ids = []
    for i in soup.select('a.list-group-item'):
        article_ids.append(i['href'].split('/')[-1])
    return article_ids


def get_standalone_photo_ids_in_page(page_num):
    soup = get_soup_from_url('photo/list/?page={}'.format(page_num))
    photo_ids = []
    for i in soup.select('a.col-xs-6.col-sm-3'):
        photo_ids.append(i['href'].split('/')[-1])
    return photo_ids


def get_max_page_num(url='article/list/'):
    soup = get_soup_from_url(url)
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


def update_standalone_photos():
    max_page_num = get_max_page_num('photo/list/')
    print(max_page_num)
    for i in range(max_page_num, 0, -1):
        photo_ids = get_standalone_photo_ids_in_page(i)
        for photo_id in photo_ids:
            photo = WebPhoto(old_id=photo_id)
            photo.save()


def update_standalone_photos_incremental():
    max_page_num = get_max_page_num()

    for i in range(1, max_page_num+1):
        photo_ids = get_standalone_photo_ids_in_page(i)

        at_least_one_photo_in_db = False

        for photo_id in photo_ids:
            photo = WebPhoto(old_id=photo_id)
            r = photo.save()

            if not r:
                at_least_one_photo_in_db = True

        if at_least_one_photo_in_db:
            print('This page contains cached photos, skip the rest pages')
            break
