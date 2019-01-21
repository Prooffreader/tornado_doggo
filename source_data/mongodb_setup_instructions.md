# 1. Download file "Dogs of NYC _ WNYC.csv" from https://fusiontables.google.com/data?docid=1pKcxc8kzJbBVzLu_kgzoAMzqYhZyUhtScXjB0BQ#rows:id=1

# 2. In the download directory, run:
    $ mongo
    > use dogs
    > db.createCollection("nyc")
    > exit

# 3. In the source_data, run in the terminal:
    $ mongoimport -d dogs -c nyc --type csv --file "Dogs of NYC _ WNYC.csv" --headerline

# 4. Verify import with
    $ mongo
    > use dogs
    > db.nyc.findOne()

