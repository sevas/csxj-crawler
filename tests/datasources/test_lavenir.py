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


class TestLavenirOldLinkExtraction(object):
    def test_links_old_flowplayer(self):
        """[BACKWARDS] lavenir parser tags embedded flowplayer videos as embedded videos (but does not extract url and marks it as 'unfinished')"""
        with open(os.path.join(DATA_ROOT, "links_old_flowplayer.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("__EMBEDDED_VIDEO_URL__", u"""__EMBEDDED_VIDEO_TITLE__""", set([u'unfinished', 'video', 'external', 'embedded', 'flowplayer'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)


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
                make_tagged_url("http://player.vimeo.com/video/60173231?title=0&byline=0&portrait=0&color=47bf61", u"""http://player.vimeo.com/video/60173231?title=0&byline=0&portrait=0&color=47bf61""", set(['video', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_external_links(self):
        """ lavenir parser correctly extracts external, in-text links"""
        with open(os.path.join(DATA_ROOT, "external_links.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.couleurcafe.be/en/couleur_cafe/tickets/presale-274.html", u"""Les préventes pour le festival sont désormais en vente""", set(['external', 'in text'])),
                make_tagged_url("http://www.couleurcafe.be/en/couleur_cafe/home-270.html", u"""Couleur Café""", set(['external', 'in text'])),
                make_tagged_url("/channel/index.aspx?channelid=72", u"""Festivals de l'été""", set(['internal', 'sidebar box'])),
                make_tagged_url("/channel/index.aspx?channelid=293", u"""Tout sur la culture à Bruxelles""", set(['internal', 'sidebar box'])),
                make_tagged_url("/channel/index.aspx?channelid=369", u"""Tout sur le festival Couleur Café""", set(['internal', 'sidebar box'])),
                make_tagged_url("/channel/index.aspx?channelid=72", u"""Festivals de l'été""", set(['bottom box', 'internal'])),
                make_tagged_url("/channel/index.aspx?channelid=293", u"""Tout sur la culture à Bruxelles""", set(['bottom box', 'internal'])),
                make_tagged_url("/channel/index.aspx?channelid=369", u"""Tout sur le festival Couleur Café""", set(['bottom box', 'internal'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_embedded_youtube(self):
        """ lavenir parser correctly extract links from embedded youtube videos"""
        with open(os.path.join(DATA_ROOT, "links_embedded_youtube.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.youtube.com/embed/gS9o1FAszdk", u"""http://www.youtube.com/embed/gS9o1FAszdk""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.youtube.com/embed/qMxX-QOV9tI", u"""http://www.youtube.com/embed/qMxX-QOV9tI""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.youtube.com/embed/6KUJE2xs-RE", u"""http://www.youtube.com/embed/6KUJE2xs-RE""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.youtube.com/embed/uSD4vsh1zDA", u"""http://www.youtube.com/embed/uSD4vsh1zDA""", set(['iframe', 'external', 'embedded', 'in text'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_highlighted_youtube_and_ghost_links(self):
        """ lavenir parser can extracts links to videos in that weird 'highlighted' top section. Also, it deals with ghost links like a champ."""
        with open(os.path.join(DATA_ROOT, "links_highlighted_youtube_and_ghost_links.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://rainn.org/", u"""RAINN,""", set(['external', 'in text'])),
                make_tagged_url("http://www.youtube.com/embed/KtzqvqzBdUQ", u"""http://www.youtube.com/embed/KtzqvqzBdUQ""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://", u"""__GHOST_LINK__""", set([u'ghost link', 'sidebar box'])),
                make_tagged_url("http://", u"""__GHOST_LINK__""", set(['bottom box', u'ghost link'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_flowplayer(self):
        """ lavenir parser tags embedded flowplayer videos as embedded videos (but does not extract url and marks it as 'unfinished')"""
        with open(os.path.join(DATA_ROOT, "links_flowplayer.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("__EMBEDDED_VIDEO_URL__", u"""__EMBEDDED_VIDEO_TITLE__""", set([u'unfinished', 'video', 'external', 'embedded', 'flowplayer'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_meltybuzz_video(self):
        with open(os.path.join(DATA_ROOT, "meltybuzz_video.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.meltybuzz.fr/swf/api/e/argv/id/1057156/c/FF6600/", u"""http://www.meltybuzz.fr/swf/api/e/argv/id/1057156/c/FF6600/""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/buzz", u"""Buzz""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/buzz/vusurinternet", u"""Vu sur internet""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/videos", u"""Vidéos""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/championsleague", u"""Champions League""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

class TestLavenirNewLinkExtraction(object):
    """ Test suite for the new lavenir.net page template """
    def test_new_links_storify(self):
        """ lavenir [new template] parser can extract a link to an embedded storify widget"""
        with open(os.path.join(DATA_ROOT, "new_links_storify.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://storify.com/Lavenir/les-meilleurs-tweets-sur-l-euro.js", u"""View the story "Les meilleurs tweets sur l'Euro" on Storify""", set(['external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/buzz", u"""Buzz""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/buzz/vusurinternet", u"""Vu sur internet""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/channel/index.aspx?channelid=299", u"""Tout sur l'Euro 2012 de football""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_scribblelive(self):
        """ lavenir [new template] parser can extract a link to an embedded scribblelive iframe"""
        with open(os.path.join(DATA_ROOT, "new_links_scribblelive.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/sports/cnt/DMF20130309_018", u"""+ Cliquez sur ce lien pour suivre notre grand direct D1: 8 matches au programme!""", set(['internal', 'in text'])),
                make_tagged_url("http://live.lavenir.net/Event/D2-D3-Promotion-09-03-2013", u"""Si vous surfez via notre application mobile, cliquez sur ce lien pour suivre le multilive""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://embed.scribblelive.com/Embed/v5.aspx?Id=87875&ThemeId=6630", u"""http://embed.scribblelive.com/Embed/v5.aspx?Id=87875&ThemeId=6630""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/d2", u"""D2""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/d3b", u"""D3B""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/promotiond", u"""Promotion D""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/promotionb", u"""Promotion B""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/hainaut/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/brabantwallon/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/liege/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/namur/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/luxembourg/sports/football", u"""Football""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_intext_iframe(self):
        """ lavenir [new template] parser can extract a link to an in text embedded iframe"""
        with open(os.path.join(DATA_ROOT, "new_links_intext_iframe.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.youtube.com/embed/_lEgFnNwPzY", u"""http://www.youtube.com/embed/_lEgFnNwPzY""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.lavenir.net/enimages", u"""En images""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/videos", u"""Vidéos""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/basket", u"""Basket""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_ignore_photosets(self):
        """ lavenir [new template] parser ignores photosets"""
        with open(os.path.join(DATA_ROOT, "new_links_ignore_photosets.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("/sports/cyclisme", u"""Cyclisme""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_highlighted_video(self):
        """ lavenir [new template] parser can extract a link to a video in the 'highlight' section"""
        with open(os.path.join(DATA_ROOT, "new_links_highlighted_video.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.youtube.com/embed/6G-75ljWk3A", u"""http://www.youtube.com/embed/6G-75ljWk3A""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/buzz", u"""Buzz""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/buzz/instantgag", u"""Instant Gag""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_in_text(self):
        """ lavenir [new template] parser can extract in-text links"""
        with open(os.path.join(DATA_ROOT, "new_links_in_text.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.cretesdespa.be", u"""www.cretesdespa.be""", set(['external', 'in text'])),
                make_tagged_url("http://www.chronorace.be", u"""http://www.chronorace.be""", set(['external', 'in text'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/jogging", u"""Jogging""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/liege/sports", u"""Sports""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_iframe_videos(self):
        """ lavenir [new template] parser can extract another kind of in text iframe videos (rtlinfo)"""
        with open(os.path.join(DATA_ROOT, "new_links_iframe_videos.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.rtl.be/clubrtl/page/syndication/913.aspx?videoid=435782&key=cdbf072d-48bd-48f8-b711-0db29ad4a71f", u"""http://www.rtl.be/clubrtl/page/syndication/913.aspx?videoid=435782&key=cdbf072d-48bd-48f8-b711-0db29ad4a71f""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.rtl.be/clubrtl/page/syndication/913.aspx?videoid=435780&key=cdbf072d-48bd-48f8-b711-0db29ad4a71f", u"""http://www.rtl.be/clubrtl/page/syndication/913.aspx?videoid=435780&key=cdbf072d-48bd-48f8-b711-0db29ad4a71f""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.rtl.be/clubrtl/page/syndication/913.aspx?videoid=435781&key=cdbf072d-48bd-48f8-b711-0db29ad4a71f", u"""http://www.rtl.be/clubrtl/page/syndication/913.aspx?videoid=435781&key=cdbf072d-48bd-48f8-b711-0db29ad4a71f""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/europaleague", u"""Europa League""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/channel/index.aspx?channelid=86", u"""TOUT SUR LES DIABLES ROUGES""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_special_in_text(self):
        """ lavenir [new template] parser can in-text links, even if they look like they are located in a bolded paragraph"""
        with open(os.path.join(DATA_ROOT, "new_links_special_in_text.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://tech.lavenir.net/ge/visite_touristique.kmz", u"""Pour découvrir ce parcours en mode 3D avec photographies, cliquez sur ce lien""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("/sports/jogging", u"""Jogging""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_in_text_vimeo(self):
        """ lavenir [new template] parser can extract a link to an embedded vimeo iframe. iframes are cool."""
        with open(os.path.join(DATA_ROOT, "new_links_in_text_vimeo.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.marathonnature.be/", u"""Marathon Nature""", set(['external', 'in text'])),
                make_tagged_url("http://www.marathonnature.be/", u"""www.lavenir.net/jogging""", set(['external', 'in text'])),
                make_tagged_url("http://www.lavenir.net/kyra", u"""www.lavenir.net/kyra""", set(['internal', 'in text'])),
                make_tagged_url("http://jogging.lavenir.net/", u"""www.lavenir.net/jogging""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lavenir.net/kyra", u"""page facebook""", set(['internal', 'in text'])),
                make_tagged_url("http://player.vimeo.com/video/61011660?title=0&byline=0&portrait=0&color=47bf61", u"""http://player.vimeo.com/video/61011660?title=0&byline=0&portrait=0&color=47bf61""", set(['iframe', 'external', 'embedded', 'in text'])),
                make_tagged_url("http://www.lavenir.net/enimages", u"""En images""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/buzz", u"""Buzz""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/buzz/insolite", u"""Insolite""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/jogging", u"""Jogging""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/videos", u"""Vidéos""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_bottom_links(self):
        """ lavenir [new template] parser can extract links for related articles"""
        with open(os.path.join(DATA_ROOT, "new_links_bottom_links.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("/sports/cnt/DMF20130303_00276326", u"""Euro indoor de Göteborg: pas de médaille pour Tia Hellebaut, qui ne passe pas 1m92""", set(['bottom box', 'internal', 'related'])),
                make_tagged_url("http://www.lavenir.net/diaporamas", u"""Diaporamas""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/athletisme", u"""Athlétisme""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/channel/index.aspx?channelid=497", u"""Tout sur l'Euro indoor d'athlétisme""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_pdf_newspaper_tag(self):
        """ lavenir [new template] parser correctly detects and tags links to the pdf version of the publication"""
        with open(os.path.join(DATA_ROOT, "new_links_pdf_newspaper_tag.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://lavenir.newspaperdirect.com/epaper/viewer.aspx?utm_source=site&utm_medium=journal", u"""en format PDF""", set(['internal', 'pdf newspaper', 'in text'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/diaporamas", u"""Diaporamas""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/basket", u"""Basket""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/liege/sports", u"""Sports""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_another_storify(self):
        """ lavenir [new template] parser handles several kinds of embedded storify"""
        with open(os.path.join(DATA_ROOT, "new_links_another_storify.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("//storify.com/lavenir_net/foot-les-incontournables-images-du-week-end-04-03", """View the story "Foot: les incontournables images du week-end (04/03/2013)" on Storify""", set(['external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/enimages", u"""En images""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/la-video-du-jour", u"""La vidéo du jour""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/buzz/vusurinternet", u"""Vu sur internet""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/videos", u"""Vidéos""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/channel/index.aspx?channelid=448", u"""LES WEEK-ENDS FOOT EN IMAGES""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_embedded_poll(self):
        """ lavenir [new template] parser handles embedded in-house polling system (qualifio.lavenir.net)"""
        with open(os.path.join(DATA_ROOT, "new_links_embedded_poll.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://qualifio.lavenir.net/10/v1.cfm?id=0D9ECE28-5056-8040-9FF7-84C0DDC965F9", u"""http://qualifio.lavenir.net/10/v1.cfm?id=0D9ECE28-5056-8040-9FF7-84C0DDC965F9""", set(['internal', 'iframe', 'internal site', 'embedded', 'in text'])),
                make_tagged_url("/sports/autres", u"""Autres""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/athletisme", u"""Athlétisme""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/moteurs", u"""Moteurs""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/proleague", u"""Pro League""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/channel/index.aspx?channelid=447", u"""TOUS NOS QUIZ SPORTIFS""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_soccer_video_from_hungary(self):
        """ lavenir [new template] parser loves hungarian soccer videos"""
        with open(os.path.join(DATA_ROOT, "new_links_soccer_video_from_hungary.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://videa.hu/videok/sport/as-roma-3-1-genoa-alessio-romagnoli-francesco-totti-a7Mhqa5118CHtLlG", u"""szólj hozzá: AS Roma 3-1 Genoa MATCH HIGHLIGHTS""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/serie-a", u"""Serie A""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_epic_dataviz(self):
        """ lavenir [new template] parser handles some kind of soccer-related dataviz thingy"""
        with open(os.path.join(DATA_ROOT, "new_links_epic_dataviz.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://lavenir.newspaperdirect.com/epaper/viewer.aspx?utm_source=site&utm_medium=journal", u"""en format PDF""", set(['internal', 'pdf newspaper', 'in text'])),
                make_tagged_url("http://tech.lavenir.net/foot_d1_afp", u"""http://tech.lavenir.net/foot_d1_afp""", set(['internal', 'iframe', 'internal site', 'embedded', 'in text'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/proleague", u"""Pro League""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/regions/hainaut/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/channel/index.aspx?channelid=70", u"""TOUT SUR LE SPORTING DE CHARLEROI""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_vimeo_in_header(self):
        """ lavenir [new template] parser can extract (vimeo) videos from the article header"""
        with open(os.path.join(DATA_ROOT, "new_links_vimeo_in_header.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/jogging", u"""www.lavenir.net/jogging""", set(['internal', 'in text'])),
                make_tagged_url("http://player.vimeo.com/video/60939915?title=0&byline=0&portrait=0&color=47bf61", u"""http://player.vimeo.com/video/60939915?title=0&byline=0&portrait=0&color=47bf61""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/enimages", u"""En images""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/jogging", u"""Jogging""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/videos", u"""Vidéos""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_rendered_tweet_in_iframes(self):
        """ lavenir [new template] parser handles embedded tweets rendered in an iframe"""
        with open(os.path.join(DATA_ROOT, "new_links_rendered_tweet_in_iframes.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/sports/cnt/DMF20130305_00277443", u"""+ Maradona prêt à étudier une éventuelle proposition de Montpellier""", set(['internal', 'in text'])),
                make_tagged_url("http://www.lavenir.net/sports/cnt/DMF20130303_00276317", u"""C'est désormais officiel, René Girard va quitter le champion de France en titre, en fin de saison.""", set(['internal', 'in text'])),
                make_tagged_url("https://twitter.com/Footballogue/status/308856064181424129", u"""[RENDERED TWEET]""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("https://twitter.com/Midilibre/status/308662550617284608", u"""[RENDERED TWEET]""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/ligue1", u"""Ligue 1""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_new_links_yet_another_storify(self):
        """ lavenir [new template] parser has no issue handling an embedded storify, even if there is no <noscript> element"""
        with open(os.path.join(DATA_ROOT, "new_links_yet_another_storify.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=dmf20120711_00180928", u"""des tenues, plutôt chics, signées Ralph Lauren""", set(['internal', 'in text'])),
                make_tagged_url("http://storify.com/lavenir_net/les-espagnols-seront-beaux-aux-jo.js?header=false", u"""__RENDERED_STORIFY__""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/life", u"""Life""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/autres", u"""Autres""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/belgiqueetmonde", u"""Belgique et monde""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/life/belle", u"""Belle""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/life/belle/mode", u"""Mode""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/channel/index.aspx?channelid=300", u"""Tout sur les JO 2012 à Londres""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_new_jwplayer(self):
        """ lavenir [new template] parser tags embedded jwplayer videos as embedded videos (but does not extract url and marks it as 'unfinished')"""
        with open(os.path.join(DATA_ROOT, "links_new_jwplayer.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=DMF20110331_063", u"""Il avait été condamné à une peine de prison de deux semaines avec suris, une amende et un retrait de permis d'un mois""", set(['internal', 'in text'])),
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=DMF20110331_063", u"""Le joueur de Grozny avait été condamné en première instance à une déchéance du droit de conduire de six mois.""", set(['internal', 'in text'])),
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=DMF20110310_044", u"""et avait proposé d’accomplir une peine de travail sous la forme d’une action sociale""", set(['internal', 'in text'])),
                make_tagged_url("__EMBEDDED_VIDEO_URL__", u"""__EMBEDDED_VIDEO_TITLE__""", set([u'unfinished', 'video', 'external', 'embedded', 'jwplayer'])),
                make_tagged_url("/sports/cnt/DMF20121009_00215953", u"""Jonathan Legear : « Mon accident ne changera rien à ma carrière »""", set(['bottom box', 'internal', 'related'])),
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=DMF20121010_00216197", u"""Une peine alternative via l’IBSR""", set(['bottom box', 'internal', 'related'])),
                make_tagged_url("http://www.lavenir.net/article/detail.aspx?articleid=DMF20121010_00215993", u"""Et pourtant… Porsche propose des cours de conduite""", set(['bottom box', 'internal', 'related'])),
                make_tagged_url("/sports/cnt/DMF20121008_00215326", u"""Jonathan Legear: «Je n’étais pas dans un état profond d’ivresse»""", set(['bottom box', 'internal', 'related'])),
                make_tagged_url("http://www.lavenir.net/enimages", u"""En images""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/societe/faitsdivers", u"""Faits divers""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/regions", u"""Régions""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/videos", u"""Vidéos""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_new_video_embed_element_eitb(self):
        """ lavenir [new template] parser can extract eitb.com videos in an <embed> element """
        with open(os.path.join(DATA_ROOT, "links_new_video_embed_element_eitb.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.eitb.com/en/get/multimedia/video/id/1002865/size/grande/f_mod/1355423402", u"""__EMBEDDED_VIDEO_TITLE__""", set(['video', 'external', 'embedded'])),
                make_tagged_url("http://www.lavenir.net/buzz", u"""Buzz""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/buzz/vusurinternet", u"""Vu sur internet""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/basket", u"""Basket""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_new_ignore_images_in_video_div(self):
        """ lavenir [new template] parser ignore <img> elements located where a video should have been"""
        with open(os.path.join(DATA_ROOT, "links_new_ignore_images_in_video_div.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/buzz/insolite", u"""Insolite""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football", u"""Football""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_new_ignore_animated_gifs_in_video_div(self):
        """ lavenir [new template] parser ignore <img> elements located where a video should have been. It also works for animated gif files. Which are pronoucened 'jif', btw."""
        with open(os.path.join(DATA_ROOT, "links_new_ignore_animated_gifs_in_video_div.html")) as f:
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/premierleague", u"""Premier League""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_new_ooyala_videos(self):
        with open(os.path.join(DATA_ROOT, "links_new_ooyala_videos.html")) as f:
            """ lavenir [new template] handles ooyala videos (tagged as unfinished)"""
            article, raw_html = lavenir.extract_article_data(f)
            extracted_links = article.links
            urls = [
                make_tagged_url("http://www.lavenir.net/sports/cnt/DMF20130124_00259765", u"""+ Chelsea: enquête de la police sur Hazard""", set(['internal', 'in text'])),
                make_tagged_url("http://www.lequipe.fr/Football/match/289914", u"""L'Equipe.fr""", set(['external', 'in text'])),
                make_tagged_url("http://www.lavenir.net/sports/cnt/DMF20130124_00259765", u"""Nous mettons tout en place pour interroger Hazard. Nous prenons cette affaire très au sérieux""", set(['internal', 'in text'])),
                make_tagged_url("http://www.lavenir.net/sports/cnt/DMF20130124_00259819", u"""Hazard échappe donc à des poursuites judiciaires""", set(['internal', 'in text'])),
                make_tagged_url("https://twitter.com/CHARLIEM0RGAN/status/294135719700602881", u"""__RENDERED_TWEET__""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("__EMBEDDED_VIDEO_URL__", u"""__EMBEDDED_VIDEO_TITLE__""", set([u'unfinished', 'video', 'external', 'embedded', 'ooyala'])),
                make_tagged_url("/sports/cnt/DMF20130126_00260499", u"""La FA veut plus de trois matches pour Hazard""", set(['bottom box', 'internal', 'related'])),
                make_tagged_url("http://www.lavenir.net/enimages", u"""En images""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/la-video-du-jour", u"""La vidéo du jour""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/filinfo/sports", u"""Sports""", set(['internal', 'keyword'])),
                make_tagged_url("http://www.lavenir.net/videos", u"""Vidéos""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/diables", u"""Diables rouges""", set(['internal', 'keyword'])),
                make_tagged_url("/sports/football/premierleague", u"""Premier League""", set(['internal', 'keyword'])),
            ]
            expected_links = urls
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



