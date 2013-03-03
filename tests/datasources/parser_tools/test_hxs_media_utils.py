
from scrapy.selector import HtmlXPathSelector
from nose.tools import eq_, raises

from csxj.datasources.parser_tools import hxs_media_utils

class TestYoutubeURLExtraction(object):
    def test_youtube_object_with_a_tag(self):
        """hxs_media_utils.extract_url_from_youtube_object() can extract the source url if provided as a sub <a> tag"""
        raw_html = """
            <html>
            <body>
            <div id="youtube-media">
            <object type="application/x-shockwave-flash" height="200" width="300" data="http://www.youtube.com/v/4tkHmGycfz4&amp;amp;rel=0&amp;amp;enablejsapi=1&amp;amp;playerapiid=ytplayer&amp;amp;fs=1" id="media-youtube-default-external-object-1">
                <param name="movie" value="http://www.youtube.com/v/4tkHmGycfz4&amp;amp;rel=0&amp;amp;enablejsapi=1&amp;amp;playerapiid=ytplayer&amp;amp;fs=1">
                <param name="allowScriptAccess" value="sameDomain">
                <param name="quality" value="best">
                <param name="allowFullScreen" value="true">
                <param name="bgcolor" value="#FFFFFF">
                <param name="scale" value="noScale">
                <param name="salign" value="TL">
                <param name="FlashVars" value="playerMode=embedded">
                <param name="wmode" value="transparent">
                <!-- Fallback content -->
                  <a href="http://www.youtube.com/watch?v=4tkHmGycfz4"><img src="http://img.youtube.com/vi/4tkHmGycfz4/0.jpg" alt="See video" title="See video" height="200" width="300"></a>  </object>
            </div>
            </body>
            </html>
        """

        hxs = HtmlXPathSelector(text=raw_html)
        youtube_object = hxs.select("//div [@id='youtube-media']/object")

        expected_url = "http://www.youtube.com/watch?v=4tkHmGycfz4"
        url = hxs_media_utils.extract_url_from_youtube_object(youtube_object)
        eq_(expected_url, url)

    def test_youtube_object_without_a_tag(self):
        """hxs_media_utils.extract_url_from_youtube_object() can extract the source url from the 'data' attribute"""
        raw_html = """
            <html>
            <body>
            <div id="youtube-media">
            <object type="application/x-shockwave-flash" height="200" width="300" data="http://www.youtube.com/v/4tkHmGycfz4&amp;amp;rel=0&amp;amp;enablejsapi=1&amp;amp;playerapiid=ytplayer&amp;amp;fs=1" id="media-youtube-default-external-object-1">
                <param name="movie" value="http://www.youtube.com/v/4tkHmGycfz4&amp;amp;rel=0&amp;amp;enablejsapi=1&amp;amp;playerapiid=ytplayer&amp;amp;fs=1">
                <param name="allowScriptAccess" value="sameDomain">
                <param name="quality" value="best">
                <param name="allowFullScreen" value="true">
                <param name="bgcolor" value="#FFFFFF">
                <param name="scale" value="noScale">
                <param name="salign" value="TL">
                <param name="FlashVars" value="playerMode=embedded">
                <param name="wmode" value="transparent">
            </div>
            </body>
            </html>
        """

        hxs = HtmlXPathSelector(text=raw_html)
        youtube_object = hxs.select("//div [@id='youtube-media']/object")

        expected_url = "http://www.youtube.com/v/4tkHmGycfz4&amp;rel=0&amp;enablejsapi=1&amp;playerapiid=ytplayer&amp;fs=1"
        url = hxs_media_utils.extract_url_from_youtube_object(youtube_object)
        eq_(expected_url, url)


    @raises(ValueError)
    def test_youtube_object_data_is_not_url(self):
        """hxs_media_utils.extract_url_from_youtube_object() raises ValueError if the 'data' attr does not seem to be a url"""
        raw_html = """
            <html>
            <body>
            <div id="youtube-media">
            <object type="application/x-shockwave-flash" height="200" width="300" data="www.youtube.com/v/4tkHmGycfz4&amp;amp;rel=0&amp;amp;enablejsapi=1&amp;amp;playerapiid=ytplayer&amp;amp;fs=1" id="media-youtube-default-external-object-1">
                <param name="movie" value="http://www.youtube.com/v/4tkHmGycfz4&amp;amp;rel=0&amp;amp;enablejsapi=1&amp;amp;playerapiid=ytplayer&amp;amp;fs=1">
                <param name="allowScriptAccess" value="sameDomain">
                <param name="quality" value="best">
                <param name="allowFullScreen" value="true">
                <param name="bgcolor" value="#FFFFFF">
                <param name="scale" value="noScale">
                <param name="salign" value="TL">
                <param name="FlashVars" value="playerMode=embedded">
                <param name="wmode" value="transparent">
            </div>
            </body>
            </html>
        """

        hxs = HtmlXPathSelector(text=raw_html)
        youtube_object = hxs.select("//div [@id='youtube-media']/object")
        hxs_media_utils.extract_url_from_youtube_object(youtube_object)

    @raises(ValueError)
    def test_youtube_object_no_known_url(self):
        """hxs_media_utils.extract_url_from_youtube_object() raises ValueError if there is no known way to extract the URL"""
        raw_html = """
            <html>
            <body>
            <div id="youtube-media">
            <object type="application/x-shockwave-flash" height="200" width="300" >
                <param name="movie" value="http://www.youtube.com/v/4tkHmGycfz4&amp;amp;rel=0&amp;amp;enablejsapi=1&amp;amp;playerapiid=ytplayer&amp;amp;fs=1">
                <param name="allowScriptAccess" value="sameDomain">
                <param name="quality" value="best">
                <param name="allowFullScreen" value="true">
                <param name="bgcolor" value="#FFFFFF">
                <param name="scale" value="noScale">
                <param name="salign" value="TL">
                <param name="FlashVars" value="playerMode=embedded">
                <param name="wmode" value="transparent">
            </div>
            </body>
            </html>
        """

        hxs = HtmlXPathSelector(text=raw_html)
        youtube_object = hxs.select("//div [@id='youtube-media']/object")
        hxs_media_utils.extract_url_from_youtube_object(youtube_object)



class TestKewegoURLExtraction(object):
    def test_from_flash_object(self):
        """hxs_media_utils.extract_url_from_kplayer_object() can extract the source url from the object parameters"""
        raw_html = """
        <html>
        <body>
        <div id="kewego-media">
        <object width="300" height="200" type="application/x-shockwave-flash" id="054c411daa8s" data="http://sll.kewego.com/swf/p3/epix.swf">
          <param name="flashVars" value="language_code=fr&amp;playerKey=7b7e2d7a9682&amp;skinKey=a07930e183e6&amp;sig=054c411daa8s&amp;autostart=0&amp;advertise=true">
          <param name="movie" value="http://sll.kewego.com/swf/p3/epix.swf">
          <param name="allowFullScreen" value="true">
          <param name="allowscriptaccess" value="always">
          <param name="wmode" value="opaque">

          <video width="300" height="200" preload="none" poster="http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&amp;sig=054c411daa8s" controls="controls">&nbsp;</video>
          <script src="//sll.kewego.com/embed/assets/kplayer-standalone.js"></script>
          <script defer="defer">kitd.html5loader("flash_epix_054c411daa8s");</script>
        </object>
        </div>
        </body>
        </html>
        """
        hxs = HtmlXPathSelector(text=raw_html)
        kewego_object = hxs.select("//div [@id='kewego-media']/object")
        expected_url = "http://sll.kewego.com/swf/p3/epix.swf?language_code=fr&playerKey=7b7e2d7a9682&skinKey=a07930e183e6&sig=054c411daa8s&autostart=0&advertise=true"
        url = hxs_media_utils.extract_url_from_kplayer_object(kewego_object)
        eq_(expected_url, url)

    @raises(ValueError)
    def test_no_params(self):
        """hxs_media_utils.extract_url_from_kplayer_object() raises ValueError when the 'flashVars' child parameter is missing """
        raw_html = """
        <html>
        <body>
        <div id="kewego-media">
        <object width="300" height="200" type="application/x-shockwave-flash" id="054c411daa8s" data="http://sll.kewego.com/swf/p3/epix.swf">
          <param name="movie" value="http://sll.kewego.com/swf/p3/epix.swf">
          <param name="allowFullScreen" value="true">
          <param name="allowscriptaccess" value="always">
          <param name="wmode" value="opaque">

          <video width="300" height="200" preload="none" poster="http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&amp;sig=054c411daa8s" controls="controls">&nbsp;</video>
          <script src="//sll.kewego.com/embed/assets/kplayer-standalone.js"></script>
          <script defer="defer">kitd.html5loader("flash_epix_054c411daa8s");</script>
        </object>
        </div>
        </body>
        </html>
        """
        hxs = HtmlXPathSelector(text=raw_html)
        kewego_object = hxs.select("//div [@id='kewego-media']/object")
        hxs_media_utils.extract_url_from_kplayer_object(kewego_object)

    @raises(ValueError)
    def test_missing_data_attr(self):
        """hxs_media_utils.extract_url_from_kplayer_object() raises ValueError when the 'data' attribute is missing"""
        raw_html = """
        <html>
        <body>
        <div id="kewego-media">
        <object width="300" height="200" type="application/x-shockwave-flash" id="054c411daa8s" >
          <param name="flashVars" value="language_code=fr&amp;playerKey=7b7e2d7a9682&amp;skinKey=a07930e183e6&amp;sig=054c411daa8s&amp;autostart=0&amp;advertise=true">
          <param name="movie" value="http://sll.kewego.com/swf/p3/epix.swf">
          <param name="allowFullScreen" value="true">
          <param name="allowscriptaccess" value="always">
          <param name="wmode" value="opaque">

          <video width="300" height="200" preload="none" poster="http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&amp;sig=054c411daa8s" controls="controls">&nbsp;</video>
          <script src="//sll.kewego.com/embed/assets/kplayer-standalone.js"></script>
          <script defer="defer">kitd.html5loader("flash_epix_054c411daa8s");</script>
        </object>
        </div>
        </body>
        </html>
        """
        hxs = HtmlXPathSelector(text=raw_html)
        kewego_object = hxs.select("//div [@id='kewego-media']/object")
        hxs_media_utils.extract_url_from_kplayer_object(kewego_object)

    @raises(ValueError)
    def test_data_attr_not_url(self):
        """hxs_media_utils.extract_url_from_kplayer_object() raises ValueError when the 'data' attribute does not look like a URL"""
        raw_html = """
        <html>
        <body>
        <div id="kewego-media">
        <object width="300" height="200" type="application/x-shockwave-flash" id="054c411daa8s" data="HELLO">
          <param name="flashVars" value="language_code=fr&amp;playerKey=7b7e2d7a9682&amp;skinKey=a07930e183e6&amp;sig=054c411daa8s&amp;autostart=0&amp;advertise=true">
          <param name="movie" value="http://sll.kewego.com/swf/p3/epix.swf">
          <param name="allowFullScreen" value="true">
          <param name="allowscriptaccess" value="always">
          <param name="wmode" value="opaque">

          <video width="300" height="200" preload="none" poster="http://api.kewego.com/video/getHTML5Thumbnail/?playerKey=7b7e2d7a9682&amp;sig=054c411daa8s" controls="controls">&nbsp;</video>
          <script src="//sll.kewego.com/embed/assets/kplayer-standalone.js"></script>
          <script defer="defer">kitd.html5loader("flash_epix_054c411daa8s");</script>
        </object>
        </div>
        </body>
        </html>
        """
        hxs = HtmlXPathSelector(text=raw_html)
        kewego_object = hxs.select("//div [@id='kewego-media']/object")
        url = hxs_media_utils.extract_url_from_kplayer_object(kewego_object)
