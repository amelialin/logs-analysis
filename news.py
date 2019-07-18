import psycopg2

DBNAME = "news"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()

# 1. What are the most popular three articles of all time? Which articles have been accessed the most?

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
print 'results: \n', results

# 2. Who are the most popular article authors of all time? That is, when you sum up all of the articles each author has written, which authors get the most page views?

# 3. On which days did more than 1% of requests lead to errors?

db.close()
