import csxj.db as db


def log_message(s, tab_count=0):
    line_template = u"{0}{1}"
    line = line_template.format("\t"*tab_count, s)
    print(line)


if __name__ == "__main__":
    db_root = "/Users/sevas/Documents/juliette/json_db_0_5_reprocess"
    providers = db.get_all_provider_names(db_root)
    lesoir = db.Provider(db_root, "lesoir")

    total = 0
    for date in lesoir.get_all_days():
        log_message(date)

        for batch_time in lesoir.get_all_batch_hours(date):
            reprocessed_articles = lesoir.get_reprocessed_batch_content(date, batch_time)
            if reprocessed_articles:
                for ((reprocessed_date, reprocessed_time), articles) in reprocessed_articles:
                    print "\t on {0} at {1}: {2} articles reprocessed".format(reprocessed_date, reprocessed_time, len(articles))
                    total += len(articles)
    print total