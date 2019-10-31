import csv

path = "movie.csv"

movie=list();
count=0
path = "movie.csv"
with open(path,'w', newline='') as f:
    csv_write = csv.writer(f)
    csv_head = ["product/productId","review/userId","review/profileName","review/helpfulness","review/score","review/time","review/summary","review/text"]
    csv_write.writerow(csv_head)


with open(path,'a+', newline='') as f1:
    with open('movies.txt',errors='ignore') as f2:
        line=f2.readline()
        while line:
            if 'review/profileName' in line or 'review/text' in line:
                nextline=f2.readline()
                while nextline:
                    while not nextline.strip():
                        nextline=f2.readline()
                    if 'product/productId:' in nextline:
                        movie.append(line.split(':',1)[1].strip())
                        print(movie[:-2])
                        #csv_write = csv.writer(f1)
                        #csv_write.writerow(movie)
                        movie.clear()
                        movie.append(nextline.split(':')[1].strip())
                        break
                    if 'review/helpfulness:' in nextline:
                        movie.append(line)
                        movie.append(nextline.split(':',1)[1].strip())
                        break
                    line=line+ ' ' +nextline.strip()
                    nextline=f2.readline()
            else:
                movie.append(line.split(':',1)[1].strip())

            line=f2.readline()


