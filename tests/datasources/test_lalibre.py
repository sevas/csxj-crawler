# coding=utf-8
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
                make_tagged_url("http://politictwist.blogs.lalibre.be/", u"Politic Twist, le blog politique décalé", set(['internal', 'sidebar box', 'internal site']))
            ]

            expected_bottom_links = [
                make_tagged_url("http://politictwist.blogs.lalibre.be/", u"Politic Twist, le blog politique décalé", set(['internal', 'bottom box', 'internal site']))
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
                make_tagged_url("www.forestnational.be", "www.forestnational.be", set(['external', 'in text', 'plaintext'])),
                make_tagged_url("www.stratos-sphere.com", "www.stratos-sphere.com", set(['external', 'in text', 'plaintext']))
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
                make_tagged_url("http://galeries.lalibre.be/album/actumonde/ouragansandy/15_21_01_171104928_624846-01-07.jpg/", u"""Les USA sur le pied de guerre avant le passage de Sandy""", set(['sidebar box', 'image gallery', 'internal'])),
                make_tagged_url("#embed_pos1", u"""Retrouvez les photos et les vidéos de l'ouragan""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos2", u"""Vidéo: Sandy vu de l'espace""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("#embed_pos3", u"""Sandy menace 50 millions d'Américains""", set(['internal', 'sidebar box', 'anchor'])),
            ]

            expected_bottom_links = [
                make_tagged_url("/societe/planete/article/774682/comment-choisit-on-le-nom-des-tempetes.html", u"""Comment choisit-on le nom des tempêtes?""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/774709/nouveau-numero-d-appel-d-urgence-pour-les-belges-aux-etats-unis.html", u"""Nouveau numéro d'appel d'urgence pour les Belges aux Etats-Unis""", set(['bottom box', 'internal'])),
                make_tagged_url("http://galeries.lalibre.be/album/actumonde/ouragansandy/15_21_01_171104928_624846-01-07.jpg/", u"""Les USA sur le pied de guerre avant le passage de Sandy""", set(['bottom box', 'internal', 'image gallery'])),
            ]

            expected_embbeded_media_links = [
                make_tagged_url("http://storify.com/pocket_pau/l-ouragan-sandy-menace-les-etats-unis", u"""View the story "L'ouragan Sandy menace les Etats-Unis" on Storify""", set(['external', 'embedded', 'script'])),
                make_tagged_url("http://www.ustream.tv/embed/recorded/26471477?v=3&wmode=direct", u"""http://www.ustream.tv/embed/recorded/26471477?v=3&wmode=direct""", set(['embedded', 'external', 'iframe'])),
                make_tagged_url("http://sa.kewego.com/swf/kp.swf?language_code=fr&width=510&height=383&playerKey=bf195c8ba4f5&configKey=&suffix=&sig=b5224f57c4cs&autostart=false", u"""Sandy menace 50 millions d'Américains""", set(['kplayer', 'video', 'external', 'embedded'])),
            ]

            expected_intext_links = [
                make_tagged_url("lalibre.be", u"lalibre.be", set(['in text', 'plaintext']))
            ]

            expected_links = expected_audio_links + expected_sidebox_links + expected_bottom_links + expected_embbeded_media_links + expected_intext_links
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

    def test_plaintext_links(self):
        """ lalibre parser correctly tags plaintext links """
        with open(os.path.join(DATA_ROOT, "plaintext_links.html")) as f:
            article, raw_html = lalibre.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/societe/gastronomie/article/785611/belgian-bubbles-un-produit-100-naturel-pour-des-fetes-reussies.html", u"""Belgian Bubbles, un produit 100% naturel pour des fêtes réussies""", set(['internal', 'sidebar box'])),
                make_tagged_url("/societe/gastronomie/article/787152/edito-crise-de-foie-gras.html", u"""Edito: Crise de foie (gras)""", set(['internal', 'sidebar box'])),
                make_tagged_url("/economie/entreprise-emploi/article/787084/upignac-a-la-gnaque.html", u"""Upignac a la gnaque""", set(['internal', 'sidebar box'])),
                make_tagged_url("/societe/gastronomie/article/785611/belgian-bubbles-un-produit-100-naturel-pour-des-fetes-reussies.html", u"""Belgian Bubbles, un produit 100% naturel pour des fêtes réussies""", set(['bottom box', 'internal'])),
                make_tagged_url("/societe/gastronomie/article/787152/edito-crise-de-foie-gras.html", u"""Edito: Crise de foie (gras)""", set(['bottom box', 'internal'])),
                make_tagged_url("/economie/entreprise-emploi/article/787084/upignac-a-la-gnaque.html", u"""Upignac a la gnaque""", set(['bottom box', 'internal'])),
                make_tagged_url("http://www.micronutris.com/", "http://www.micronutris.com/", set(['plaintext', 'external', 'in text']))
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_tweet(self):
        """ lalibre parser correctly extracts and tags embedded tweets (and a whole bunch of other links) """
        with open(os.path.join(DATA_ROOT, "embedded_tweet.html")) as f:
            article, raw_html = lalibre.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("https://twitter.com/JohnnySjh/status/282908799470292993", u"""https://twitter.com/JohnnySjh/status/282908799470292993""", set(['tweet', 'embedded media', 'external'])),
                make_tagged_url("/culture/people/article/785865/depardieu-apparait-en-chaise-roulante.html", u"""Depardieu apparaît... en chaise roulante""", set(['internal', 'sidebar box'])),
                make_tagged_url("/culture/people/article/784586/vous-soutenez-gerard-depardieu.html", u"""Vous soutenez Gérard Depardieu""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/international/article/785820/hollande-si-on-aime-la-france-on-doit-la-servir.html", u'''Hollande : "Si on aime la France, on doit la servir"''', set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/international/article/785045/gerard-depardieu-il-va-s-embeter-en-belgique-juge-cohn-bendit.html", u"""Gérard Depardieu? "Il va s'embêter" en Belgique juge Cohn-Bendit""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/international/article/784814/depardieu-qu-il-retourne-au-cinema-muet.html", u'''Depardieu, "Qu'il retourne au cinéma muet"''', set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/international/article/784820/riches-ils-ont-quitte-la-france.html", u"""Riches, ils ont quitté la France""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/international/article/784891/edito-minable.html", u"""Édito : Minable... ?""", set(['internal', 'sidebar box'])),
                make_tagged_url("/culture/people/article/785865/depardieu-apparait-en-chaise-roulante.html", u"""Depardieu apparaît... en chaise roulante""", set(['bottom box', 'internal'])),
                make_tagged_url("/culture/people/article/784586/vous-soutenez-gerard-depardieu.html", u"""Vous soutenez Gérard Depardieu""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/785820/hollande-si-on-aime-la-france-on-doit-la-servir.html", u'''Hollande : "Si on aime la France, on doit la servir"''', set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/785045/gerard-depardieu-il-va-s-embeter-en-belgique-juge-cohn-bendit.html", u"""Gérard Depardieu? "Il va s'embêter" en Belgique juge Cohn-Bendit""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/784814/depardieu-qu-il-retourne-au-cinema-muet.html", u'''Depardieu, "Qu'il retourne au cinéma muet"''', set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/784820/riches-ils-ont-quitte-la-france.html", u"""Riches, ils ont quitté la France""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/784891/edito-minable.html", u"""Édito : Minable... ?""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/international/article/787374/taxe-a-75-depardieu-reste-en-belgique.html", u"""Taxe à 75%: Depardieu reste en Belgique""", set(['bottom box', 'internal'])),
                make_tagged_url("/societe/cyber/article/788995/twitter-veut-le-feu-vert-de-la-justice-pour-denoncer-les-racistes.html", u"""Twitter veut le feu vert de la justice pour dénoncer les racistes""", set(['bottom box', 'internal'])),
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

    def test_links_intext_overload(self):
        """ lalibre parser is very good with plaintext links"""
        with open(os.path.join(DATA_ROOT, "links_intext_overload.html")) as f:
            article, raw_html = lalibre.extract_article_data(f)
            extracted_links = article.links
            updated_tagged_urls = [
                make_tagged_url("www.nyx.com", u"""www.nyx.com""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("europeanequities.nyx.com", u"""europeanequities.nyx.com""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("www.bourse.be", u"""www.bourse.be""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("www.beurs.be", u"""www.beurs.be""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("bourse.be", u"""bourse.be""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("http://www.londonstockexchange.com", u"""http://www.londonstockexchange.com""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("http://www.six-swiss-exchange.com/", u"""http://www.six-swiss-exchange.com/""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("http://deutsche-boerse.com", u"""http://deutsche-boerse.com""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("/economie/actualite/article/754828/le-jeu-video-sans-console-via-belgacom.html", u"""Le jeu vidéo sans console via Belgacom""", set(['internal', 'sidebar box'])),
                make_tagged_url("/economie/actualite/article/753635/suivre-les-cours-de-bourse-a-la-plage-gare-aux-plongeons.html", u"""Suivre les cours de Bourse à la plage ? Gare aux plongeons !""", set(['internal', 'sidebar box'])),
                make_tagged_url("/economie/actualite/article/752413/travailler-en-vacances-une-autre-facon-de-garder-la-ligne.html", u"""Travailler en vacances : une autre façon de garder la ligne !""", set(['internal', 'sidebar box'])),
                make_tagged_url("/economie/actualite/article/754828/le-jeu-video-sans-console-via-belgacom.html", u"""Le jeu vidéo sans console via Belgacom""", set(['bottom box', 'internal'])),
                make_tagged_url("/economie/actualite/article/753635/suivre-les-cours-de-bourse-a-la-plage-gare-aux-plongeons.html", u"""Suivre les cours de Bourse à la plage ? Gare aux plongeons !""", set(['bottom box', 'internal'])),
                make_tagged_url("/economie/actualite/article/752413/travailler-en-vacances-une-autre-facon-de-garder-la-ligne.html", u"""Travailler en vacances : une autre façon de garder la ligne !""", set(['bottom box', 'internal'])),
                make_tagged_url("/economie/actualite/article/755981/la-grece-lance-une-bataille-diplomatique.html", u"""La Grèce lance une bataille diplomatique""", set(['bottom box', 'internal'])),
                make_tagged_url("/economie/actualite/article/755996/apple-roi-de-la-bourse-us.html", u"""Apple, roi de la bourse US""", set(['bottom box', 'internal'])),
            ]
            expected_links = updated_tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_links_overload(self):
        with open(os.path.join(DATA_ROOT, "links_overload.html")) as f:
            article, raw_html = lalibre.extract_article_data(f)
            extracted_links = article.links
            updated_tagged_urls = [
                make_tagged_url("http://www.lalibre.be/economie/actualite/article/800148/caterpillar-un-plan-industriel-qui-vise-a-assurer-la-viabilite-du-site-de-gosselies.html", u"""suppression de 1.400 emplois à Gosselies""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/799466/geert-bourgeois-refuse-de-nommer-les-3-bourgmestres.html", u"""non-nomination des bourgmestres de la périphérie bruxelloise""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/798203/le-drole-de-marche-de-la-presidente-du-cpas-d-anvers.html", u"""xénophobie au CPAS d'Anvers""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/bruxelles/article/795824/le-molenbeek-de-schepmans-polit-deja-son-image.html", u"""Françoise Schepmans""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/bruxelles/article/795824/le-molenbeek-de-schepmans-polit-deja-son-image.html", u"""une interview à LaLibre""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/799929/destexhe-veut-barrer-la-route-aux-extremistes-musulmans.html", u"""comme l'a soutenu cette semaine Alain Destexhe""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/politique-belge/article/799742/cerexhe-j-ai-parfois-eu-l-impression-de-coller-des-rustines.html", u"""vanté de ses neuf ans au ministère de l'Emploi""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/799203/picque-encore-et-toujours-picque.html", u"""cote de popularité grimpe""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/politique-belge/article/790019/didier-reynders-dirigera-le-mr-a-bruxelles.html", u"""à la tête de la Régionale bruxelloise du MR""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/799203/picque-encore-et-toujours-picque.html", u"""notre Baromètre politique""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/politique-belge/article/798988/magnette-ce-che-guevara-du-pauvre.html", u"""pas tardé à réagir""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/belgique/article/799750/pourquoi-magnette-a-t-il-sorti-l-artillerie-lourde.html", u"""vivement critiqué le MR""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/politique-belge/article/799747/ps-et-mr-larrons-en-foire-ou-alliance-contre-nature.html", u"""l'alliance PS-MR""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("http://www.lalibre.be/actu/politique-belge/article/798882/barometre-la-n-va-persiste-et-signe.html", u"""N-VA""", set(['internal', 'internal site', 'in text'])),
                make_tagged_url("lalibre.be", u"""lalibre.be""", set(['plaintext', 'external', 'in text'])),
                make_tagged_url("/actu/politique-belge/article/800666/schepmans-philippe-moureaux-a-pourtant-le-temps-pour-une-serieuse-psychanalyse.html", u'''Schepmans: Philippe Moureaux "a pourtant le temps pour une sérieuse psychanalyse"''', set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/politique-belge/article/799747/ps-et-mr-larrons-en-foire-ou-alliance-contre-nature.html", u"""PS et MR : larrons en foire ou alliance contre-nature?""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/belgique/article/799929/destexhe-veut-barrer-la-route-aux-extremistes-musulmans.html", u"""Destexhe veut barrer la route aux extrémistes musulmans""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/belgique/article/799750/pourquoi-magnette-a-t-il-sorti-l-artillerie-lourde.html", u"""Pourquoi Magnette a-t-il sorti lartillerie lourde ?""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/belgique/article/799203/picque-encore-et-toujours-picque.html", u"""Picqué, encore et toujours Picqué""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/politique-belge/article/798988/magnette-ce-che-guevara-du-pauvre.html", u'''Magnette, "ce Che Guevara du pauvre"''', set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/belgique/article/799466/geert-bourgeois-refuse-de-nommer-les-3-bourgmestres.html", u"""Geert Bourgeois refuse de nommer les 3 bourgmestres""", set(['internal', 'sidebar box'])),
                make_tagged_url("/actu/politique-belge/article/800666/schepmans-philippe-moureaux-a-pourtant-le-temps-pour-une-serieuse-psychanalyse.html", u'''Schepmans: Philippe Moureaux "a pourtant le temps pour une sérieuse psychanalyse"''', set(['bottom box', 'internal'])),
                make_tagged_url("/actu/politique-belge/article/799747/ps-et-mr-larrons-en-foire-ou-alliance-contre-nature.html", u"""PS et MR : larrons en foire ou alliance contre-nature?""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/belgique/article/799929/destexhe-veut-barrer-la-route-aux-extremistes-musulmans.html", u"""Destexhe veut barrer la route aux extrémistes musulmans""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/belgique/article/799750/pourquoi-magnette-a-t-il-sorti-l-artillerie-lourde.html", u"""Pourquoi Magnette a-t-il sorti lartillerie lourde ?""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/belgique/article/799203/picque-encore-et-toujours-picque.html", u"""Picqué, encore et toujours Picqué""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/politique-belge/article/798988/magnette-ce-che-guevara-du-pauvre.html", u'''Magnette, "ce Che Guevara du pauvre"''', set(['bottom box', 'internal'])),
                make_tagged_url("/actu/politique-belge/article/799742/cerexhe-j-ai-parfois-eu-l-impression-de-coller-des-rustines.html", u'''Cerexhe: "Jai parfois eu limpression de coller des rustines"''', set(['bottom box', 'internal'])),
                make_tagged_url("/actu/belgique/article/799466/geert-bourgeois-refuse-de-nommer-les-3-bourgmestres.html", u"""Geert Bourgeois refuse de nommer les 3 bourgmestres""", set(['bottom box', 'internal'])),
                make_tagged_url("/actu/politique-belge/article/800672/bourgmestre-un-metier-a-risques.html", u"""Bourgmestre, un métier à risques""", set(['bottom box', 'internal'])),
            ]
            expected_links = updated_tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_vuvox_without_title(self):
        """ lalibre parser extracts embedded vuvox objects without title"""
        with open(os.path.join(DATA_ROOT, "vuvox_without_title.html")) as f:
            article, raw_html = lalibre.extract_article_data(f)
            extracted_links = article.links
            updated_tagged_urls = [
                make_tagged_url("#embed_pos1", u"""Vidéo : Comment prendre des photos au fond de la piscine ?""", set(['internal', 'sidebar box', 'anchor'])),
                make_tagged_url("/sports/omnisports/article/753960/les-belges-aux-jeux-pas-de-podium-pour-van-alphen-qui-finit-4e.html", u"""Les Belges aux Jeux: pas de podium pour Van Alphen qui finit 4e""", set(['internal', 'sidebar box'])),
                make_tagged_url("http://galeries.lalibre.be/album/omnisports/JO2012/insolites/34.jpg/", u"""Toutes les photos insolites des JO""", set(['internal', 'sidebar box', 'image gallery'])),
                make_tagged_url("http://ask.blogs.lalibre.be/", u"""Ask LaLibre, le blog qui vous permet de tout savoir""", set(['internal', 'sidebar box', 'jblog'])),
                make_tagged_url("/sports/omnisports/article/753960/les-belges-aux-jeux-pas-de-podium-pour-van-alphen-qui-finit-4e.html", u"""Les Belges aux Jeux: pas de podium pour Van Alphen qui finit 4e""", set(['bottom box', 'internal'])),
                make_tagged_url("/sports/omnisports/article/754784/water-polo-coups-de-boule-et-coups-de-maillots-sous-l-eau.html", u"""Water polo: coups de boule et coups de maillots sous l'eau""", set(['bottom box', 'internal'])),
                make_tagged_url("http://ask.blogs.lalibre.be/", u"""Ask LaLibre, le blog qui vous permet de tout savoir""", set(['bottom box', 'internal', 'jblog'])),
                make_tagged_url("http://galeries.lalibre.be/album/omnisports/JO2012/insolites/34.jpg/", u"""Toutes les photos insolites des JO""", set(['bottom box', 'internal', 'image gallery'])),
                make_tagged_url("http://www.vuvox.com/collage_express/collage.swf?collageID=05bf5f41ae", u"""http://www.vuvox.com/collage_express/collage.swf?collageID=05bf5f41ae""", set(['external', 'embedded'])),
            ]
            expected_links = updated_tagged_urls
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

            expected_content = [u"MoussDioufa\xe9t\xe9r\xe9v\xe9l\xe9augrandpublicgr\xe2ce\xe0soninterpr\xe9tationdulieutenantN'Gumadanslas\xe9riefran\xe7aiseJulieLescaut.V\xe9roniqueGenestestrest\xe9tr\xe8sprochedeMoussDioufapr\xe8ssonaccidentvasculairec\xe9r\xe9bral.Ellear\xe9agisurTwittersuiteaud\xe9c\xe8sdel'acteur.", u'']
            eq_(article.content, expected_content, msg=u"\n{0}\n{1}".format(article.content, expected_content))
