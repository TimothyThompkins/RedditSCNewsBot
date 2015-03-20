# reddit_post.py
# a_soy_milkshake

# This function checks our posts and determines if we should comment

import time
from urlparse import urlparse

from diffbot_client import diffbotClient

relevant_flair= ['news' , 'sports']

news_sources = ['thestate', 'yahoo', 'myrtlebeachonline', 'nbc', 'wspa', 'cbs', 'greenvilleonline', 'theguardian', 'enquirehearld', 'huffpost','wcnc', 'cnn', 'islandpacket', 'postandcourier', 'greenvilleonline', 'goupstate', 'hearldonline', 'free-times', 'aikenstandard', 'charlestoncitypaper', 'myrtlebeachonline', 'charlotteobserver', 'nbcnews', 'cbsnews', 'cnn', 'wbtw', 'washingtontimes', 'foxnews', 'npr', 'wyff4', 'carolina live', 'usatoday', 'wjcl', 'live5news', 'foxcarolina', 'wistv', 'rawstory', 'thenonprofittimes', 'nytimes', 'nydailynews', 'abcnews4', 'washingtonpost', 'wltx', 'c-span', 'msnbc', 'wmbfnews', 'charlotteobserver', 'weeklystandard', 'politico', 'wncn', 'fitsnews', 'dailykos', 'nbc4i', 'forbes', 'reuters', 'cbs46', 'wjbf', 'moultrienews', 'wsoctv', 'indexjournal', 'espn', 'deadspin']

blacklist_news_sources = []
#Our comment must be between these ranges in order to post
character_post_min = 40
character_post_max = 6000

class redditPost:

    def __init__(self, post_flair, post_url, post_id, submission_instance, comment_authors=None):
    #def __init__(self, **kwargs):
        self.post_flair = post_flair
        self.post_url = post_url
        self.post_id = post_id
        self.submission_instance = submission_instance

        if comment_authors is None:
            self.comment_authors = []
        else:
             self.comment_authors = comment_authors

    #Test to display data about object created
    def displayRedditPostData(self):
        print self.post_flair
        print self.post_url
        url_info = urlparse(self.post_url)
        print url_info.netloc
        print self.post_id

    #Determines if comment can be added to post. If so returns readability information
    def check_comment_status(self, USERNAME):
        has_relevant_flair = self.post_flair in relevant_flair

        url_info = urlparse(self.post_url)
        #This checks to see if any part of the url name is in the news source list
        for x, y in enumerate(news_sources):
            if url_info.netloc.find(news_sources[x]) > 0:
                approved_news_source = True
                break
            else:
                approved_news_source = False

        #Check to see if blacklist_news_sources has any content before we try to enumerate it. If it is 0 then we know that the submitted url cannot possibly be a bad news source.
        if len(blacklist_news_sources) > 0:
            for x, y in enumerate(blacklist_news_sources):
                if url_info.netloc.find(blacklist_news_sources[x]) > 0:
                    unapproved_news_source = True
                    break
                else:
                    unapproved_news_source = False

        else:
            unapproved_news_source = False

        #Check here to make sure it's not in the blacklist of news sources
        if unapproved_news_source is False:

            if (has_relevant_flair or approved_news_source):
                #Check here to see if bot user name is in list of comment authors in post
                if USERNAME not in self.comment_authors:
                    reddit_comment_content = self.set_comment_content()

                    if reddit_comment_content is not None:
                        print "Comment content set. Post ID: {0} : {1} ".format(self.post_id, time.asctime( time.localtime(time.time()) ))
                        return (True, reddit_comment_content)

                    else:
                        print "No comment content set. Character count out of range. Post ID: {0} : {1} ".format(self.post_id, time.asctime( time.localtime(time.time()) ))
                        reddit_comment_content = 'character_count'
                        return (False, reddit_comment_content)

                else:
                    print "No comment content set. This bot has already commented once. Post ID: {0} : {1} ".format(self.post_id, time.asctime( time.localtime(time.time()) ))
                    reddit_comment_content = 'commented'
                    return (False, reddit_comment_content)


            elif has_relevant_flair is False:
                #submission_instance.link_flair_text returns 'None' if there is no flair
                if self.post_flair == 'None':
                    print "No comment content set. Post has NO flair and is not an approved source. Post ID: {0} : {1} ".format(self.post_id, time.asctime( time.localtime(time.time()) ))
                    reddit_comment_content = 'no_flair'
                    return (False, reddit_comment_content)

                else:
                    print "No comment content set. Post has WRONG flair and is not an approved source. Post ID: {0} : {1} ".format(self.post_id, time.asctime( time.localtime(time.time()) ))
                    reddit_comment_content = 'wrong_flair'
                    return (False, reddit_comment_content)

            else:
                print "No comment content set. Post has WRONG flair and is not an approved source. Post ID: {0} : {1} ".format(self.post_id, time.asctime( time.localtime(time.time()) ))
                reddit_comment_content = 'wrong_flair'
                return (False, reddit_comment_content)

        else:
            print "No comment content set. News Source is Black-listed. Post ID: {0} : {1} ".format(self.post_id, time.asctime( time.localtime(time.time()) ))
            reddit_comment_content = 'blacklist'
            return (False, reddit_comment_content)


    def set_comment_content(self):
        url = self.post_url

        diffbot = diffbotClient() # Make a new diffbot client

        api = "article" # Set the type of web content we'll be analyzing (always article in this case)
        response = diffbot.request(url, api, self.post_id) # Returns the json request

        article_title = diffbot.get_article_title(response) # Returns the article title from the json request
        article_text = diffbot.get_article_text(response) # Returns the article text from the json request
        article_image_url = diffbot.get_article_image_url(response, self.post_id) #Returns the article image from the json request

        if (len(article_text) > character_post_min) and (len(article_text) < character_post_max): #We've got to have at least min number of characters, that's probably a sentence's worth, otherwise don't post because there's probably some other issue. If there's more than 5000 characters, we don't want to post that because it's way to big.

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
            print "Comment character count less than %s. Post ID: %s : %s" % \
            (str(character_post_min), str(self.post_id), time.asctime( time.localtime(time.time()) ))
            my_comment_content = None
            return my_comment_content

        else:
            print "Comment character count greater than %s. Post ID: %s : %s" % \
            (str(character_post_max), str(self.post_id), time.asctime( time.localtime(time.time()) ))
            my_comment_content = None
            return my_comment_content

    def get_submission_instance_current(self):
        return self.submission_instance

    def get_post_ID(self):
        return self.post_id
