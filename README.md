# tornado_doggo
A tiny test tornado webserver that serves a single endpoint answering queries about dogs in New York City

(As an aside, I've been working as a Python Developer in Data Science in a closed-source environment for 3.5 years, not that I've been completely inactive on GitHub during that time, but it's nice to be able to contribute even a small project that's properly engineered instead of the run-once data science "cowboy code" I've tended to quickly commit in the past.)

Please keep in mind that this is after two days of study of Tornado, and one previous project with asyncio. I have extensive experience with MongoDB, but this is the first time I've used the asynchronous client motor.

# The Project
Very simple, usage is:

    python3 doggo.py <port number>

make sure your port is open and you have permissions, etc. The `requirements.txt` file lists the packages you need; `requests` is only for the test program, `apitest.py`, which also needs the environment variable `READY_TEST_BASE_URL` set to the URL with port number.

The dataset is in MongoDB; its downloading and installation instructions are in the `/source_data` folder, as is the downloaded CSV itself (a bit more than 5 MB) so you can just use that if you want.

The `static` directory only contains a favicon, which is kind of ridiculous because this is a REST API not designed to be accessed through a browser, but what the heck, it's a cute doggo! Also `robots.txt` because I don't like to pollute webcrawlers with my ephemera.

# Querying
Here's an example of the first row of the table, with the field names

| dog_name | gender | breed        | birth  | dominant_color | secondary_color | third_color | spayed_or_neutered | guard_or_trained | borough   | zip_code |
| -------- | ------ | ------------ | ------ | -------------- | --------------- | ----------- | ------------------ | ---------------- | --------- | -------- |
| Buddy    | M      | Afghan Hound | Jan-00 | BRINDLE        | BLACK           | n/a         | Yes                | No               | Manhattan | 10003    |

Field names have to be lower-case, but values are case-insensitive. The total number of dogs is 81542

So if you want to know how many male dogs are named buddy, for example, you could `curl` a `GET` request to `/count` with `params={"dog_name": "bUdDy", "gender": "m"}`
Or if you really want to see the cute favicon, goto http://ipaddress:port/count?dog_name=bUdDy&gender=m
