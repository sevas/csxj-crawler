# coding=utf-8
"""
Link extraction test suite for lavenir.py
"""

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import lavenir

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', lavenir.SOURCE_NAME)


class TestLavenirLinkExtraction(object):

    def test_bottom_box_and_sidebar_and_intext_links(self):
        """ lavenir parser correctly extracts and tags in text links + sidebar box links + bottom box links. Btw it also tests 'same owner' tagging, it's an all-in-one test. """
        with open(os.path.join(DATA_ROOT, "bottom_box_and_sidebar_and_intext_links.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.jobat.be/fr/articles/de-quel-bois-sont-faits-vos-cadets-au-boulot/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""Une volonté d’engagement et encore 2 autres caractéristiques de ces jeunes recrues""", set(['same owner', 'external', 'in text'])),
                make_tagged_url("http://www.jobat.be/fr/articles/cinq-types-de-collegues-insupportables-que-nous-connaissons-tous/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""Nico le petit comique et 4 autres collègues que nous connaissons tous""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://www.jobat.be/fr/articles/5-ruses-pour-obtenir-plus-de-ses-collegues/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""5 ruses pour en obtenir plus de ses collègues""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("http://www.jobat.be/fr/articles/cinq-types-de-collegues-insupportables-que-nous-connaissons-tous/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""Nico le petit comique et 4 autres collègues que nous connaissons tous""", set(['bottom box', 'external', 'same owner'])),
                make_tagged_url("http://www.jobat.be/fr/articles/5-ruses-pour-obtenir-plus-de-ses-collegues/?utm_source=lavenir&utm_medium=content&utm_campaign=artikel&utm_content=link", u"""5 ruses pour en obtenir plus de ses collègues""", set(['bottom box', 'external', 'same owner'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_in_text_links(self):
        """ lavenir parser correctly extracts and tags in text links and does not mistakelny extracts the end of a sentence as a plaintext link"""
        with open(os.path.join(DATA_ROOT, "in_text_links.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=DMF20130223_00273017", u"""Oscar Pistorius""", set(['internal', 'in text'])),
                make_tagged_url("http://www.lavenir.net/sports/cnt/DMF20130222_00272411", u"""est sorti libre vendredi après-midi""", set(['internal', 'in text'])),
                make_tagged_url("/channel/index.aspx?channelid=490", u"""L'athlète Pistorius tue sa compagne: toutes nos infos""", set(['internal', 'sidebar box'])),
                make_tagged_url("/channel/index.aspx?channelid=490", u"""L'athlète Pistorius tue sa compagne: toutes nos infos""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_scribblelive(self):
        """ lavenir parser correctly extracts embedded scribblelive in iframe"""
        with open(os.path.join(DATA_ROOT, "embedded_scribblelive.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=dmf20130221_00271895", u"""Tout savoir sur cette manif""", set(['internal', 'in text'])),
                make_tagged_url("http://www.lavenir.net/sports/cnt/dmf20130205_00264485", u"""Richard Virenque est venu en Belgique""", set(['internal', 'in text'])),
                make_tagged_url("http://live.lavenir.net/event/manifestation_contre_lausterite_suivez_les_perturbations_en_direct", u"""Si vous surfez via notre application mobile, cliquez ici pour suivre le live""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://embed.scribblelive.com/Embed/v5.aspx?Id=84774&ThemeId=6630", u"""http://embed.scribblelive.com/Embed/v5.aspx?Id=84774&ThemeId=6630""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("/channel/index.aspx?channelid=487", u"""Tout sur la manifestation du 21 février 2013""", set(['internal', 'sidebar box'])),
                make_tagged_url("/channel/index.aspx?channelid=487", u"""Tout sur la manifestation du 21 février 2013""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


class TestLavenirContentExtraction(object):

    def test_clean_title_extraction(self):
        """ lavenir parser correctly extracts the title"""
        with open(os.path.join(DATA_ROOT, "title_and_text.html")) as f:
            article, _ = lavenir.extract_article_data(f)

            expected_title = u'Verglas et neige sur nos routes'
            eq_(article.title, expected_title)

    def test_clean_intro_extraction(self):
        """ lavenir parser correctly extracts the intro"""
        with open(os.path.join(DATA_ROOT, "title_and_text.html")) as f:
            article, _ = lavenir.extract_article_data(f)

            expected_intro = u'Prudence sur les routes, la neige a \xe0 nouveau fait son apparition. La situation est particuli\xe8rement difficile sur le r\xe9seau secondaire.'
            eq_(article.intro, expected_intro)

    def test_clean_content_extraction(self):
        """ lavenir parser correctly extracts the article content"""
        with open(os.path.join(DATA_ROOT, "title_and_text.html")) as f:
            article, _ = lavenir.extract_article_data(f)
            expected_content = [u'Il a neig\xe9 en faible quantit\xe9 sur la Belgique. C\'est particuli\xe8rement l\'est de la Belgique qui est concern\xe9. "On a constat\xe9 de 1 \xe0 3 cm en plaine et jusqu\'\xe0 10 cm dans les Hautes Fagnes. Il s\'agit d\'une neige fine qui continuera \xe0 tomber dimanche apr\xe8s-midi". ', u'De nombreuses zones nuageuses sont pr\xe9vues ce dimanche avec des p\xe9riodes de faibles chutes de neige.', u"Un seul accident, survenu de nuit sur la N4, a \xe9t\xe9 constat\xe9. Mais la circulation y a d\xe9j\xe0 \xe9t\xe9 r\xe9tablie. Les services d'\xe9pandage ont travaill\xe9 toute la nuit et sont encore en tourn\xe9e dimanche matin.", u'"Le fait que nous sommes dimanche explique le peu de tracas rencontr\xe9. En pleine semaine, les choses ne se seraient probablement pas pass\xe9es aussi facilement", a encore d\xe9clar\xe9 le centre Perex qui appelle  \xe0 les conducteurs \xe0 adapter leur conduite sur le r\xe9seau secondaire.du  pays malgr\xe9 la neige, ont-ils annonc\xe9 dimanche matin.', u'Le verglas tend \xe0 se g\xe9n\xe9raliser sur le r\xe9seau autoroutier de Flandre', u'En Flandre, selon le centre de trafic routier r\xe9gional, la circulation sur la bande de gauche de nombreuses autoroutes \xe9tait rendue difficile \xe0 cause de la pr\xe9sence de neige.', u"Le nord du pays n'a aussi connu qu'un seul accident dans la nuit de samedi \xe0 dimanche, survenu sur le viaduc de Merksem.", u'Quelques conseils: adaptez votre vitesse; respectez les distances de s\xe9curit\xe9; et ne freinez pas brusquement sans n\xe9cessit\xe9 absolue.', u'Encore des chutes de neige ', u'Dimanche soir et nuit, le temps restera nuageux avec surtout de l\xe9g\xe8res averses de pluie ou de neige fondante dans la partie basse et moyenne de la Belgique.', u'Le haut du pays sera travers\xe9 par de faibles chutes de neige. Les minima varieront de -2\xb0C dans les Ardennes \xe0 +2\xb0C au littoral.', u'Lundi, il fera encore nuageux avec pr\xe9sence, de temps \xe0 autre, de pluie ou de neige fondante. En haute Belgique, on palera de faibles chutes de neige. Le vent de nord-est sera mod\xe9r\xe9 dans le pays \xe0 assez fort au littoral. Les maxima seront compris entre -1\xb0C dans les Ardennes et de +1\xb0C \xe0 +4\xb0C ailleurs.', u"Le reste de la semaine, il fera g\xe9n\xe9ralement sec et plut\xf4t sombre, surtout en d\xe9but de semaine. Les temp\xe9ratures \xe0 mi-journ\xe9e avoisineront les +4\xb0C.Durant le seconde partie de semaine, les chances d'\xe9claircies grandiront avec des temp\xe9ratures pouvant atteindre les +6\xb0C.", u'Cependant, les nuits resteront tr\xe8s fra\xeeches et le mercure continuera de flirter avec les 0\xb0C. ']
            eq_(article.content, expected_content)



