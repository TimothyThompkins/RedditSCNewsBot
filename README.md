# RedditSCNewsBot
This is a reddit bot that posts the content of news sources submitted to reddit.com/r/SouthCarolina as a plaintext comment to help redditors with slow internet connections, the lazy, and to attempt to avoid paywalls. If you can however, please remember to follow the article link to support the news source with ad revenue.

It functions by looking at the 10 most recent posts and checks to see if they either have an approved flair (News or Sports), or if the submitted url is a confirmed news source. If the post falls into either of those categories, an attempt is made to extract the main article text and post that as a comment. If the comment is less than 10 characters or more than 6000 it will not be posted. It currently checks every 300 seconds (5 minutes) if there are any new submissions.

Note that the api tokens and reddit user login credentials are stored in separate files.
Dependencies include:
Praw
BeautifulSoup

This code is completely open source and free to be modified by anyone. Please direct questions, comments, and concerns to reddit.com/u/a_soy_milkshake.
