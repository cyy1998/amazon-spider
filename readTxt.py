import redis

r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True)


with open('movies.txt',errors='ignore') as f:
    for line in f:
        if 'product/productId' in line:
            print(line)
            r.sadd('productID', line.split(':',1)[1].strip())

print(r.smembers('productID'))





