import psycopg2
from pprint import pprint

DBNAME = "news"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()

# Sanity checks of table sizes

c.execute('''
    select count(*) as num 
    from articles;
    '''
    )
results = c.fetchall()
print 'articles:', results[0][0]
c.execute('''
    select count(*) as num 
    from authors;
    '''
    )
results = c.fetchall()
print 'authors:', results[0][0]
c.execute('''
    select count(*) as num 
    from log;
    '''
    )
results = c.fetchall()
print 'log:', results[0][0]

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
results = c.fetchall()
pprint(results)

print 'Out of total count:'
c.execute('''
    select count(*) as num 
    from articles join log
        on concat('/article/', articles.slug) = log.path;
    '''
    )
results = c.fetchall()[0][0]
pprint(results)

# 2. Who are the most popular article authors of all time? That is, when you sum up all of the articles each author has written, which authors get the most page views?

print 'Most popular authors:'
c.execute('''
    select authors.name, count(*) as num 
    from articles join log 
        on concat('/article/', articles.slug) = log.path
    join authors
        on articles.author = authors.id
    group by authors.name
    order by num desc
    limit 3;
    '''
    )
results = c.fetchall()
pprint(results)

print 'Out of total count:'
c.execute('''
    select count(*) as num 
    from articles join log 
        on concat('/article/', articles.slug) = log.path
    join authors
        on articles.author = authors.id;
    '''
    )
results = c.fetchall()[0][0]
pprint(results)

# 3. On which days did more than 1% of requests lead to errors?

db.close()
