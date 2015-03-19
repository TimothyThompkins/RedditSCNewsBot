# RedditSCNewsBot

## Description
This is a reddit bot that posts the content of news articles submitted to http://reddit.com/r/SouthCarolina as a comment on the post in an effort to make the content more accessible for those with slow internet connections and those that are reading on mobile. It is also makes an attempt to avoid pay walls and welcome webpages.

Please direct questions, comments, and concerns to http://reddit.com/u/a_soy_milkshake.
The open source code is found at https://github.com/TimothyThompkins/RedditSCNewsBot

This bot is deployed on heroku.


## Functionality
It functions by looking at the 10 most recent posts and checks to see if they either have an approved flair (News or Sports), or if the submitted url is a confirmed news source. If the post falls into either of those categories, an attempt is made to extract the main article text and post that as a comment. If the comment is less than 10 characters or more than 6000 it will not be posted. It currently checks every 300 seconds (5 minutes) if there are any new submissions. Additionally, It has safeguards to prevent itself from ever commenting on a post more than once.

Note that the api token and reddit user login credentials are stored in separate text files.


## Requirements

To install the requirements run:

```
pip install -r requirements.txt
```

## Execution

To execute run:

```
python reddit_client.py
```
