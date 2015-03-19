#SCNewsHelper.py
#a_soy_milkshake
#March 2015

# This is the main function that is the "reddit bot". This code connects to reddit, pulls content, posts comments, etc...
# This reddit bot has username /u/SCNewsHelper

# Possible Imporvements:
# 1. More robust exception and error handling
# 2. Add timer for RateLimitExceeded Error and add post on which that error was called to a queue to be posted later. Best accomplished with multi-threading.

import praw
import time
import sys
import threading
from reddit_post import redditPost
from reddit_credentials import user_name
from reddit_credentials import password

heroku_deployment = False #This determines if our app is being run locally or on heroku. If it's on heroku we'll want to act differently than local execution.

execution_interval = 300 #This is the time in seconds between execution. If this is too low we will double comment because as reddit is adding our comment, we're checking again to see if it's there
comment_rate_limit = 20 #This is the time in seconds the bot waits before trying to post annother comment.
post_analyze_limit = 10 #This is the number of posts we want to look at for each call

analyzed_posts = [] #This array holds the post ids of posts that we tried to add comments to but failed (either b/c of an exception or we have already commented). We keep this to stop from calling the API too many times if we've already failed, or to stop from the coninual retrial to add a comment. The only exceiption to this should be if we are rate limited.
rate_limit_error = 'RateLimitExceeded'
user_agent = "South Carolina News Content Commenter:v1.0 (by /u/SCNewsHelper)" #This is our user_agent we use to access reddit

#Logs user into reddit. This is required if you're going to be commenting.
def __login(reddit_object,_user = user_name, _pass = password):

    try:
        print "Logging in to reddit as {0} : {1} \n".format(_user, time.asctime( time.localtime(time.time()) ))
        reddit_object.login(username=_user, password=_pass)

    except:
        message = __exception_message()
        login_wait_period = 20
        #print "Login Failed. Retrying in " + str(login_wait_period) + " seconds : " + time.asctime( time.localtime(time.time()) ) + "\n"
        print "Login Failed. Threw an %s error. Retrying in %s seconds : %s \n" % \
        (message, str(login_wait_period), time.asctime( time.localtime(time.time()) ))
        time.sleep(login_wait_period)
        __login(reddit_object,_user = user_name, _pass = password)

#Prints out the execption error and returns the class from which it came.
def __exception_message():
    exc_type, exc_value = sys.exc_info()[:2]
    print 'Handling %s exception with message "%s" in %s' % \
    (exc_type.__name__, exc_value, threading.current_thread().name)
    return exc_type.__name__

#This lets us add posts that we have already analyzed to an array so that we don't try to add them again if we failed.
def __add_analyzed_post_id(post_id):
    if post_id not in analyzed_posts:
        analyzed_posts.append(post_id)

def add_new_comment(reddit_object, subreddit, post_analyze_limit):
    reddit_post_submissions = []

    print "Pulling last %s newest posts from /r/%s : %s \n" % \
    (str(post_analyze_limit), str(subreddit), time.asctime( time.localtime(time.time()) ))
    submission_generator = subreddit.get_new(limit = post_analyze_limit) #This gets the first "post_analyze_limit" posts and creates a new object for each one

    for i, submission in enumerate(submission_generator):
        flair_text = str(submission.link_flair_text)
        post_url = str(submission.url)
        post_id = str(submission.id)
        submission = reddit_object.get_submission(submission_id = post_id)

        #This checks to see if any of the posts that have been declared "analyzed" are in our most recent pull
        if post_id not in analyzed_posts:
            reddit_post_submissions.append(redditPost(flair_text, post_url, post_id, submission)) #This creates an array with a reddit object equal to post_analyze_limit

    #We want to reverse the array because if we do get rate limited and have to wait to comment again, if we start commenting on the last post (oldest of the newest), if someone adds a new post during that time, we won't have missed the last one.
    reddit_post_submissions = list(reversed(reddit_post_submissions))

    if (len(reddit_post_submissions) > 0):

        for i, current_post in enumerate(reddit_post_submissions):
            article_content = current_post.check_comment_status()

            if article_content is not None:
                print "Attempting to add comment to post with post id: %s : %s" % \
                (str(current_post.get_post_ID()), time.asctime( time.localtime(time.time()) ))

                try:
                    #print article_content #This is for testing to look at the article content
                    current_post.get_submission().add_comment(article_content)
                    print "Added comment to post with post id: %s : %s \n" % \
                    (str(current_post.get_post_ID()), time.asctime( time.localtime(time.time()) ))

                    #No need to wait for next post if we're already at the last post.
                    if i is not (post_analyze_limit-1):
                        print "Waiting %s seconds before attempting to comment again : %s \n" % \
                        (str(comment_rate_limit), time.asctime( time.localtime(time.time()) ))
                        time.sleep(comment_rate_limit) #This is to prevent rate limiting. It may not even be necessary.

                except:
                    message = __exception_message()

                    print "Comment addition to post with post id: %s failed : %s \n" % \
                    (str(current_post.get_post_ID()), time.asctime( time.localtime(time.time()) ))

                    #If it's an RateLimitExceeded error it means we may have reached our rate limit, so we need to wait until we can comment again. In that case don't add the post to the analyzed post

                    if message is not rate_limit_error:
                        __add_analyzed_post_id(str(current_post.get_post_ID())) #Add post_id to analyzed list so we don't look at it again

                    #No need to wait for next post if we're already at the last post.
                    if i is not (post_analyze_limit-1):
                        print "Waiting %s seconds before attempting to comment again : %s \n" % \
                        (str(comment_rate_limit), time.asctime( time.localtime(time.time()) ))
                        time.sleep(comment_rate_limit) #This is to prevent rate limiting. It may not even be necessary.

            else:
                __add_analyzed_post_id(str(current_post.get_post_ID())) #Add post_id to analyzed list so we don't look at it again
                print "No comment was added to post with post id: %s : %s \n" % \
                (str(current_post.get_post_ID()), time.asctime( time.localtime(time.time()) ))

    else:
        print "No new posts have been added in the last %s seconds : %s \n" % \
        (str(execution_interval), time.asctime( time.localtime(time.time()) ))


def main():

    r = praw.Reddit(user_agent) #This creates a new reddit object
    subreddit = r.get_subreddit('southcarolina')
    #subreddit = r.get_subreddit('SCNewsHelper') #Use this subreddit to test.
    __login(r)

    if heroku_deployment is False:

        while True:
            #Add a try statement here eventually to handle exceptions TMT
            add_new_comment(r, subreddit, post_analyze_limit)
            print "Execution End. Waiting %s seconds before next execution : %s \n" % \
            (str(execution_interval), time.asctime( time.localtime(time.time()) ))
            print "_________________________________________________________________" + "\n"
            time.sleep(execution_interval)

    else:
        add_new_comment(r, subreddit, post_analyze_limit)


if __name__ == '__main__':
    main()
