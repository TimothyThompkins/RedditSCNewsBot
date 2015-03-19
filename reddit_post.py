#reddit_post.py
#a_soy_milkshake
#March 2015

#This function checks our posts and determines if we should comment

import time
from urlparse import urlparse
from diffbot_client import diffbotClient

relevant_flair= ['news' , 'sports']

news_sources = ['thestate', 'yahoo', 'myrtlebeachonline', 'nbc', 'wspa', 'cbs', 'greenvilleonline', 'theguardian', 'enquirehearld', 'huffpost','wcnc', 'cnn', 'islandpacket', 'postandcourier', 'greenvilleonline', 'goupstate', 'hearldonline', 'free-times', 'aikenstandard', 'charlestoncitypaper', 'myrtlebeachonline', 'charlotteobserver', 'nbcnews', 'cbsnews', 'cnn', 'wbtw', 'washingtontimes', 'foxnews', 'npr', 'wyff4', 'carolina live', 'usatoday', 'wjcl', 'live5news', 'foxcarolina', 'wistv', 'rawstory', 'thenonprofittimes', 'nytimes', 'nydailynews', 'abcnews4', 'washingtonpost', 'wltx', 'c-span', 'msnbc', 'wmbfnews', 'charlotteobserver', 'weeklystandard', 'politico', 'wncn', 'fitsnews', 'dailykos', 'nbc4i', 'forbes', 'reuters', 'cbs46', 'wjbf', 'moultrienews', 'wsoctv', 'indexjournal', 'espn', 'deadspin']

bad_news_sources = []
#Our comment must be between these ranges in order to post
character_post_min = 10
character_post_max = 6000

class redditPost:

    def __init__(self, post_flair, post_url, post_id, submission):
        self.post_flair = post_flair
        self.post_url = post_url
        self.post_id = post_id
        self.submission = submission

    #Test to display data about object created
    def displayRedditPostData(self):
        print self.post_flair
        print self.post_url
        url_info = urlparse(self.post_url)
        print url_info.netloc
        print self.post_id

    #Determines if comment can be added to post. If so returns readability information
    def check_comment_status(self, USERNAME):
        comment_author = []
        readability_data = [] #Will contain content and wordcount of article
        has_relevant_flair = self.post_flair in relevant_flair

        url_info = urlparse(self.post_url)
        #This checks to see if any part of the url name is in the news source list
        for x, y in enumerate(news_sources):
            if url_info.netloc.find(news_sources[x]) > 0:
                approved_news_source = True
                break
            else:
                approved_news_source = False

        #Check to see if bad_news_sources has any content before we try to enumerate it. If it is 0 then we know that the submitted url cannot possibly be a bad news source.
        if len(bad_news_sources) > 0:
            for x, y in enumerate(bad_news_sources):
                if url_info.netloc.find(bad_news_sources[x]) > 0:
                    unapproved_news_source = True
                    break
                else:
                    unapproved_news_source = False

        else:
            unapproved_news_source = False

        #Check here to see if the post has the approved subreddit flair
        if (has_relevant_flair or approved_news_source) and (unapproved_news_source is False):
            submission_instance = self.submission
            comments = submission_instance.comments

            #Look through all the comments and get each author, put each one into an array fix for loop to more 'pythony' type TMT
            for i, j in enumerate(comments):
                comment_individual = submission_instance.comments[i]
                comment_author.append(str(comment_individual.author))

            #Check here to see if bot user name is in list of comment authors in post
            if USERNAME not in comment_author:
                reddit_comment_content = self.set_comment_content()
                print "Comment content set : " + time.asctime( time.localtime(time.time()) )
                return reddit_comment_content

            else:
                print "No comment content set. This bot has already commented once : " + time.asctime( time.localtime(time.time()) )
                print "Post ID: {0} Post URL: {1}".format(self.post_id, self.post_url)
                reddit_comment_content = None
                return reddit_comment_content

        else:
            print "No comment content set. Wrong flair, news source is not approved, or news source is flagged as bad : " + time.asctime( time.localtime(time.time()) )
            print "Post ID: {0} Post URL: {1}".format(self.post_id, self.post_url)
            #print "We cannot comment because it doesn't have the !\n"
            reddit_comment_content = None
            return reddit_comment_content

    def set_comment_content(self):
        url = self.post_url

        diffbot = diffbotClient() # Make a new diffbot client

        api = "article" # Set the type of web content we'll be analyzing (always article in this case)
        response = diffbot.request(url, api) # Returns the json request

        article_title = diffbot.get_article_title(response) # Returns the article title from the json request
        article_text = diffbot.get_article_text(response) # Returns the article text from the json request
        article_image_url = diffbot.get_article_image_url(response) #Returns the article image from the json request

        if (len(article_text) > character_post_min) and (len(article_text) < character_post_max): #We've got to have at least 10 characters, that's probably a sentence's worth, otherwise don't post because there's probably some other issue. If there's more than 5000 characters, we don't want to post that because it's way to big.

            #Check to see if we have an image stored in article_image_url. If so post one link, if no post the other. Note, I come across very few news sources without articles, but this is completely dependent on what ever the text extractor API returns. It could be something completly unrelated.
            if article_image_url is not None:
                my_comment_content = "**%s**\n \n [Image](%s) \n \n %s \n \n*This comment was made by a bot. Please post bugs and comments to /r/SCNewsHelper*" % \
                (article_title, article_image_url, article_text)

                return my_comment_content

            else:
                my_comment_content = "**%s**\n \n %s \n \n*This comment was made by a bot. Please post bugs and comments to /r/SCNewsHelper*" % \
                (article_title, article_text)

                return my_comment_content

        elif (len(article_text) < character_post_min):
            print "Comment character count less than %s : %s" % \
            (str(character_post_min), time.asctime( time.localtime(time.time()) ))
            my_comment_content = None
            return my_comment_content

        else:
            print "Comment character count greater than %s : %s" % \
            (str(character_post_max), time.asctime( time.localtime(time.time()) ))
            my_comment_content = None
            return my_comment_content

    def get_submission(self):
        return self.submission

    def get_post_ID(self):
        return self.post_id
