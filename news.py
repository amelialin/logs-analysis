#!/usr/bin/env python2

import psycopg2
from pprint import pprint

DBNAME = "news"
OUTPUT_FILE = "output.txt"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()

# Sanity checks of table sizes

# c.execute('''
#     select count(*) as num 
#     from articles;
#     '''
#     )
# results = c.fetchall()
# print 'articles:', results[0][0]

# c.execute('''
#     select count(*) as num 
#     from authors;
#     '''
#     )
# results = c.fetchall()
# print 'authors:', results[0][0]

# c.execute('''
#     select count(*) as num 
#     from log;
#     '''
#     )
# results = c.fetchall()
# print 'log:', results[0][0]

# 1. What are the most popular three articles of all time? Which articles have been accessed the most?

print 'Most popular articles:'
c.execute('''
    select title, count(*) as num 
    from articles join log
        on concat('/article/', articles.slug) = log.path
    group by title
    order by num desc
    limit 3;
    '''
    )
top_articles = c.fetchall()
pprint(top_articles)

# print 'Out of total count:'
# c.execute('''
#     select count(*) as num 
#     from articles join log
#         on concat('/article/', articles.slug) = log.path;
#     '''
#     )
# results = c.fetchall()[0][0]
# pprint(results)

# 2. Who are the most popular article authors of all time? That is, when you sum up all of the articles each author has written, which authors get the most page views?

print 'Most popular authors:'
c.execute('''
    select authors.name, count(*) as num 
    from articles join log 
        on concat('/article/', articles.slug) = log.path
    join authors
        on articles.author = authors.id
    group by authors.name
    order by num desc;
    '''
    )
top_authors = c.fetchall()
pprint(top_authors)

# print 'Out of total count:'
# c.execute('''
#     select count(*) as num 
#     from articles join log 
#         on concat('/article/', articles.slug) = log.path
#     join authors
#         on articles.author = authors.id;
#     '''
#     )
# results = c.fetchall()[0][0]
# pprint(results)

# 3. On which days did more than 1% of requests lead to errors?

print 'High error days:'
c.execute('''
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
top_error_days = c.fetchall()
pprint(top_error_days)

with open(OUTPUT_FILE, 'w') as fp:
    fp.write("1. TOP ARTICLES\nWhat are the most popular three articles of all time? Which articles have been accessed the most?\n\n")
    fp.write('\n'.join('"{}"'.format(x[0]).title() + ' - ' + '{:,} views'.format(x[1]) for x in top_articles) + '\n\n')
    fp.write("2. TOP AUTHORS\nWho are the most popular article authors of all time?\n\n")
    fp.write('\n'.join('{} - {:,} views'.format(x[0],x[1]) for x in top_authors) + '\n\n')
    fp.write("3. TOP ERROR DAYS\nOn which days did more than 1% of requests lead to errors?\n\n")
    fp.write('\n'.join('{:%B %d}, {:%Y} - {}% errors'.format(x[0],x[0],x[1]) for x in top_error_days))

db.close() 

# if __name__ == '__main__':
#     db = psycopg2.connect(database=DBNAME)
#     c = db.cursor()
#     db.close()