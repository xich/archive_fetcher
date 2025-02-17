# Install

To start, run the following:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then you can:

```
python fetch.py "collection name"
```

(e.g. python fetch.py "pub_chicago-daily-tribune")

By default it waits 3 seconds between urls, but may not need that, you can set with --delay flag.

When you're done, you can:

```
deactivate
```

to disable the python venv you created.
