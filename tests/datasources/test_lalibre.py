# -*- coding: utf-8 -*-
"""
Link extraction test suite for lalibre.py
"""

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import lalibre

from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', lalibre.SOURCE_NAME)


class TestLalibreLinkExtraction(object):
    def test_same_sidebox_and_bottom_links(self):
        """ lalibre parser can extract bottom links from an article. """
        with open(os.path.join(DATA_ROOT, "links_single_bottom_sidebox_link.html")) as f:
            article, _ = lalibre.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("http://politictwist.blogs.lalibre.be/", u"Politic Twist, le blog politique décalé", set(['sidebar box', 'internal site']))
            ]

            expected_bottom_links = [
                make_tagged_url("http://politictwist.blogs.lalibre.be/", u"Politic Twist, le blog politique décalé", set(['bottom box', 'internal site']))
            ]

            expected_links = expected_bottom_links + expected_sidebox_links
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_removed_article(self):
        """ lalibre parser returns None when processing a removed article """
        with open(os.path.join(DATA_ROOT, "links_removed_article.html")) as f:
            article, _ = lalibre.extract_article_data(f)
            eq_(article, None)

    def test_intext_links(self):
        """ lalibre parser can extract in-text urls"""
        with open(os.path.join(DATA_ROOT, "links_intext.html")) as f:
            article, _ = lalibre.extract_article_data(f)
            extracted_links = article.links

            expected_intext_links = [
                make_tagged_url("http://www.ticketnet.be/fr/manifestation/idmanif/5918", u'''"Est-ce qu'on ne pourrait pas s'aimer un peu?"''', set(['external', 'in text'])),
                make_tagged_url("http://www.stratos-sphere.com/", u"""Stratos-Sphere""", set(['external', 'in text'])),
                make_tagged_url("http://www.forestnational.be/fr/", u"""dEUS""", set(['external', 'in text'])),
                make_tagged_url("http://www.madamemoustache.be/page/Upcoming/101/16122011-JoyeuxBordelpresentFUCKYOUITSMAGIC.html", u""" FUCK YOU IT S XMAS""", set(['external', 'in text'])),
                make_tagged_url("http://www.netevents.be/fr/soiree/203907/Chez-Maman-fete-ses-17-ans/", u'''"Chez maman"''', set(['external', 'in text'])),
                make_tagged_url("", u"""Super Saturday""", set(['no target', 'in text'])),
            ]

            assert_taggedURLs_equals(expected_intext_links, extracted_links)

    def test_storify_sidebox_bottom_links(self):
        """ lalibre parser can extract embedded storify links """
        with open(os.path.join(DATA_ROOT, "links_storify_sidebox_bottom_links.html")) as f:
            article, _ = lalibre.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u'''Le storify dédié à "Chevaux et baïonnettes"''', set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/actu/usa-2012/article/773103/obama-depeint-un-romney-incompetent-en-politique-etrangere.html", u"""Obama dépeint un Romney incompétent en politique étrangère""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/usa-2012/article/773295/coup-de-mou-pour-un-dirigeable-de-mitt-romney.html", u"""Coup de mou pour un dirigeable de Mitt Romney""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/usa-2012/article/773089/obama-et-romney-a-egalite-avant-le-dernier-debat.html", u"""Obama et Romney à égalité avant le dernier débat""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/usa-2012/article/772885/reelu-obama-devrait-continuer-la-guerre-secrete-contre-al-qaida.html", u"""Réélu, Obama devrait continuer la "guerre secrète" contre Al-Qaïda""", set(['internal', 'sidebar box'])),
            ]

            expected_bottom_links = [
                make_tagged_url("/actu/usa-2012/article/773103/obama-depeint-un-romney-incompetent-en-politique-etrangere.html", u"""Obama dépeint un Romney incompétent en politique étrangère""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/773089/obama-et-romney-a-egalite-avant-le-dernier-debat.html", u"""Obama et Romney à égalité avant le dernier débat""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/772885/reelu-obama-devrait-continuer-la-guerre-secrete-contre-al-qaida.html", u"""Réélu, Obama devrait continuer la "guerre secrète" contre Al-Qaïda""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/773295/coup-de-mou-pour-un-dirigeable-de-mitt-romney.html", u"""Coup de mou pour un dirigeable de Mitt Romney""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/773304/mais-qu-ont-elles-de-si-interessant-ces-notes.html", u"""Mais qu'ont-elles de si intéressant ces notes?""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/773547/usa-virgil-goode-le-petit-candidat-qui-pourrait-jouer-un-grand-role.html", u"""USA : Virgil Goode, le petit candidat qui pourrait jouer un grand rôle""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/773578/la-tournee-effrenee-de-barack-obama.html", u"""La tournée effrénée de Barack Obama""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/773807/obama-a-t-il-traite-romney-de-bullshitter.html", u"""Obama a-t-il traité Romney de "bullshitter" ?""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/usa-2012/article/774012/que-peut-on-attendre-d-un-deuxieme-mandat-de-barack-obama.html", u"""Que peut-on attendre dun deuxième mandat de Barack Obama ?""", set(['bottom box', 'internal'])),
            ]

            expected_embbeded_media_links = [
                make_tagged_url("http://storify.com/pocket_pau/chyevaux-et-baionnettes-invites-surprises-du-derni", u"""View the story "Chevaux et baïonnettes, invités surprises du dernier débat " on Storify""", set(['external', 'embedded', 'script'])),
            ]

            expected_links = expected_sidebox_links + expected_bottom_links + expected_embbeded_media_links
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_storify_embedded_video_links(self):
        """ lalibre parser can process an article with an embedded storify and embedded videos """
        with open(os.path.join(DATA_ROOT, "links_storify_video_links.html")) as f:
            article, _ = lalibre.extract_article_data(f)
            extracted_links = article.links

            expected_audio_links = [
                make_tagged_url("http://podcast.lalibre.be/articles/audio_llb_774524_1351533121.mp3", u"""Ecoutez Georges Dallemagne dans Les Flingueurs de l'info sur Twizz Radio""", set(['audio', 'sidebar box', 'internal site', 'embedded'])),
            ]

            expected_sidebox_links = [
                make_tagged_url("http://galeries.lalibre.be/album/actumonde/ouragansandy/15_21_01_171104928_624846-01-07.jpg/", u"""Les USA sur le pied de guerre avant le passage de Sandy""", set(['sidebar box', 'internal site'])),
                make_tagged_url("#embed_pos1", u"""Retrouvez les photos et les vidéos de l'ouragan""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos2", u"""Vidéo: Sandy vu de l'espace""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos3", u"""Sandy menace 50 millions d'Américains""", set(['internal', 'sidebar box', 'anchor'])),
            ]

            expected_bottom_links = [
                make_tagged_url("/societe/planete/article/774682/comment-choisit-on-le-nom-des-tempetes.html", u"""Comment choisit-on le nom des tempêtes?""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/774709/nouveau-numero-d-appel-d-urgence-pour-les-belges-aux-etats-unis.html", u"""Nouveau numéro d'appel d'urgence pour les Belges aux Etats-Unis""", set(['bottom box', 'internal'])),
                make_tagged_url("http://galeries.lalibre.be/album/actumonde/ouragansandy/15_21_01_171104928_624846-01-07.jpg/", u"""Les USA sur le pied de guerre avant le passage de Sandy""", set(['bottom box', 'internal site'])),
            ]

            expected_embbeded_media_links = [
                make_tagged_url("http://storify.com/pocket_pau/l-ouragan-sandy-menace-les-etats-unis", u"""View the story "L'ouragan Sandy menace les Etats-Unis" on Storify""", set(['external', 'embedded', 'script'])),
                make_tagged_url("http://www.ustream.tv/embed/recorded/26471477?v=3&wmode=direct", u"""http://www.ustream.tv/embed/recorded/26471477?v=3&wmode=direct""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=b5224f57c4cs&autostart=false", u"""Sandy menace 50 millions d'Américains""", set(['kplayer', 'video', 'external', 'embedded'])),
            ]

            expected_links = expected_audio_links + expected_sidebox_links + expected_bottom_links + expected_embbeded_media_links
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_videos_links(self):
        """ lalibre parser can process an article with embedded videos """
        with open(os.path.join(DATA_ROOT, "links_embedded_videos.html")) as f:
            article, _ = lalibre.extract_article_data(f)
            extracted_links = article.links

            expected_sidebox_links = [
                make_tagged_url("#embed_pos1", u"""L'incroyable but de Mexès face à Anderlecht""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("http://infosports.lalibre.be/football/ligue-des-champions/phase-de-groupes/groupe-f/rencontre/209126/anderlecht-ac-milan/direct", u"""Revivez la rencontre Anderlecht-Milan""", set(['sidebar box', 'internal site'])),
                make_tagged_url("http://betfirst.dhnet.be", u"""Faites vos paris sportifs""", set(['sidebar box', 'external'])),
                make_tagged_url("http://infosports.lalibre.be/football/ligue-des-champions/phase-de-groupes/groupe-c/resultats", u"""Les résultats et classements de Ligue des Champions""", set(['sidebar box', 'internal site'])),
                make_tagged_url("#embed_pos5", u'''Deschacht : "pas d'excuse, je devais marquer"''', set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos3", u'''Proto : "jamais pris un but comme ça"''', set(['internal', 'sidebar box', 'anchor'])),
            ]

            expected_bottom_links = [
                make_tagged_url("/sports/football/article/779271/genk-qualifie-un-match-avant-la-fin.html", u"""Genk qualifié un match avant la fin""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/football/article/779281/bruges-sort-sans-gloire-de-l-europa-league-1-2.html", u"""Bruges sort sans gloire de l'Europa League (1-2)""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/football/article/780016/jamais-l-horizon-mauve-n-aura-paru-aussi-degage.html", u"""Jamais lhorizon mauve naura paru aussi dégagé""", set(['bottom box', 'internal'])),
                make_tagged_url("http://infosports.lalibre.be/football/ligue-des-champions/phase-de-groupes/groupe-f/rencontre/209126/anderlecht-ac-milan/direct", u"""Revivez la rencontre Anderlecht-Milan""", set(['bottom box', 'internal site'])),
                make_tagged_url("http://betfirst.dhnet.be", u"""Faites vos paris sportifs""", set(['bottom box', 'external'])),
                make_tagged_url("http://infosports.lalibre.be/football/ligue-des-champions/phase-de-groupes/groupe-c/resultats", u"""Les résultats et classements de Ligue des Champions""", set(['bottom box', 'internal site'])),
            ]

            expected_embbeded_media_links = [
                make_tagged_url("http://www.youtube.com/embed/C8Z3yoIfUqc", u"""http://www.youtube.com/embed/C8Z3yoIfUqc""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=b10774aee0es&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=ca8cdb85890s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=b79fc6ccc1bs&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=1b2b29b8280s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=d68d7e19b04s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
            ]

            expected_links = expected_sidebox_links + expected_bottom_links + expected_embbeded_media_links
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_same_owner_tagging(self):
        """ lalibre parser correctly tags 'same owner' links """
        with open(os.path.join(DATA_ROOT, "links_same_owner_tagging.html")) as f:
            article, raw_html = lalibre.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/societe/sciences-sante/article/779520/ejaculation-precoce-le-remede-medical-miracle.html", u"""Éjaculation précoce: le remède médical miracle?""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://www.essentielle.be/", u"""Essentielle.be, le site des femmes actives""", set(['sidebar box', 'external', 'same owner'])),
                make_tagged_url("/societe/general/article/774960/amitie-hommefemme-possible.html", u"""Amitié homme/femme, possible?""", set(['internal', 'sidebar box'])),
                make_tagged_url("/societe/general/article/774515/la-meilleure-musique-pendant-le-sexe-est.html", u"""La meilleure musique pendant le sexe est""", set(['internal', 'sidebar box'])),
                make_tagged_url("/societe/general/article/773803/ces-etudiantes-qui-commercialisent-leur-corps.html", u"""Ces étudiantes qui commercialisent leur corps""", set(['internal', 'sidebar box'])),
                make_tagged_url("/societe/general/article/772893/qui-des-hommes-ou-des-femmes-mentent-le-plus.html", u"""Qui des hommes ou des femmes mentent le plus ?""", set(['internal', 'sidebar box'])),
                make_tagged_url("/societe/sciences-sante/article/779520/ejaculation-precoce-le-remede-medical-miracle.html", u"""Éjaculation précoce: le remède médical miracle?""", set(['bottom box', 'internal'])),
                make_tagged_url("/societe/general/article/774960/amitie-hommefemme-possible.html", u"""Amitié homme/femme, possible?""", set(['bottom box', 'internal'])),
                make_tagged_url("/societe/general/article/774515/la-meilleure-musique-pendant-le-sexe-est.html", u"""La meilleure musique pendant le sexe est""", set(['bottom box', 'internal'])),
                make_tagged_url("/societe/general/article/773803/ces-etudiantes-qui-commercialisent-leur-corps.html", u"""Ces étudiantes qui commercialisent leur corps""", set(['bottom box', 'internal'])),
                make_tagged_url("/societe/general/article/772893/qui-des-hommes-ou-des-femmes-mentent-le-plus.html", u"""Qui des hommes ou des femmes mentent le plus ?""", set(['bottom box', 'internal'])),
                make_tagged_url("http://www.essentielle.be/", u"""Essentielle.be, le site des femmes actives""", set(['bottom box', 'external', 'same owner'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_extract_embedded_tweets(self):
        """ lalibre parser can extract rendered tweets from within the text content """

        with open(os.path.join(DATA_ROOT, "links_extract_embedded_tweets.html")) as f:
            article, raw_html = lalibre.extract_article_data(f)
            extracted_links = article.links
            embedded_content_links = [
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=c7acd5f9065s&autostart=false", u"""__NO_TITLE__""", set(['kplayer', 'video', 'external', 'embedded'])),
            ]
            bottom_links = [
                make_tagged_url("/actu/belgique/article/786880/sierre-la-presse-epinglee.html", u"""Sierre :  la presse épinglée""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/belgique/article/789293/une-liste-verte-pour-les-autocars.html", u"""Une liste verte pour les autocars ?""", set(['bottom box', 'internal'])),
            ]
            associated_tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Grosse frayeur en Suisse""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/actu/belgique/article/786880/sierre-la-presse-epinglee.html", u"""Sierre :  la presse épinglée""", set(['internal', 'sidebar box'])),
            ]
            embedded_audio_links = [
            ]
            in_text_links = [
                make_tagged_url("https://twitter.com/maximedaye/status/288587213661421568", u"""https://twitter.com/maximedaye/status/288587213661421568""", set(['tweet', 'embedded media', 'external'])),
            ]
            expected_links = embedded_content_links + bottom_links + associated_tagged_urls + embedded_audio_links + in_text_links
            assert_taggedURLs_equals(expected_links, extracted_links)


class TestLalibreContentExtraction(object):
    def test_clean_paragraph_extraction(self):
        """ lalibre parser extracts the paragraphs as a list of strings without bullshit characters (e.g. \\t, \\r, \\n)"""
        with open(os.path.join(DATA_ROOT, "content_paragraphs_overload.html")) as f:
            article, _ = lalibre.extract_article_data(f)
            content = article.content

            eq_(len(content), 45)
            for line in content:
                stripped_line = line.strip('\t\r\n')
                eq_(line, stripped_line)

    def test_clean_intro_extraction(self):
        """ lalibre parser extracts the 'articleHat' div as the intro field"""
        with open(os.path.join(DATA_ROOT, "content_intro_articleHat.html")) as f:
            article, _ = lalibre.extract_article_data(f)

            expected_intro = u"Une enquête a été ouverte pour déterminer les causes de l'incendie."
            eq_(article.intro, expected_intro)

    def test_no_paragraphs(self):
        """ lalibre parser extracts text content even if there are no paragraphs"""
        with open(os.path.join(DATA_ROOT, "content_no_paragraphs.html")) as f:
            article, _ = lalibre.extract_article_data(f)

            expected_content = [u"Mouss Diouf a été révélé au grand public grâce à son interprétation du lieutenant N'Guma dans la série française Julie Lescaut. \r\n\r\nVéronique Genest est resté très proche de Mouss Diouf après son accident vasculaire cérébral. Elle a réagi sur Twitter suite au décès de l'acteur."]
            eq_(article.content, expected_content, msg="\n{0}\n{1}".format(article.content, expected_content))
