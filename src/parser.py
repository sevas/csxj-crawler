#!/usr/bin/env python


from BeautifulSoup import BeautifulSoup 

class ArticleData(object):
    def __init__(self, url, title, date, content, links, category):
        self.url = url
        self.title = title
        self.date = date
        self.content = content
        self.links = links
        self.category = category










def extract_category(story):
    pass




def sanitize_content():
    "removes image links, removes paragraphs, formatting"
    pass
    

def extract_content(story):
    header = story.find("div", {"id":"story_head"})
    body = story.find("div", {"id":"story_body"})

    print body
    

def extract_links(story):
    pass


def extract_title(story):
    pass

def extract_date(story):
    pass



if __name__ == '__main__':
    import sys
    data_directory = "../sample_data" 
    sys.path.append(data_directory)
    from dataset import dataset

    url = dataset['le soir']['URL']
    filename = dataset['le soir']['file']
    filepath = "%s/%s" % (data_directory, filename)
    
    with open(filepath) as f:
        html_content = f.read()
        soup = BeautifulSoup(html_content)
        
        story = soup.find("div", {'id':'story'})
        extract_content(story)
