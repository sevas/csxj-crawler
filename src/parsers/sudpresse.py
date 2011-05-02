__author__ = 'sevas'

from itertools import chain
import urllib
from utils import make_soup_from_html_content, fetch_content_from_url



def extract_title_and_url(container):
    if container.h1 and container.h1.a:
        link = container.h1.a
        return link.contents[0].strip(), link.get('href')



def extract_title_and_url_in_buzz(container):
        if container.h2 and container.h2.a:
            link = container.h2.a
            return link.contents[0].strip(), link.get('href')



def extract_headlines_from_buzz(column):
    buzz_container = column.find('div', {'class':'buzz exergue clearfix'})

    buzz_stories = list()
    main_buzzes = buzz_container.findAll('div')
    buzz_stories = [extract_title_and_url_in_buzz(b) for b in main_buzzes]

    def extract_title_and_url_from_list_item(item):
        return item.a.contents[0].strip(), item.a.get('href')

    buzz_list = buzz_container.ul.findAll('li')
    buzz_stories.extend([extract_title_and_url_from_list_item(item) for item in buzz_list])

    return buzz_stories


def extract_headlines_from_wrap_columns(column):
    wrap_columns = column.findAll('div', {'class':'wrap-columns clearfix'})
    stories_by_column = [col.findAll('div', {'class':'article lt clearfix'}) for col in wrap_columns]
    stories_by_column.extend([col.findAll('div', {'class':'article lt clearfix noborder'}) for col in wrap_columns])

    # flatten the result list
    all_stories = chain(*stories_by_column)

    return [extract_title_and_url(story) for story in all_stories]



def extract_main_headline(column):
    main_headline = column.find('div', {'class':'article gd clearfix'})
    return extract_title_and_url(main_headline)



def extract_headlines_from_regular_stories(column):
    regular_stories = column.findAll('div', {'class':'article md clearfix noborder'})
    return [extract_title_and_url(story) for story in regular_stories]



def extract_headlines_from_column_1(column):
    all_headlines = list()
    all_headlines.append(extract_main_headline(column))
    all_headlines.extend(extract_headlines_from_regular_stories(column))
    all_headlines.extend(extract_headlines_from_wrap_columns(column))
    all_headlines.extend(extract_headlines_from_buzz(column))

    return all_headlines



def extract_headlines_from_column_3(column):

    stories = column.findAll('div', {'class':'octetFun'})

    headlines = list()
    for story in stories:
        if story.h3.a.contents:
            title_and_url = story.h3.a.contents[0].strip(), story.h3.a.get('href')
            headlines.append(title_and_url)

    return headlines


def extract_headlines_for_one_region(region_container):
    main_story = region_container.h3.a.contents[0], region_container.h3.a.get('href')

    story_list = region_container.find('ul', {'class':'story_list'})
    def extract_title_and_link(item):
        return item.a.contents[0], item.a.get('href')

    headlines = [main_story]
    headlines.extend([extract_title_and_link(item) for item in story_list.findAll('li')])

    #print headlines
    return headlines



def extract_regional_headlines(content):
    region_containers = content.findAll('div', {'class':'story secondaire couleur_03'})

    return list(chain(*[extract_headlines_for_one_region(c) for c in region_containers]))



def get_regional_toc():
    url = 'http://sudpresse.be/regions'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    return extract_regional_headlines(soup.find('div', {'id':'content_first'}))



def make_full_url(prefix, titles_and_urls):
    return [(title, urllib.basejoin(prefix, url)) for title, url in titles_and_urls]



def get_frontpage_toc():
    url = 'http://sudpresse.be/'
    html_content = fetch_content_from_url(url)
    soup = make_soup_from_html_content(html_content)

    column1 = soup.find('div', {'class':'column col-01'})
    headlines = extract_headlines_from_column_1(column1)
    column3  = soup.find('div', {'class':'column col-03'})
    headlines.extend(extract_headlines_from_column_3(column3))


    regional_headlines = make_full_url(url, get_regional_toc())
    headlines.extend(regional_headlines)

    return make_full_url(url, headlines)





if __name__=='__main__':
    toc = get_frontpage_toc()

    print len(toc)
    for title, url in toc:
        print title, url