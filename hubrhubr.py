import requests
import io
import json
from bs4 import BeautifulSoup

url = 'https://habr.com/'

# Получим html страницу
def get_html(url):
    r = requests.get(url)

    return r.text

# Получим все ссылки постов и их названия на главной странцие
def get_all_posts(html):
        soup = BeautifulSoup(html, features="html.parser")
        a_posts = soup.find_all('a', class_='post__title_link')
        link_posts = []

        for link_post in a_posts:
            link_posts.append({"name_article": str(link_post.text), 'link': link_post.get('href')})

        return link_posts

# Получим ключевые слова под каждым постом
def get_all_keywords(html):
    soup = BeautifulSoup(html, features="html.parser")
    ul_keywords = soup('ul', class_="post__hubs inline-list")

    list_ = []

    for ul in ul_keywords:
        li = (ul.find_all('li', class_='inline-list__item_hub'))
        list_li_keywords = []

        for a in li:
            list_li_keywords.append(str(a.find('a', class_="hub-link").text))

        list_.append(list_li_keywords)

    return list_

def get_name_author_article(html):
    list_name_author = []
    soup = BeautifulSoup(html, features="html.parser")
    name_all = soup.find_all('span', class_='user-info__nickname')

    for name in name_all:
        list_name_author.append(name.text)

    return list_name_author

# Получаем текст кажого поста
def get_all_text_article(html):
    link_posts = get_all_posts(get_html(url))
    text = []

    for post in link_posts:
        html_post = get_html(post['link'])
        soup = BeautifulSoup(html_post, features='html.parser')
        text.append({'text': soup.find('div', class_="comment__message ")})

    return text

def merge_dir(link_posts, list_, name_authors):
    for index, post in enumerate(link_posts):
        post.update({'keywords': list_[index]})
        post.update({'name_author': name_authors[index]})

# Запишем словарь в файл JSON
def write_json(data):
    with io.open('data_hubr_hubr.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(str_)

link_posts = get_all_posts(get_html(url))
list_ = get_all_keywords(get_html(url))
name_authors = get_name_author_article(get_html(url))
merge_dir(link_posts, list_, name_authors)
write_json(link_posts)



