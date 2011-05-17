import sys
from BeautifulSoup import BeautifulSoup, Tag
from utils import fetch_content_from_url, make_soup_from_html_content, remove_text_formatting_markup







def extract_frontpage_title_and_url(link):
    title = ''.join([remove_text_formatting_markup(c.strip()) for c in link.contents])
    return title, link.get('href')



def extract_headlines_from_module(module_container):
    body = module_container.find('div', {'class':'ModuleElementBody'})
    
    headline_lists = body.findAll('div', {'class':'tot_widget-ul'})
    print len(headline_lists)



def extract_headlines_from_modules(maincontent):
    module_zone = maincontent.findAll('div', {'id':'hp-zone-list'})

    all_modules = module_zone.findAll('div', {'class':'ModuleElement'})



def extract_small_articles(maincontent):
    small_articles_container = maincontent.find('div', {'id':'SmallArticles'})

    small_articles = small_articles_container.findAll('div', {'class':'SmallArticles-Items'})
    small_articles.extend(small_articles_container.findAll('div', {'class':'SmallArticles-Items SmallArticles-Lasts'}))

    return [extract_frontpage_title_and_url(item.h5.a) for item in small_articles ]


def extract_first_articles(maincontent):
    first_article = maincontent.find('div', {'id':'FirstArticlesLeft'})
    titles_and_urls = list()

    titles_and_urls.append(extract_frontpage_title_and_url(first_article.h1.a))

    articles_right = maincontent.findAll('div', {'class':'ArticlesRight '})
    articles_right.extend(maincontent.findAll('div', {'class':'ArticlesRight ArticlesRight-First'}))
    articles_right.extend(maincontent.findAll('div', {'class':'ArticlesRight ArticlesRight-Last'}))
    
    titles_and_urls.extend(extract_frontpage_title_and_url(article.h5.a) for article in articles_right)

    return titles_and_urls



def make_full_url((title, url)):
    if url.startswith('http://'):
        return title, url
    else:
        return title, 'http://www.rtl.be{0}'.format(url)


def get_frontpage_toc():
    url = 'http://www.rtl.be/info/'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    maincontent = soup.find('div', {'class':'mainContent'})

    first_articles = extract_first_articles(maincontent)
    small_articles = extract_small_articles(maincontent)

    all_articles = first_articles + small_articles

    return [make_full_url(title_and_url) for title_and_url in all_articles]


if __name__=='__main__':
    toc = get_frontpage_toc()
    for title, url in toc:
        print title, url