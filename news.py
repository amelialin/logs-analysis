#!/usr/bin/env python3

import psycopg2

DATABASE_NAME = "news"
OUTPUT_FILE = "output.txt"

def get_top_articles(cursor):
    """Returns list of tuples of (article title, views) for top 3 viewed articles, ranked by views descending."""
    cursor.execute('''
        SELECT title,
               COUNT(*) AS num
        FROM articles
        JOIN log ON concat('/article/', articles.slug) = log.path
        GROUP BY title
        ORDER BY num DESC
        LIMIT 3;
        '''
        )
    return cursor.fetchall()

def get_top_authors(cursor):
    """Returns list of tuples of (author, views of all authored articles) for all authors, ranked by views descending."""
    cursor.execute('''
        SELECT authors.name,
               COUNT(*) AS num
        FROM articles
        JOIN log ON concat('/article/', articles.slug) = log.path
        JOIN authors ON articles.author = authors.id
        GROUP BY authors.name
        ORDER BY num DESC;
        '''
        )
    return cursor.fetchall()

def get_top_error_days(cursor):
    """Returns list of tuples of (date, percent) for all days ON which more than 1% of requests led to errors, ordered by date."""
    cursor.execute('''
        SELECT *
        FROM
            (SELECT count_total.day,
                    ROUND((errors * 100.00 / total), 1) AS percent_error
             FROM
                (SELECT CAST(time AS DATE) AS day,
                        COUNT(*) AS total
                 FROM log GROUP BY day
                 ORDER BY day ASC) AS count_total
             JOIN
                (SELECT CAST(time AS DATE) AS day,
                        COUNT(*) AS errors
                 FROM log
                 WHERE status != '200 OK' GROUP BY day
                 ORDER BY day ASC) AS count_errors
             ON count_total.day = count_errors.day) AS percent_error_by_day
        WHERE percent_error > 2
        ORDER BY day ASC;
        '''
        )
    return cursor.fetchall()

OUTPUT_TEMPLATE = '''
1. TOP ARTICLES
What are the most popular three articles of all time? Which articles have been accessed the most?

{top_articles}

2. TOP AUTHORS
Who are the most popular article authors of all time?

{top_authors}

3. TOP ERROR DAYS
On which days did more than 1% of requests lead to errors?

{top_error_days}
'''.strip()

if __name__ == '__main__':
    print('Connecting to database...')
    with psycopg2.connect(database=DATABASE_NAME) as database_connection:
        cursor = database_connection.cursor()
        print('Connection successful...')

        print('Querying for top articles...')
        top_articles = '\n'.join('"{}" - {:,} views'.format(article_title.title(), views)
                                    for (article_title, views) in get_top_articles(cursor))
        print('Querying for top authors...')
        top_authors = '\n'.join('{} - {:,} views'.format(author, views)
                                for (author, views) in get_top_authors(cursor))
        print('Querying for top error days...')
        top_error_days = '\n'.join('{:%B %d}, {:%Y} - {}% errors'.format(day, day, error_percent)
                                for (day, error_percent) in get_top_error_days(cursor))
    print('Connection closed...')

    print('Writing to output.txt...')
    with open(OUTPUT_FILE, 'w') as fp:
        fp.write(OUTPUT_TEMPLATE.format(top_articles=top_articles,
                                        top_authors=top_authors,
                                        top_error_days=top_error_days))
    print('Writing complete. All done!')