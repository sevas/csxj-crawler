import csxj.db as db


def log_message(s, tab_count=0):
    line_template = u"{0}{1}"
    line = line_template.format("\t"*tab_count, s)
    print(line)


if __name__ == "__main__":
    providers = db.get_all_provider_names("out/")
    lesoir = db.Provider("out/", "lesoir")


    for date in lesoir.get_all_days():
        log_message(date)
        batches = lesoir.get_articles_per_batch(date)

        for batch_hour, articles in batches:
            log_message(batch_hour, 1)
            for a in articles:
                log_message(a.title, 2)
