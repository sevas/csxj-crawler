#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, time
from itertools import chain
import re
import urlparse
from urllib2 import HTTPError

import BeautifulSoup as bs

from csxj.common.tagging import classify_and_tag, make_tagged_url, update_tagged_urls
from csxj.db.article import ArticleData
from parser_tools.utils import fetch_html_content, make_soup_from_html_content, TEXT_MARKUP_TAGS
from parser_tools.utils import remove_text_formatting_markup_from_fragments, remove_text_formatting_and_links_from_fragments
from parser_tools.utils import extract_plaintext_urls_from_text, setup_locales
from parser_tools import constants
from parser_tools import ipm_utils
from parser_tools import twitter_utils

from helpers.unittest_generator import generate_unittest
from helpers.unittest_generator import generate_test_func, save_sample_data_file


setup_locales()

DHNET_INTERNAL_SITES = {

    'galeries.dhnet.be': ['internal', 'image gallery'],

    'tackleonweb.blogs.dhnet.be': ['internal', 'jblog'],
    'dubus.blogs.dhnet.be': ['internal', 'jblog'],
    'alorsonbuzz.blogs.dhnet.be': ['internal', 'jblog'],
    'letitsound.blogs.dhnet.be': ['internal', 'jblog'],

    'pdf-online.dhnet.be': ['internal', 'pdf newspaper']

}

DHNET_NETLOC = 'www.dhnet.be'

SOURCE_TITLE = u"DHNet"
SOURCE_NAME = u"dhnet"


def is_on_same_domain(url):
    """
    Until we get all the internal blogs/sites, we can still detect
    if a page is hosted on the same domain.
    """
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    if netloc not in DHNET_INTERNAL_SITES:
        return netloc.endswith('dhnet.be')
    return False


def classify_and_make_tagged_url(urls_and_titles, additional_tags=set()):
    """
    Classify (with tags) every element in a list of (url, title) tuples
    Returns a list of TaggedURLs
    """
    tagged_urls = []
    for url, title in urls_and_titles:
        tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
        if is_on_same_domain(url):
            tags = tags.union(['internal site', 'internal'])
        all_tags = tags.union(additional_tags)
        tagged_urls.append(make_tagged_url(url, title, all_tags))

    return tagged_urls


def cleanup_text_fragment(text_fragment):
    """
    Recursively cleans up a text fragment (e.g. nested tags).
    Returns a plain text string with no formatting info whatsoever.
    """
    if isinstance(text_fragment, bs.Tag):
        return remove_text_formatting_markup_from_fragments(text_fragment.contents)
    else:
        return text_fragment


def filter_out_useless_fragments(text_fragments):
    """
    Removes all <br /> tags and '\n' string from a list of text fragments
    extracted from an article.
    """
    def is_linebreak(text_fragment):
        if isinstance(text_fragment, bs.Tag):
            return text_fragment.name == 'br'
        else:
            return len(text_fragment.strip()) == 0

    return [fragment for fragment in text_fragments if not is_linebreak(fragment)]


def separate_no_target_links(links):
    no_target_links = [(target, title) for (target, title) in links if not target]
    other_links = list(set(links) - set(no_target_links))
    return [('', title) for (target, title) in no_target_links], other_links


def separate_keyword_links(all_links):
    keyword_links = [l for l in all_links if l[0].startswith('/sujet')]
    other_links = list(set(all_links) - set(keyword_links))

    return keyword_links, other_links


def extract_and_tag_in_text_links(article_text):
    """
    Finds the links tags in the html text content.
    Detects which links are keyword and which aren't, sets the adequate tags.
    Returns a list of TaggedURL objects.
    """
    def extract_link_and_title(link):
        return link.get('href'), remove_text_formatting_markup_from_fragments(link.contents)

    links = [extract_link_and_title(link)
             for link in article_text.findAll('a', recursive=True)]

    no_target_links, target_links = separate_no_target_links(links)
    keyword_links, other_links = separate_keyword_links(target_links)

    tagged_urls = (
        classify_and_make_tagged_url(keyword_links, additional_tags=set(['keyword', 'in text'])) +
        classify_and_make_tagged_url(other_links, additional_tags=set(['in text'])) +
        classify_and_make_tagged_url(no_target_links, additional_tags=set(['in text', 'no target']))
    )

    return tagged_urls


def sanitize_paragraph(paragraph):
    """Returns plain text article"""

    sanitized_paragraph = [remove_text_formatting_markup_from_fragments(fragment, strip_chars='\t\r\n') for fragment in paragraph.contents if
                           not isinstance(fragment, bs.Comment)]

    return ''.join(sanitized_paragraph)


def extract_text_content_and_links_from_articletext(main_content, has_intro=True):
    article_text = main_content

    in_text_tagged_urls = []
    all_cleaned_paragraphs = []
    all_rough_paragraphs = []
    all_plaintext_urls = []
    embedded_tweets = []

    def is_text_content(blob):
        if isinstance(blob, bs.Tag) and blob.name in TEXT_MARKUP_TAGS:
            return True
        if isinstance(blob, bs.NavigableString):
            return True
        return False

    text_fragments = [c for c in article_text.contents if is_text_content(c)]

    if text_fragments:
        # we first need to avoid treating embedded tweets as text
        for paragraph in text_fragments:
            if isinstance(paragraph, bs.NavigableString):
                all_cleaned_paragraphs.append(remove_text_formatting_markup_from_fragments(paragraph))
                all_rough_paragraphs.append(paragraph)

            else:
                if not paragraph.find('blockquote', {'class': 'twitter-tweet'}):
                    in_text_links = extract_and_tag_in_text_links(paragraph)
                    in_text_tagged_urls.extend(in_text_links)
                    all_cleaned_paragraphs.append(remove_text_formatting_markup_from_fragments(paragraph))
                    all_rough_paragraphs.append(paragraph)
                else:
                    embedded_tweets.extend(
                        twitter_utils.extract_rendered_tweet(paragraph, DHNET_NETLOC, DHNET_INTERNAL_SITES))

        # extracting plaintext links
        for paragraph in all_rough_paragraphs:
            plaintext_urls = extract_plaintext_urls_from_text(remove_text_formatting_and_links_from_fragments(paragraph))
            for url in plaintext_urls:
                tags = classify_and_tag(url, DHNET_NETLOC, DHNET_INTERNAL_SITES)
                tags.update(['plaintext', 'in text'])
                all_plaintext_urls.append(make_tagged_url(url, url, tags))
    else:
        all_cleaned_paragraphs = []

    return all_cleaned_paragraphs, in_text_tagged_urls + all_plaintext_urls + embedded_tweets


def article_has_intro(article_text):
    return article_text.p


def extract_intro_from_articletext(article_text):
    """
    Finds the introduction paragraph, returns a string with the text
    """
    # intro text seems to always be in the first paragraph.
    if article_has_intro(article_text):
        intro_paragraph = article_text.p
        return remove_text_formatting_markup_from_fragments(intro_paragraph.contents)
    # but sometimes there is no intro. What the hell.
    else:
        return u''


def extract_author_name_from_maincontent(main_content):
    """
    Finds the <p> element with author info, if available.
    Returns a string if found, 'None' if not.
    """
    signature = main_content.find('p', {'id': 'articleSign'})
    if signature:
        # the actual author name is often lost in a puddle of \n and \t
        # cleaning it up.
        return signature.contents[0].lstrip().rstrip()
    else:
        return constants.NO_AUTHOR_NAME


def extract_category_from_maincontent(main_content):
    """
    Finds the breadcrumbs list. Returns a list of strings,
    one per item in the trail. The '\t\n' soup around each entry is cleaned up.
    """
    breadcrumbs = main_content.find('p', {'id': 'breadcrumbs'})
    links = breadcrumbs.findAll('a', recursive=False)

    return [link.contents[0].rstrip().lstrip() for link in links]


DATE_MATCHER = re.compile('\(\d\d/\d\d/\d\d\d\d\)')


def was_publish_date_updated(date_string):
    """
    In case of live events (soccer, the article gets updated.
    Hour of last update is appended to the publish date.
    """
    # we try to match a non-updated date, and check that it failed.<
    match = DATE_MATCHER.match(date_string)
    return not match


def make_time_from_string(time_string):
    """
    Takes a HH:MM string, returns a time object
    """
    h, m = [int(i) for i in time_string.split(':')]
    return time(h, m)


def extract_date_from_maincontent(main_content):
    """
    Finds the publication date string, returns a datetime object
    """
    date_string = main_content.find('p', {'id': 'articleDate'}).contents[0]

    if was_publish_date_updated(date_string):
        # extract the update time, make the date look like '(dd/mm/yyyy)'
        date_string, time_string = date_string.split(',')
        date_string = '{0})'.format(date_string)

        # the time string looks like : 'mis à jour le hh:mm)'
        time_string = time_string.split(' ')[-1]
        pub_time = make_time_from_string(time_string.rstrip(')'))
    else:
        pub_time = None

    pub_date = datetime.strptime(date_string, "(%d/%m/%Y)").date()

    return pub_date, pub_time



def extract_links_to_embedded_content(main_content):
    items = main_content.findAll('div', {'class': 'embedContents'})
    return [ipm_utils.extract_tagged_url_from_embedded_item(item, DHNET_NETLOC, DHNET_INTERNAL_SITES) for item in items]


def extract_article_data(source):
    """
    """
    if hasattr(source, 'read'):
        html_content = source.read()
    else:
        try:
            html_content = fetch_html_content(source)
        except HTTPError as e:
            if e.code == 404:
                return None, None
            else:
                raise
        except Exception:
            raise

    soup = make_soup_from_html_content(html_content)

    main_content = soup.find('div', {'id': 'maincontent'})

    if main_content and main_content.h1:
        title = remove_text_formatting_markup_from_fragments(main_content.h1.contents)
        pub_date, pub_time = extract_date_from_maincontent(main_content)
        category = extract_category_from_maincontent(main_content)
        author_name = extract_author_name_from_maincontent(main_content)

        article_text = main_content.find('div', {'id': 'articleText'})
        if article_has_intro(article_text):
            intro = extract_intro_from_articletext(article_text)
            text, in_text_links = extract_text_content_and_links_from_articletext(article_text)
        else:
            intro = u""
            text, in_text_links = extract_text_content_and_links_from_articletext(article_text, False)

        audio_content_links = ipm_utils.extract_embedded_audio_links(main_content, DHNET_NETLOC, DHNET_INTERNAL_SITES)
        sidebox_links = ipm_utils.extract_and_tag_associated_links(main_content, DHNET_NETLOC, DHNET_INTERNAL_SITES)
        bottom_links = ipm_utils.extract_bottom_links(main_content, DHNET_NETLOC, DHNET_INTERNAL_SITES)
        embedded_content_links = extract_links_to_embedded_content(main_content)
        all_links = in_text_links + sidebox_links + embedded_content_links + bottom_links + audio_content_links

        updated_tagged_urls = update_tagged_urls(all_links, ipm_utils.DHNET_SAME_OWNER)

        fetched_datetime = datetime.today()

        # print generate_test_func('soundcloud', 'dhnet', dict(tagged_urls=updated_tagged_urls))
        # save_sample_data_file(html_content, source, 'soundcloud', '/Users/judemaey/code/csxj-crawler/tests/datasources/test_data/dhnet')
       
        # import os
        # generate_unittest("links_embedded_canalplus", "dhnet", dict(urls=updated_tagged_urls), html_content, source, os.path.join(os.path.dirname(__file__), "../../tests/datasources/test_data/dhnet"), True)



        new_article = ArticleData(source, title, pub_date, pub_time, fetched_datetime,
                                  updated_tagged_urls,
                                  category, author_name, intro, text)
        return new_article, html_content
    else:
        return None, html_content


def extract_title_and_link_from_item_box(item_box):
    title = item_box.h2.a.contents[0].rstrip().lstrip()
    url = item_box.h2.a.get('href')
    return title, url


def is_item_box_an_ad_placeholder(item_box):
    # awesome heuristic : if children are iframes, then go to hell
    return len(item_box.findAll('iframe')) != 0


def extract_title_and_link_from_anounce_group(announce_group):
    # sometimes they use item box to show ads or some crap like that.
    odd_boxes = announce_group.findAll('div', {'class': 'box4 odd'})
    even_boxes = announce_group.findAll('div', {'class': 'box4 even'})

    all_boxes = chain(odd_boxes, even_boxes)

    return [extract_title_and_link_from_item_box(box)
            for box in all_boxes
            if not is_item_box_an_ad_placeholder(box)]


def get_first_story_title_and_url(main_content):
    """
    Extract the title and url of the main frontpage story
    """
    first_announce = main_content.find('div', {'id': 'firstAnnounce'})
    first_title = first_announce.h2.a.get('title')
    first_url = first_announce.h2.a.get('href')

    return first_title, first_url


def get_frontpage_toc():
    url = 'http://www.dhnet.be'
    html_content = fetch_html_content(url)
    soup = make_soup_from_html_content(html_content)

    main_content = soup.find('div', {'id': 'maincontent'})
    if main_content:
        all_titles_and_urls = []

        # so, the list here is a combination of several subcontainer types.
        # processing every type separately
        first_title, first_url = get_first_story_title_and_url(main_content)
        all_titles_and_urls.append((first_title, first_url))

        # this will pick up the 'annouceGroup' containers with same type in the 'regions' div
        first_announce_groups = main_content.findAll('div',
                                                     {'class': 'announceGroupFirst announceGroup'},
                                                     recursive=True)
        announce_groups = main_content.findAll('div',
                                               {'class': 'announceGroup'},
                                               recursive=True)

        # all those containers have two sub stories
        for announce_group in chain(first_announce_groups, announce_groups):
            titles_and_urls = extract_title_and_link_from_anounce_group(announce_group)
            all_titles_and_urls.extend(titles_and_urls)

        return [(title, 'http://www.dhnet.be%s' % url) for (title, url) in all_titles_and_urls], [], []
    else:
        return [], [], []


if __name__ == "__main__":
    urls = [
        "http://www.dhnet.be/infos/faits-divers/article/381082/le-fondateur-des-protheses-pip-admet-la-tromperie-devant-la-police.html",
        "http://www.dhnet.be/sports/formule-1/article/377150/ecclestone-bientot-l-europe-n-aura-plus-que-cinq-grands-prix.html",
        "http://www.dhnet.be/infos/belgique/article/378150/la-n-va-menera-l-opposition-a-un-gouvernement-francophone-et-taxateur.html",
        "http://www.dhnet.be/cine-tele/divers/article/378363/sois-belge-et-poile-toi.html",
        "http://www.dhnet.be/infos/societe/article/379508/contribuez-au-journal-des-bonnes-nouvelles.html",
        "http://www.dhnet.be/infos/belgique/article/386721/budget-l-effort-de-2-milliards-confirme.html",
        "http://www.dhnet.be/infos/monde/article/413062/sandy-paralyse-le-nord-est-des-etats-unis.html",
        "http://www.dhnet.be/infos/economie/article/387149/belfius-fait-deja-le-buzz.html",
        "http://www.dhnet.be/infos/faits-divers/article/388710/tragedie-de-sierre-toutes-nos-videos-reactions-temoignages-condoleances.html",
        "http://www.dhnet.be/people/show-biz/article/421868/rosie-huntington-whiteley-sens-dessus-dessous.html",
        "http://www.dhnet.be/infos/buzz/article/395893/rachida-dati-jette-son-venin.html",
        # "http://www.dhnet.be/infos/societe/article/420219/les-femmes-a-talons-sont-elles-plus-seduisantes.html",
        # "http://www.dhnet.be/sports/football/article/393699/hazard-s-impose-avec-lille.html",
        # "http://www.dhnet.be/sports/football/article/393678/reynders-boycotte-l-euro-de-football-en-ukraine.html",
        # "http://www.dhnet.be/people/sports/article/393650/tom-boonen-sans-les-mains.html",

        #plaintext links:
        "http://www.dhnet.be/infos/belgique/article/417360/neige-preparez-vous-au-chaos-ce-matin.html",

        # errors:
        "http://www.dhnet.be/cine-tele/cinema/article/413216/dany-boon-mon-coach-me-tapait.html",
        "http://www.dhnet.be/cine-tele/cinema/article/417899/peter-jackson-on-vit-une-periode-de-reve-pour-les-cineastes.html",
        "http://www.dhnet.be/sports/football/article/418323/benteke-s-offre-un-double-avec-aston-villa.html",
        "http://www.dhnet.be/infos/monde/article/421061/un-anti-mariage-gay-compare-hollande-a-hitler.html",
        "http://www.dhnet.be/people/show-biz/article/416554/lorie-sexy-a-souhait-dans-son-nouveau-clip.html",
        "http://www.dhnet.be/cine-tele/television/article/378062/ppda-deja-vire-de-france-3.html",
        "http://www.dhnet.be/infos/buzz/article/377700/nicolas-bedos-sort-avec-l-etudiante-qui-l-avait-interpellee.html",
        "http://www.dhnet.be/sports/basket/article/420383/podcast-basket-retour-sur-la-11e-journee.html",
        "http://www.dhnet.be/cine-tele/cinema/article/423342/joachim-lafosse-olivier-gourmet-et-emilie-dequenne-triomphent-aux-magritte.html",
        "http://www.dhnet.be/infos/monde/article/378171/la-video-de-surveillance-de-dsk-quittant-le-sofitel-devoilee.html",
        "http://www.dhnet.be/cine-tele/television/article/383998/flop-de-la-nouvelle-emission-de-tf1.html",
        "http://www.dhnet.be/sports/diables-rouges/article/387159/leekens-le-probleme-sur-les-flancs-de-la-defense-est-resolu.html",
        "http://www.dhnet.be/sports/football/article/395788/pari-ose-de-nike-avec-le-nouveau-maillot-du-barca.html",
        "http://www.dhnet.be/sports/omnisports/article/409542/colsaerts-ecrase-tiger-woods.html",
        "http://www.dhnet.be/infos/belgique/article/388466/les-cigarette-plus-cheres-de-dix-centimes-la-solution-de-facilite.html",
        "http://www.dhnet.be/infos/faits-divers/article/388821/le-rapatriement-des-enfants-et-des-familles-a-commence.html",
        "http://www.dhnet.be/people/show-biz/article/417202/alizee-revienten-soutif.html",
        "http://www.dhnet.be/infos/monde/article/421061/un-anti-mariage-gay-compare-hollande-a-hitler.html",
        "http://www.dhnet.be/infos/monde/article/415459/la-soeur-de-mohammed-merah-condamne-ses-actes.html",
        "http://www.dhnet.be/infos/monde/article/378171/la-video-de-surveillance-de-dsk-quittant-le-sofitel-devoilee.html",
        "http://www.dhnet.be/infos/belgique/article/388466/les-cigarette-plus-cheres-de-dix-centimes-la-solution-de-facilite.html",
        "http://www.dhnet.be/infos/monde/article/389327/toulouse-la-police-cerne-un-homme-se-reclamant-d-al-qaida.html",
        "http://www.dhnet.be/people/buzz/article/422740/jennifer-lawrence-laisse-tomber-le-bas.html",
        "http://www.dhnet.be/cine-tele/cinema/article/415028/la-sexualite-debridee-de-james-bond-en-detail.html",
        "http://www.dhnet.be/sports/football/article/393211/guardiola-est-remplace-par-son-t2.html",
        "http://www.dhnet.be/infos/faits-divers/article/397637/chauffeur-de-la-stib-la-video-de-l-agression.html",
        "http://www.dhnet.be/infos/belgique/article/413443/jan-fabre-agresse-apres-son-lancer-de-chats.html",
        "http://www.dhnet.be/infos/societe/article/381608/le-doigt-glace-de-la-mort-enfin-filme.html",
        "http://www.dhnet.be/infos/societe/article/400147/deux-pattes-suffisent-au-bonheur-de-ce-chat.html",
        "http://www.dhnet.be/sports/jo-2012/article/404259/mais-que-fait-il-au-fond-de-la-piscine.html",
        "http://www.dhnet.be/infos/monde/article/386567/veronique-de-keyser-bachar-el-assad-doit-partir.html"
    ]

    from csxj.common.tagging import print_taggedURLs


    urls_from_errors = [
    "http://www.dhnet.be/sports/jo-2012/article/404259/mais-que-fait-il-au-fond-de-la-piscine.html",
    "http://www.dhnet.be/infos/monde/article/386567/veronique-de-keyser-bachar-el-assad-doit-partir.html",
    "http://www.dhnet.be/sports/standard/article/386151/benteke-et-la-dictature-du-standard.html",
    "http://www.dhnet.be/sports/standard/article/386151/benteke-et-la-dictature-du-standard.html",
    "http://www.dhnet.be/sports/cyclisme/article/411974/rabobank-dans-le-peloton-l-an-prochain-sans-le-nom-de-son-sponsor.html",
    "http://www.dhnet.be/sports/diables-rouges/article/411880/le-vlaams-belang-tacle-vincent-kompany.html",
    "http://www.dhnet.be/infos/faits-divers/article/410926/legear-n-a-pas-minimise-l-accident-mais-ne-maitrise-pas-l-anglais.html",
    "http://www.dhnet.be/infos/monde/article/411527/felix-baumgartner-a-cru-qu-il-allait-s-evanouir-buzz-reussi-pour-red-bull.html",
    "http://www.dhnet.be/infos/belgique/article/411773/philippe-moureaux-entre-mepris-et-amertume.html",
    "http://www.dhnet.be/cine-tele/twizz-radio/article/410897/les-flingueurs-de-l-info-de-twizz-radio-reviendront-sur-l-alimentation.html",
    "http://www.dhnet.be/sports/football/article/391091/une-equipe-flamande-n-accepte-plus-de-jouer-contre-des-clubs-bruxellois.html",
    "http://www.dhnet.be/cine-tele/television/article/390910/les-votes-des-coaches-sur-la-sellette.html",
    "http://www.dhnet.be/sports/football/article/390872/la-ligue-des-champions-tombe-dans-l-escarcelle-de-belgacom-tv.html",
    "http://www.dhnet.be/sports/edito/article/390759/un-arbitre-qui-en-a.html",
    "http://www.dhnet.be/infos/faits-divers/article/399047/mactac-un-renvoi-en-correctionnelle.html",
    "http://www.dhnet.be/people/show-biz/article/391307/ses-seins-ne-lui-servent-plus.html",
    "http://www.dhnet.be/cine-tele/cinema/article/401289/les-kaira-meme-pas-drole.html",
    "http://www.dhnet.be/cine-tele/television/article/401580/bref-voici-les-deux-derniers-episodes.html",
    "http://www.dhnet.be/cine-tele/cinema/article/402072/le-belge-de-chez-pixar.html",
    "http://www.dhnet.be/people/show-biz/article/413110/olivia-ruiz-veut-de-plus-gros-seins.html",
    "http://www.dhnet.be/infos/societe/article/412580/le-beluga-qui-imitait-les-humains.html",
    "http://www.dhnet.be/cine-tele/twizz-radio/article/410897/les-flingueurs-de-l-info-de-twizz-radio-reviendront-sur-les-p-v-de-la-stib.html",
    "http://www.dhnet.be/cine-tele/twizz-radio/article/410897/quand-les-flingueurs-appellent-bart.html",
    "http://www.dhnet.be/people/show-biz/article/398936/la-divine-idylle-est-bel-et-bien-terminee.html",
    "http://www.dhnet.be/people/buzz/article/417129/elle-fait-un-strip-tease-en-plein-metro.html",
    "http://www.dhnet.be/people/buzz/article/417129/elle-fait-un-strip-tease-en-plein-metro.html",
    "http://www.dhnet.be/people/buzz/article/417337/quand-les-chiens-apprennent-a-conduire.html",
    "http://www.dhnet.be/infos/societe/article/417448/la-nasa-revele-le-cote-obscur-de-la-planete.html",
    "http://www.dhnet.be/cine-tele/cinema/article/402789/un-batman-d-anthologie.html",
    "http://www.dhnet.be/sports/football/article/380235/le-boxing-day-du-pauvre.html",
    "http://www.dhnet.be/cine-tele/cinema/article/425802/suivez-la-ceremonie-en-direct-des-21h.html",
    "http://www.dhnet.be/cine-tele/cinema/article/425492/la-france-est-une-passoire.html",
    "http://www.dhnet.be/sports/basket/article/425682/podcast-basket-retour-sur-le-transfert-de-walsh.html"]

    # for url in urls_from_errors:
    #     print url
    #     article, html = extract_article_data(url)
    #     if article:
    #         print "this one works just fine"
    #     else:
    #         print "404"
    
    article, html = extract_article_data(urls[-1])
    # print article.title
    # print article.url
    # print "°°°°°°°°°°°°°°°°°°°°"
    # for link in article.links:
    #     print link.title
    #     print link.URL
    #     print link.tags
        # print "°°°°°°°°°°°°°°°°°°°°"

    # from pprint import pprint
    # print_taggedURLs(article.links)



