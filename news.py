#!/usr/bin/env python3

import psycopg2
from pprint import pprint

DBNAME = "news"
OUTPUT_FILE = "output.txt"

database_connection = psycopg2.connect(database=DBNAME)
cursor = database_connection.cursor()

# 1. What are the most popular three articles of all time? Which articles have been accessed the most?

def get_top_articles(cursor):
    cursor.execute('''
        select title, count(*) as num 
        from articles join log
            on concat('/article/', articles.slug) = log.path
        group by title
        order by num desc
        limit 3;
        '''
        )
    return cursor.fetchall()

# 2. Who are the most popular article authors of all time? That is, when you sum up all of the articles each author has written, which authors get the most page views?

def get_top_authors(cursor):
    cursor.execute('''
        select authors.name, count(*) as num 
        from articles join log 
            on concat('/article/', articles.slug) = log.path
        join authors
            on articles.author = authors.id
        group by authors.name
        order by num desc;
        '''
        )
    return cursor.fetchall()

# 3. On which days did more than 1% of requests lead to errors?

def get_top_error_days(cursor):
    cursor.execute('''
        select * from
            (select count_total.day, round((errors * 100.00 / total), 1) as percent_error
            from 
                (select CAST(time AS date) as day, count(*) as total
                    from log
                    group by day
                    order by day asc
                ) as count_total 
                join (select CAST(time AS date) as day, count(*) as errors
                    from log
                    where status != '200 OK'
                    group by day
                    order by day asc
                ) as count_errors
                on count_total.day = count_errors.day
            ) as a
            where percent_error > 2
            order by day asc
        ;
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

with open(OUTPUT_FILE, 'w') as fp:
    top_articles = '\n'.join('"{}" - {:,} views'.format(article_title.title(), views) 
                             for (article_title, views) in get_top_articles(cursor))
    top_authors = '\n'.join('{} - {:,} views'.format(author, views)
                            for (author, views) in get_top_authors(cursor))
    top_error_days = '\n'.join('{:%B %d}, {:%Y} - {}% errors'.format(day, day, error_percent)
                               for (day, error_percent) in get_top_error_days(cursor))
    
    fp.write(OUTPUT_TEMPLATE.format(top_articles=top_articles,
                                    top_authors=top_authors,
                                    top_error_days=top_error_days))

database_connection.close() 

# if __name__ == '__main__':
#     database_connection = psycopg2.connect(database=DBNAME)
#     c = db.cursor()
#     db.close()