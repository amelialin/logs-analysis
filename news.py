import psycopg2

DBNAME = "news"

db = psycopg2.connect(database=DBNAME)
c = db.cursor()
c.execute('''
    select * 
    from authors
    limit 1;
    '''
    )
results = c.fetchall()
print 'results: \n', results
db.close()

# 1. What are the most popular three articles of all time? Which articles have been accessed the most?

# 2. Who are the most popular article authors of all time? That is, when you sum up all of the articles each author has written, which authors get the most page views?

# 3. On which days did more than 1% of requests lead to errors?

