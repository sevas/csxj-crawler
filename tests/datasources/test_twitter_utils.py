from csxj.datasources.common import twitter_utils
from nose.tools import eq_, raises

SAMPLE_TWIMG_PROFILE = """
    new TWTR.Widget({
    version: 2,
    type: "profile",
    rpp: 15,
    interval: 30000,
    title: "",
    subject: "",
    width: "auto",
    height: 350,
    theme: {
        shell: {
            background: "#559abc",
            color: "#ffffff"
        },
        tweets: {
            background: "#ffffff",
            color: "#444444",
            links: "#1985b5"
        }
    },
    features: {
        scrollbar: false,
        loop: true,
        live: true,
        behavior: "all"
    }
}).render().setUser('@oscarmayer').start();
"""

SAMPLE_TWIMG_SEARCH = """
    new TWTR.Widget({
      version: 2,
      type: 'search',
      search: '#RemplaceLetitreDunFilmParBelfius',
      interval: 30000,
      title: '#RemplaceLetitreDunFilmParBelfius',
      subject: 'Belfius',
      width: 400,
      height: 250,
      theme: {
        shell: {
          background: '#8f158f',
          color: '#ffffff'
        },
        tweets: {
          background: '#ffffff',
          color: '#444444',
          links: '#8f158f'
        }
      },
      features: {
        scrollbar: true,
        loop: false,
        live: true,
        behavior: 'default'
      }
    }).render().start();
"""


class TestTwitterUtils(object):
    def test_embedded_search_widget(self):
        """
            Test the twitter widget detector on an embedded search
        """
        script_content = SAMPLE_TWIMG_SEARCH
        expected_tags = set(['twitter widget', 'twitter search'])
        title, url, tags = twitter_utils.get_widget_type(script_content)
        eq_(tags, expected_tags)

    def test_embedded_profile_widget(self):
        """
            Test the twitter widget detector on an embedded profile
        """
        script_content_user = SAMPLE_TWIMG_PROFILE
        expected_tags = set(['twitter widget', 'twitter profile'])
        title, url, tags = twitter_utils.get_widget_type(script_content_user)

        eq_(tags, expected_tags)

    @raises(ValueError)
    def test_unknown_widget_type(self):
        """
            Test that unknown widget type makes the twitter widget detection raise a ValueError
        """
        script_content = script_content = """
            new TWTR.Widget({
              version: 2,
              type: 'something_new',
              interval: 30000,
              subject: 'Belfius',
              width: 400,
              height: 250,
              theme: {
                shell: {
                  background: '#8f158f',
                  color: '#ffffff'
                },
                tweets: {
                  background: '#ffffff',
                  color: '#444444',
                  links: '#8f158f'
                }
              }
            }).render().start();
        """
        title, url, tags = twitter_utils.get_widget_type(script_content)

    @raises(ValueError)
    def test_missing_type(self):
        """
            Test that a missing 'type' parameter in the widget makes the twitter widget detection raise a ValueError
        """
        script_content = script_content = """
            new TWTR.Widget({
              version: 2,
              interval: 30000,
              width: 400,
              height: 250,
              theme: {
                shell: {
                  background: '#8f158f',
                  color: '#ffffff'
                },
                tweets: {
                  background: '#ffffff',
                  color: '#444444',
                  links: '#8f158f'
                }
              },
              features: {
                scrollbar: true,
                loop: false,
                live: true,
                behavior: 'default'
              }
            }).render().start();
        """
        title, url, tags = twitter_utils.get_widget_type(script_content)

    @raises(ValueError)
    def test_unknown_script(self):
        """
            Test that random javascript makes the twitter widget detection raise a ValueError
        """
        script_content = """ var pokey="-YES-";  // fancy javascript, hey """
        title, url, tags = twitter_utils.get_widget_type(script_content)
