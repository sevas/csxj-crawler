import os.path
import json



def filter_only_new_stories(frontpage_stories, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            last_stories_fetched = [tuple(i) for i in  json.load(f)]
            new_stories = set(frontpage_stories) - set(last_stories_fetched)
    else:
        new_stories = frontpage_stories

    # save the current current list
    with open(filename, 'w') as f:
        json.dump(frontpage_stories, f)

    return new_stories
