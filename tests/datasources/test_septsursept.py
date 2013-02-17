# coding=utf-8

import os
from nose.tools import eq_

from csxj.common.tagging import make_tagged_url
from csxj.datasources import septsursept
from csxj.datasources.septsursept import separate_articles_and_photoalbums
from csxj_test_tools import assert_taggedURLs_equals

DATA_ROOT = os.path.join(os.path.dirname(__file__), 'test_data', 'septsursept')

class TestFrontpageItemsFilter(object):
    def setUp(self):
        self.article_item = (u"Some Article", "http://www.7sur7.be/7s7/fr/1504/Insolite/article/detail/1494529/2012/09/02/Ils-passent-devant-une-vitrine-avant-de-disparaitre.dhtml")
        self.photoalbum_item = (u"Some photoalbum", "http://www.7sur7.be/7s7/fr/8024/Stars/photoalbum/detail/85121/1212631/0/Showbiz-en-images.dhtml")
        self.video_item = (u"Some video", "http://www.7sur7.be/7s7/fr/3846/Sports/video/detail/1436930/Lucescu-degoute-par-la-douche-du-titre.dhtml")

    def test_photoalbum_filter(self):
        """ The 7sur7.be frontpage items filter can separate photoalbum url from regular news items. """
        frontpage_items = [self.article_item, self.photoalbum_item]

        expected_news, expected_junk = [self.article_item], [self.photoalbum_item]
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)

    def test_nothing_to_filter(self):
        """ The 7sur7.be frontpage items filter does nothing to a list of urls with no photoalbum or video. """
        frontpage_items = [self.article_item]

        expected_news, expected_junk = [self.article_item], []
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)

    def test_video_filter(self):
        """ The 7sur7.be frontpage items filter can separate video urls from regular news items. """
        frontpage_items = [self.article_item, self.video_item]

        expected_news, expected_junk = [self.article_item], [self.video_item]
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)

    def test_filter(self):
        """ The 7sur7.be frontpage items filter can separate photoalbum and video urls from regular news items from regular news items. """
        frontpage_items = [self.photoalbum_item, self.article_item, self.video_item]

        expected_news, expected_junk = [self.article_item], [self.photoalbum_item, self.video_item]
        observed_news, observed_junk = separate_articles_and_photoalbums(frontpage_items)

        eq_(expected_news, observed_news)
        eq_(expected_junk, observed_junk)



class Test7sur7LinkExtraction(object):
    def test_embedded_tweets(self):
        """ The 7sur7.be parser can extract and tag embedded tweets (as well as sidebar box links, bottom box links). """
        with open(os.path.join(DATA_ROOT, "embedded_tweets.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/7s7/fr/1505/Monde/article/detail/1451992/2012/06/11/Nadine-Morano-n-a-aucun-etat-d-ame-a-en-appeler-aux-electeurs-du-FN.dhtml", u"""Nadine Morano n'a "aucun état d'âme" à en appeler aux électeurs du FN""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1438967/2012/05/15/La-sortie-dramatique-ratee-de-Nicolas-Bedos-sur-Twitter.dhtml", u"""La sortie dramatique ratée de Nicolas Bedos sur Twitter""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1434935/2012/05/08/Gros-clash-entre-Nicolas-Bedos-et-Mathieu-Kassovitz.dhtml", u"""Gros clash entre Nicolas Bedos et Mathieu Kassovitz""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1528/Cinema/article/detail/1425335/2012/04/18/Mathieu-Kassovitz-attaque-Frederic-Beigbeder.dhtml", u"""Mathieu Kassovitz attaque Frédéric Beigbeder""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1505/Monde/article/detail/1451992/2012/06/11/Nadine-Morano-n-a-aucun-etat-d-ame-a-en-appeler-aux-electeurs-du-FN.dhtml", u"""Nadine Morano n'a "aucun état d'âme" à en appeler aux électeurs du FN""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1438967/2012/05/15/La-sortie-dramatique-ratee-de-Nicolas-Bedos-sur-Twitter.dhtml", u"""La sortie dramatique ratée de Nicolas Bedos sur Twitter""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1527/People/article/detail/1434935/2012/05/08/Gros-clash-entre-Nicolas-Bedos-et-Mathieu-Kassovitz.dhtml", u"""Gros clash entre Nicolas Bedos et Mathieu Kassovitz""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/230/Stars-internationales/actualite/index.dhtml", u"""Stars internationales""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/707974156/Twitter/actualite/index.dhtml", u"""Twitter""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("https://twitter.com/nadine__morano/status/209732333727780865", u"""https://twitter.com/nadine__morano/status/209732333727780865""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("https://twitter.com/kassovitz/status/212186904848900097", u"""https://twitter.com/kassovitz/status/212186904848900097""", set(['tweet', 'external', 'embedded'])),
                make_tagged_url("https://twitter.com/kassovitz/status/212189899279970304", u"""https://twitter.com/kassovitz/status/212189899279970304""", set(['tweet', 'external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_document(self):
        """ The 7sur7.be parser can extract and tag link to embedded document """
        with open(os.path.join(DATA_ROOT, "embedded_document.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("/7s7/fr/1502/Belgique/article/detail/1529567/2012/11/06/Forte-augmentation-du-nombre-de-demandeurs-d-asile-venant-de-Syrie.dhtml", u"""Forte augmentation du nombre de demandeurs d'asile venant de Syrie""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1502/Belgique/article/detail/1522934/2012/10/24/Le-code-de-la-nationalite-durci.dhtml", u"""Le code de la nationalité durci""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1502/Belgique/article/detail/1522338/2012/10/23/Regroupement-familial-refus-de-visas-a-foison.dhtml", u"""Regroupement familial: refus de visas à foison""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/1445/immigration/actualite/index.dhtml", u"""immigration""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/152/Politique/actualite/index.dhtml", u"""Politique""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/972/Geert-Bourgeois/actualite/index.dhtml", u"""Geert Bourgeois""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/1135/N-VA/actualite/index.dhtml", u"""N-VA""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("http://static1.7sur7.be/static/asset/2012/BOEKJE_FR_181.pdf", u"""Téléchargez pdf""", set(['internal', 'internal site', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_embedded_video_and_in_text_links(self):
        """ The 7sur7.be parser can extract and tag embedded video, in-text links, link to document"""
        with open(os.path.join(DATA_ROOT, "embedded_video_and_in_text_links.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.facebook.com/pages/Carine-Gilson-Lingerie-Couture/161436673890010", u"""page Facebook""", set(['external', 'in text'])),
                make_tagged_url("http://www.carinegilson.com/", u"""http://www.carinegilson.com/""", set(['external', 'in text'])),
                make_tagged_url("/7s7/fr/1525/Tendances/article/detail/1517986/2012/10/16/Un-nouveau-fiasco-Photoshop.dhtml", u"""Un nouveau fiasco Photoshop""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1525/Tendances/article/detail/1515857/2012/10/12/Les-talons-de-la-mort.dhtml", u"""Les talons de la mort""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1525/Tendances/article/detail/1515660/2012/10/12/Des-bijoux-tres-intimes.dhtml", u"""Des bijoux très intimes""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/400619/Tendances/actualite/index.dhtml", u"""Tendances""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/558/Entreprises/actualite/index.dhtml", u"""Entreprises""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("http://static1.7sur7.be/static/asset/2012/Look_book_CG_Couture_SS_012_dff_low_41.pdf", u"""Téléchargez pdf""", set(['internal', 'internal site', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/mDzPISNuHCs/?wmode=opaque", u"""http://www.youtube.com/embed/mDzPISNuHCs/?wmode=opaque""", set(['external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

    def test_many_embedded_videos_and_links(self):
        """ The 7sur7.be parser can extract and tag many embedded video in one article"""
        with open(os.path.join(DATA_ROOT, "many_embedded_videos_and_links.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.7sur7.be/7s7/fr/1748/Open-d-Australie/article/detail/1381644/2012/01/18/Baghdatis-fracasse-4-raquettes-en-25-secondes-video.dhtml", u"""Marcos Baghdatis - Stanislas Wawrinka, Australian Open 2012""", set(['internal', 'in text'])),
                make_tagged_url("http://www.7sur7.be/7s7/fr/1513/tennis/article/detail/227704/2008/04/02/Furax-Youzhny-s-ouvre-le-crane-avec-sa-raquette.dhtml", u"""Mikhail Youzhny - Nicolas Almagro, Miami, 2008""", set(['internal', 'in text'])),
                make_tagged_url("http://www.7sur7.be/7s7/fr/1513/tennis/article/detail/1109699/2010/05/25/Verdasco-a-Gasquet-Su-puta-madre.dhtml", u"""Fernando Verdasco - Richard Gasquet, Open de Nice, 2010""", set(['internal', 'in text'])),
                make_tagged_url("http://www.7sur7.be/newslettersports", u"""Inscrivez-vous à la newsletter sports de 7sur7 et recevez chaque jour les dernières infos sports""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1513/tennis/article/detail/1489797/2012/08/22/Darcis-se-paye-Roddick.dhtml", u"""Darcis se paye Roddick""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1513/tennis/article/detail/1489306/2012/08/22/Wickmayer-eliminee-a-Dallas-Darcis-au-3e-tour-a-Salem.dhtml", u"""Wickmayer éliminée à Dallas, Darcis au 3e tour à Salem""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1513/tennis/article/detail/1489235/2012/08/21/Goffin-affrontera-Kubot-en-1-8e-de-finale-a-Winston-Salem.dhtml", u"""Goffin affrontera Kubot en 1/8e de finale à Winston-Salem""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/26/Hors-jeu/actualite/index.dhtml", u"""Hors-jeu""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("http://www.youtube.com/embed/Oe6uLXaAnhQ/?wmode=opaque", u"""http://www.youtube.com/embed/Oe6uLXaAnhQ/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/lKRaOgL6_-c/?wmode=opaque", u"""http://www.youtube.com/embed/lKRaOgL6_-c/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/QqrCuIB76gs/?wmode=opaque", u"""http://www.youtube.com/embed/QqrCuIB76gs/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/g7kS68T6ptA/?wmode=opaque", u"""http://www.youtube.com/embed/g7kS68T6ptA/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/ekQ_Ja02gTY/?wmode=opaque", u"""http://www.youtube.com/embed/ekQ_Ja02gTY/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/fi-CgSO9Evw/?wmode=opaque", u"""http://www.youtube.com/embed/fi-CgSO9Evw/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/YQ2ssjDKWvk/?wmode=opaque", u"""http://www.youtube.com/embed/YQ2ssjDKWvk/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/bnREpkrIhRM/?wmode=opaque", u"""http://www.youtube.com/embed/bnREpkrIhRM/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/C8Nyc9jzSDg/?wmode=opaque", u"""http://www.youtube.com/embed/C8Nyc9jzSDg/?wmode=opaque""", set(['external', 'embedded'])),
                make_tagged_url("http://www.youtube.com/embed/FaaezNd7ykg/?wmode=opaque", u"""http://www.youtube.com/embed/FaaezNd7ykg/?wmode=opaque""", set(['external', 'embedded'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)


    def test_same_owner(self):
        """ The 7sur7.be parser can extract and tag links to 'same owner' sites (and a couple of others)"""
        with open(os.path.join(DATA_ROOT, "same_owner.html")) as f:
            article, raw_html = septsursept.extract_article_data(f)
            extracted_links = article.links
            tagged_urls = [
                make_tagged_url("http://www.7sur7.be/7s7/fr/1745/Standard/article/detail/1506809/2012/09/25/Jelle-Van-Damme-menace-De-Ceuninck-Fais-attention-toi.dhtml", u"""Si la tension est clairement montée entre Jelle Van Damme et Benjamin Deceuninck hier soir à Mouscron""", set(['internal', 'in text'])),
                make_tagged_url("http://www.7sur7.be/7s7/fr/1745/Standard/article/detail/1506951/2012/09/26/Deceuninck-Je-ne-me-suis-pas-senti-menace.dhtml", u'''Le journaliste de la RTBF ne s'est pas "senti menacé"''', set(['internal', 'in text'])),
                make_tagged_url("http://www.standard.be/multimedia/videos/details-video/~itv-jelle-van-damme.htm?lng=fr#.UGMIPnI4SSo", u'''"Standard TV".''', set(['external', 'in text'])),
                make_tagged_url("http://www.standard.be/multimedia/videos/details-video/~itv-jelle-van-damme.htm?lng=fr#.UGMIPnI4SSo", u"""__GHOST_LINK__""", set(['external', 'in text'])),
                make_tagged_url("/7s7/fr/1509/Football-Belge/article/detail/1506791/2012/09/25/Le-Standard-est-passe-tout-pres-de-la-catastrophe.dhtml", u"""Le Standard est passé tout près de la catastrophe""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1745/Standard/article/detail/1506809/2012/09/25/Jelle-Van-Damme-menace-De-Ceuninck-Fais-attention-toi.dhtml", u'''Jelle Van Damme menace De Ceuninck: "Fais attention, toi!"''', set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1745/Standard/article/detail/1506881/2012/09/26/Ron-Jans-Oui-cette-qualification-me-soulage.dhtml", u'''Ron Jans: "Oui, cette qualification me soulage"''', set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1745/Standard/article/detail/1506951/2012/09/26/Deceuninck-Je-ne-me-suis-pas-senti-menace.dhtml", u'''Deceuninck: "Je ne me suis pas senti menacé"''', set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1509/Football-Belge/article/detail/1507218/2012/09/26/Le-parquet-propose-deux-rencontres-a-Batshuayi.dhtml", u"""Le parquet propose deux rencontres à Batshuayi""", set(['bottom box', 'internal'])),
                make_tagged_url("http://www.11dor.be", u"""Jouez avec: Le 11 d'Or et gagnez 25.000 euro!""", set(['bottom box', 'external', 'same owner'])),
                make_tagged_url("http://www.7sur7.be/newslettersports", u"""Inscrivez-vous à la newsletter sports de 7sur7 et recevez chaque jour les dernières infos sports""", set(['bottom box', 'internal'])),
                make_tagged_url("/7s7/fr/1509/Football-Belge/article/detail/1506791/2012/09/25/Le-Standard-est-passe-tout-pres-de-la-catastrophe.dhtml", u"""Le Standard est passé tout près de la catastrophe""", set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1745/Standard/article/detail/1506809/2012/09/25/Jelle-Van-Damme-menace-De-Ceuninck-Fais-attention-toi.dhtml", u'''Jelle Van Damme menace De Ceuninck: "Fais attention, toi!"''', set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1745/Standard/article/detail/1506881/2012/09/26/Ron-Jans-Oui-cette-qualification-me-soulage.dhtml", u'''Ron Jans: "Oui, cette qualification me soulage"''', set(['internal', 'sidebar box'])),
                make_tagged_url("/7s7/fr/1481/Home/932/Ligue-Jupiler/actualite/index.dhtml", u"""Ligue Jupiler""", set(['internal', 'sidebar box', 'keyword'])),
                make_tagged_url("/7s7/fr/1481/Home/493/Standard/actualite/index.dhtml", u"""Standard""", set(['internal', 'sidebar box', 'keyword'])),
            ]
            expected_links = tagged_urls
            assert_taggedURLs_equals(expected_links, extracted_links)

class Test7sur7ContentExtraction(object):
    def test_clean_intro_extraction(self):
        """ 7sur7 parser correctly extracts the intro"""
        with open(os.path.join(DATA_ROOT, "content_intro_articleHat.html")) as f:
            article, _ = septsursept.extract_article_data(f)
            expected_intro = u'Plus que n\'importe quel autre sport, le tennis est une discipline qui exige une ma\xeetrise de soi infaillible. Un match ne tient parfois qu\'\xe0 un ou deux points cruciaux, en particulier sur les surfaces plus rapides, et donc, il faut pouvoir garder son sang-froid \xe0 tout instant. Le contr\xf4le des \xe9motions fait l\'objet d\'un travail intense chez certains joueurs au temp\xe9rament plus explosif. Cela dit, un d\xe9rapage n\'est jamais \xe0 exclure, et l\'\xeatre humain n\'est pas \xe0 l\'abri d\'une r\xe9action impr\xe9visible. Ce week-end, David Nalbandian a \xe9t\xe9 disqualifi\xe9 (fort logiquement) pour avoir frapp\xe9 du pied dans un panneau publicitaire, qui a heurt\xe9 le tibia d\'un juge de ligne. La jambe en sang, l\'arbitre a d\xfb \xeatre soign\xe9. L\'occasion \xe9tait belle de faire une petite compilation des dix plus gros "p\xe9tages de plomb" de l\'histoire du tennis.'
            eq_(article.intro, expected_intro)

    def test_clean_text_extraction(self):
        """ 7sur7 parser correctly extracts the article text"""
        with open(os.path.join(DATA_ROOT, "same_owner.html")) as f:
            article, _ = septsursept.extract_article_data(f)
            expected_content = [u'Si la tension est clairement mont\xe9e entre Jelle Van Damme et Benjamin Deceuninck hier soir \xe0 Mouscron, l\'incident continue \xe0 faire couler beaucoup d\'encre. Le journaliste de la RTBF ne s\'est pas "senti menac\xe9". De son c\xf4t\xe9, Jelle Van Damme n\'avait pas encore donn\xe9 sa version des faits."Il a peut-\xeatre \xe9t\xe9 surpris""Ce n\'est pas un probl\xe8me pour moi d\'en reparler. Lui (NDLR: Benjamin Deceuninck) a peut-\xeatre \xe9t\xe9 surpris. C\'est mon avis. Quand on joue 120 minutes et qu\'on se bat, j\'estime que ce n\'\xe9tait pas le moment de poser une question comme \xe7a. OK, c\'est leur m\xe9tier. Alors, j\'ai aussi le droit de r\xe9agir comme \xe7a. J\'ai peut-\xeatre un peu trop agressif, trop direct. Mais cette question \xe9tait inutile \xe0 ce moment pr\xe9cis. Pour moi, \xe7a reste une question ridicule. Elle ne sert \xe0 rien hormis qu\'\xe0 cr\xe9er une atmosph\xe8re n\xe9gative. Je vais toujours prot\xe9ger mes co\xe9quipiers, le coach ou le pr\xe9sident", a soulign\xe9 Jelle Van Damme sur "Standard TV".BuzzNe supportant visiblement pas une question directe du journaliste de la RTBF \xe0 son entra\xeeneur, Jelle Van Damme s\'est ensuite montr\xe9 agressif verbalement. "Si tu commences avec des questions comme \xe7a... Fais attention \xe0 toi", a-t-il dit, en direct, tout en pointant du doigt Deceuninck."Je connais le temp\xe9rament de Jelle""Je tiens \xe0 pr\xe9ciser qu\'\xe0 aucun moment je ne me suis senti en danger physiquement. J\'ai \xe9t\xe9 surpris par l\'ampleur de la r\xe9action, je l\'avoue. Mais, je connais le temp\xe9rament de Jelle... Et il y avait beaucoup d\'adr\xe9naline durant cette rencontre. Pour moi, on peut trouver une question idiote ou non appropri\xe9e, mais \xe9vitons ce genre de d\xe9rapage.""Van Damme doit m\'appeler"Les choses vont donc en rester l\xe0. "Bien entendu ! Il n\'y a aucune raison de dramatiser. D\'ailleurs, Van Damme doit m\'appeler aujourd\'hui pour aplanir le diff\xe9rend", a d\xe9voil\xe9 le journaliste.Pour le Standard, "l\'incident est clos"Du c\xf4t\xe9 du Standard de Li\xe8ge, on estime "qu\'un journaliste doit avoir le droit de poser des questions directes tout en reconnaissant le droit \xe0 ses interlocuteurs de r\xe9agir. Van Damme s\'est simplement laiss\xe9 envahir par l\'\xe9motion. Pour nous, l\'incident est clos."', u'']
            eq_(article.content, expected_content)
