import os.path
import json



def load_last_toc_from_file(filename):
    last_stories_fetched = list()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            last_stories_fetched = [tuple(i) for i in  json.load(f)]
    return last_stories_fetched



def save_toc_to_file(toc, filename):
    with open(filename, 'w') as f:
        json.dump(toc, f)



def filter_only_new_stories(frontpage_stories, filename):
    last_stories_fetched = load_last_toc_from_file(filename)
    new_stories = set(frontpage_stories) - set(last_stories_fetched)
    save_toc_to_file(frontpage_stories, filename)
    return list(new_stories)
