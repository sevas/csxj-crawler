"""
Note: functions listed here depends on scrapy's HtmlXpathSelector (hxs) interfaces
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-



def extract_url_from_youtube_object(hxs_youtube_object):
    """ Extracts the source url from an embedded youtube object (parsed By scrapy HtmlXpathSelector)"""
    if hxs_youtube_object.select("./a/@href"):
        return hxs_youtube_object.select('./a/@href').extract()[0]
    elif hxs_youtube_object.select('./@data'):
        data = hxs_youtube_object.select('./@data').extract()[0]
        if data.startswith('http'):
            return data
        else:
            raise ValueError("The data attribute of that youtube object does not look like a url. Update the parser.")
    else:
        raise ValueError("Could not find a source url for this youtube object" )


def extract_url_from_kplayer_object(hxs_kplayer_object):
    """ Extracts the source url from an embedded kplayer object (parsed By scrapy HtmlXpathSelector)"""
    if hxs_kplayer_object.select('./@data'):
        data = hxs_kplayer_object.select('./@data').extract()[0]
        if data.startswith('http'):
            params = hxs_kplayer_object.select("./param [@name='flashVars']/@value").extract()
            if params:
                url = "{0}?{1}".format(data, params[0])
                return url
            else:
                raise ValueError("Params could not be extracted from that kplayer object.")
        else:
            raise ValueError("The data attribute of that kplayer object does not look like a url. Update the parser.")
    else:
        raise ValueError("This kplayer object has no 'data' attribute.")