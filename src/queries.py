from __future__ import division

import os, os.path
import json
import itertools
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.gridspec import GridSpec
from parsers.article import ArticleData




def get_subdirs(parent_path):
    return [d for d in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, d))]



def get_articles(json_filepath):
    with open(json_filepath, 'r') as f:
        json_content = json.load(f)
        articles_string = json_content['articles']
        return [ArticleData.from_json(article_s) for article_s in articles_string]

    

def get_flat_article_list(provider_path):
    all_days = get_subdirs(provider_path)
    all_articles = []


    for day in all_days:
        day_path = os.path.join(provider_path, day)
        all_batches = get_subdirs(day_path)

        for batch in all_batches:
            batch_path = os.path.join(day_path, batch)
            all_articles.extend(get_articles(os.path.join(batch_path, 'articles.json')))

    return all_articles


def categorize_articles(articles):
    def keyfunc(article):
        return article.category

    groups = []
    uniquekeys = []
    data = sorted(articles, key=keyfunc)
    for k, g in itertools.groupby(data, keyfunc):
        groups.append(list(g))      # Store group iterator as a list
        uniquekeys.append(k)

    return zip(uniquekeys, groups)



def count_links(articles):
    ext_links = sum([len(art.external_links) for art in articles])
    int_links = sum([len(art.internal_links) for art in articles])

    return ext_links, int_links



CategoryCounters = namedtuple('CategoryCounters', 'name total_links total_articles  link_article_ratio')


def make_barchart_in_subplot(ax, xs, title, labels):
    ind = np.arange(len(xs))
    ax.barh(ind, xs, color='#00afaf')
    ax.set_yticklabels(ind+0.35, labels, fontsize='small', fontname='sans')
    ax.set_title(title)


def make_barchart(xs, title, labels):
    ind = np.arange(len(xs))
    plt.barh(ind, xs, color='#00afaf')
    plt.yticks(ind+0.35, labels, fontsize='small', fontname='sans')
    plt.title(title)


def sort_categories_by_links_article_ratio(categorized_articles):
    link_counters = list()

    max_total_articles = len(max(categorized_articles, key=lambda a: len(a[1]))[1])

    for (group, articles) in categorized_articles:
        total_articles = len(articles)

        total_links = sum(count_links(articles))
        if total_links and max_total_articles:
            ratio =  (total_articles / total_links) / max_total_articles
            link_counters.append(CategoryCounters(name=group,
                                                  total_links=total_links,
                                                  total_articles=total_articles,
                                                  link_article_ratio=ratio))

    def keyfunc(counter):
        return counter.link_article_ratio
    link_counters.sort(key=keyfunc)

    return link_counters


def plot_categories_by_links_article_ratio_in_subplot(ax, categorized_articles, source_name):
    link_counters = sort_categories_by_links_article_ratio(categorized_articles)

    x = np.array([c.link_article_ratio for c in link_counters])

    def make_label(counter):
        return u'{0} (n_a={1}  n_l={2})'.format(u'/'.join(counter.name),
                                               counter.total_articles,
                                               counter.total_links)


    labels = [make_label(c) for c in link_counters]
    make_barchart_in_subplot(ax, x, source_name, labels)


def plot_categories_by_links_article_ratio(categorized_articles):
    link_counters = sort_categories_by_links_article_ratio(categorized_articles)

    for counter in link_counters:
        print counter

    x = np.array([c.link_article_ratio for c in link_counters])

    def make_label(counter):
        return u'{0} (n_a={1}  n_l={2})'.format(u'/'.join(counter.name),
                                               counter.total_articles,
                                               counter.total_links)


    labels = [make_label(c) for c in link_counters]
    make_barchart(x, 'Categories by article/links ratio', labels)
    plt.show()



def plot_categories_by_number_of_articles(categorized_articles):
    article_counters = list()
    for (group, articles) in categorized_articles:
        article_counters.append((group, len(articles)))

    def keyfunc(counter):
        return counter[1]
    article_counters.sort(key=keyfunc)

    x = np.array([counter[1] for counter in article_counters])

    def make_label(article_counter):
        return u'{0}'.format(u'/'.join(article_counter[0]))

    labels = [make_label(c) for c in article_counters]
    make_barchart(x, '# Articles per category', labels)
    plt.show()



def plot_categories_by_number_of_links(categorized_articles):

    LinkCounter = namedtuple('LinkCounter', 'name total_ext_links total_int_links total_links')

    link_counters = list()
    for (group, articles) in categorized_articles:
        n_ext_links, n_int_links = count_links(articles)
        link_counters.append(LinkCounter(name=group,
                                         total_ext_links=n_ext_links,
                                         total_int_links=n_int_links,
                                         total_links=n_ext_links+n_int_links))


    def keyfunc(counter):
        return counter.total_links
    link_counters.sort(key=keyfunc)

    print link_counters

    x1 = np.array([counter.total_ext_links for counter in link_counters])
    x2 = np.array([counter.total_int_links for counter in link_counters])

    def make_label(link_counter):
        return u'{0}'.format(u'/'.join(link_counter.name))
    labels = [make_label(c) for c in link_counters]

    ind = np.arange(len(x1))
    p1 = plt.barh(ind, x1, color='#af8700')
    p2 = plt.barh(ind, x2, left=x1, color='#00afaf')
    plt.yticks(ind+0.35, labels, fontsize='small', fontname='sans')
    plt.title('Number of links per category')
    plt.legend( (p1[0], p2[0]), ('External links', 'Internal links'), 'lower right' )
    plt.show()
    

if __name__=='__main__':
    lesoir_articles = get_flat_article_list('../static_data/lesoir')
    dhnet_articles =  get_flat_article_list('../static_data/dhnet')
    lalibre_articles =  get_flat_article_list('../static_data/lalibre')


    all_articles = {
        'lesoir':lesoir_articles,
        'dhnet':dhnet_articles,
        'lalibre':lalibre_articles
    }

    for (name, articles) in all_articles.items():
        print '{0}: {1} articles'.format(name, len(articles))



#    master_plot = plt.figure()
#    ax1 = master_plot.add_subplot(221)
#    ax2 = master_plot.add_subplot(222)
#    ax3 = master_plot.add_subplot(223)
#
#    for (source_name, articles), ax in zip(all_articles.items(), (ax1, ax2, ax3)):
#        categorized_articles = categorize_articles(articles)
#        for (group, articles) in categorized_articles:
#            print group, len(articles), count_links(articles)
#        plot_categories_by_links_article_ratio(ax, categorized_articles, source_name)
#
#    plt.show()

    categorized_articles = categorize_articles(lalibre_articles)

    for (cat_name, articles) in categorized_articles:
        print u'{0} : \t {1} articles'.format(u'/'.join(cat_name), len(articles))

    #plot_categories_by_links_article_ratio(categorized_articles)
    plot_categories_by_number_of_articles(categorized_articles)

    #plot_categories_by_number_of_links(categorized_articles)




