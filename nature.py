import requests
import json
import io
from bs4 import BeautifulSoup
import os
from neo import create_nodes_article, create_nodes_author, create_relationship, create_node_ref_art
from save_files import save_article, save_article_name

BASE_URL = 'https://www.nature.com/'

# Получим html страницу
def get_html(url):
    r = requests.get(url)

    return r.text

# Получим блок For Reader
def get_block_for_reader(html):
    soup = BeautifulSoup(html, features="html.parser")
    block_for_reader = soup.find('div', class_='grid grid-3 mq875-grid-4 mq640-grid-6 mq480-grid-12 mb20 just-mq640-last')\
        .find('ul', class_='clean-list ma0 mt10 mb6').\
        find_all('li', class_='pb4')

    return block_for_reader

# Получим журналы, которые публикуются в nature
def get_all_journals(html):
    block_for_reader = get_block_for_reader(html)
    link_journals = block_for_reader[0].find('a').get('href')
    htmls_journals = get_html(link_journals)
    soup = BeautifulSoup(htmls_journals, features="html.parser")
    divs = soup.find_all('div', class_='cleared pt40 pb20 ma0 border-gray-medium border-bottom-1')
    list_journals = []

    for div in divs:
        li_s = div.find_all('li')

        for li in li_s:
            list_journals.append('www.nature.com' + li.find('a').get('href'))

    return list_journals

# Получим все темы
def get_all_subject_pages(html):
    block_for_reader = get_block_for_reader(html)
    link_subject_pages = block_for_reader[1].find('a').get('href')
    html_subject_pages = get_html(link_subject_pages)
    soup = BeautifulSoup(html_subject_pages, features="html.parser")
    sections_names = soup.find_all('div', class_='container cleared container-type-link-grid')
    subject_section = []

    for section in sections_names:
        sec = section.find('section', class_='position-relative')
        name = sec.find('h2').text
        all_links_in_section = sec.find_all('a')

        links = []
        for link in all_links_in_section:
            links.append({'link': 'https://www.nature.com' + link.get('href'), 'name': link.text})

        subject_section.append({'name_page': name, 'links': links})

    return subject_section

# Получим ссылки на статьи из раздела Latest Research
def get_links_latest_research(html):
    soup = BeautifulSoup(html, features="html.parser")
    link_more_latest_research = 'https://www.nature.com' +\
                                soup.find('div', class_='position-absolute mt-negative-20 position-left grid grid-12 last text-center').find('a').get('href')
    html_latest_research = get_html(link_more_latest_research)
    soup = BeautifulSoup(html_latest_research, features="html.parser")
    list_article = soup.find_all('article')
    atricles = []

    for article in list_article:
        link = article.find('a').get('href')
        atricles.append('https://www.nature.com' + link)

    return atricles

# Возвращает информацию о статье
def get_info_article(url):
    html_page_article = get_html(url)
    soup = BeautifulSoup(html_page_article, features="html.parser")

    try:
        name_article = soup.find('h1', itemprop='name headline').text
    except:
        return

    try:
        date = soup.find('time').text
    except:
        return

    author_lists_links = soup.find_all('li', itemprop='author')
    authors = []

    for author in author_lists_links:
        authors.append(author.find('span', itemprop='name').text)

    subject_article = []
    sub = []

    try:
        subjects = soup.find_all('a', class_='subject-tag-link-steelblue mr2 mb2')
    except:
        return

    for subject in subjects:
        subject_article.append({'name':subject.text, 'link':'https://www.nature.com' + subject.get('href')})
        sub.append(subject.text)

    try:
        doi_article_link = soup.find('p', class_='standard-space-below text14').find('a').text
        doi_split = doi_article_link.split('/')
        doi = doi_split[3] + '/' + doi_split[4]
    except:
        return

    total_info_artile = {'name': name_article, 'date': date, 'authors': authors, 'subjects': sub, 'doi': doi}

    return total_info_artile

# Запишем словарь в файл JSON
def write_json(data, path):
    with io.open(path, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(str_)

def get_info_all_article_latest_research():
    all_links_article = get_links_latest_research(get_html(BASE_URL))
    os.mkdir(path='article_latest_research')

    for (index, article) in enumerate(all_links_article):
        info_article = get_info_article(article)
        os.mkdir(path='article_latest_research' + '/' + 'article_' + str(index))

        write_json(info_article, 'article_latest_research'
                   + '/' + 'article_' + str(index)
                   + '/' + 'article_' + str(index)
                   + '.json')

        save_article(info_article['doi'])
        create_nodes_article(info_article['name'], info_article['doi'], info_article['authors'], info_article['date'], info_article['subjects'])

def get_link_subject(subject):
    subjects_pages = get_all_subject_pages(get_html(BASE_URL))

    for subjects in subjects_pages:
        links = subjects['links']

        for link in links:
            if subject == link['name']:
                return link['link']

# Получить все ссылки на статьи которые указаны в поле Reference
def get_references_links(link):
    soup = BeautifulSoup(get_html(link), features="html.parser")
    li_s = soup.find_all('li', class_='small-space-below border-gray-medium border-bottom-1 position-relative js-ref-item')

    ref = []
    for li in li_s:
        link = li.find('li', class_='pin-right').find('a')
        if link is not None:
            ref.append(link.get('href'))

    return ref

def get_references_name_artricles(link):
    soup = BeautifulSoup(get_html(link), features="html.parser")
    li_s = soup.find_all('li', class_='small-space-below border-gray-medium border-bottom-1 position-relative js-ref-item')
    names=[]
    links=[]

    for name in li_s:
        names.append(name.find('p').text)
        li = name.find('li', class_='pin-right')

        if li is not None:
            link = li.find('a')

        if link is not None:
            links.append(link.get('href'))
        else:
            links.append("---")

    return (names, links)

# Получим все встатьи через поисковый запрос в журнал nature
def get_articles_subject_pages(subject):
    link_start_page = 'https://www.nature.com/search?article_type=protocols,research,reviews&subject=' + subject
    link_next_page = link_start_page

    while link_next_page is not None:
        soup = BeautifulSoup(get_html(link_next_page), features='html.parser')
        headline = soup.find_all('h2', itemprop="headline")
        links_articles = []

        # Получим все ссылки на статьи на текущей странице
        for h in headline:
            links_articles.append('https://www.nature.com' + h.find('a').get('href'))

        for (index, link) in enumerate(links_articles):

            # Получим информацию о статье
            info_article = get_info_article(link)
            names_ref_articles, links_ref_articles = get_references_name_artricles(link)

            # Выделить в модуль взаимодействия с бд
            try:
                save_article(info_article['doi'])
                node_article = create_nodes_article(info_article['name'],
                                                    info_article['doi'],
                                                    info_article['authors'],
                                                    info_article['date'],
                                                    info_article['subjects'])

                for (index, name_ref) in enumerate(names_ref_articles):
                    if name_ref is not None:
                        node_ref_art = create_node_ref_art(name_ref, links_ref_articles[index])
                        create_relationship(node_article, "LINK", node_ref_art)

                for author in info_article['authors']:
                    node_author = create_nodes_author(author)
                    create_relationship(node_author, 'WROTE', node_article)
            except:continue
            # Выделить в модуль взаимодействия с бд
        try:
            link_next_page = 'https://www.nature.com' + \
                         soup.find_all('li', class_='inline-group-item inline-group-middle')[-1].find('a').get('href')
        except:break
    return link_next_page

get_articles_subject_pages("Space physics")

#save_article_name('Happer, W., Jau, Y.-Y. & Walker, T. Optically Pumped Atoms (John Wiley-VCH, Hoboken, NJ, 2010')