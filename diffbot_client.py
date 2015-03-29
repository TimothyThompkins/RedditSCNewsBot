# diffbot_client.py
# a_soy_milkshake

# This is the diffbot client that sends requests to api.diffbot.com

import json
import types
import time
import os

import requests
from bs4 import BeautifulSoup
from heroku_deployment import herokuDeployment

#If this fails below the app should quit itself
h = herokuDeployment()

if h.local_deployment is True:
    file = open('diffbot_api_token.txt', 'r')
    diffbot_api_token = file.readline().strip() #Reads first line

else:
    diffbot_api_token = os.environ['diffbot_api_token']


class diffbotClient(object):

    base_url = 'http://api.diffbot.com/'

    # Makes the request to the diffbot api
    def request(self, url, api, post_id, token = diffbot_api_token, version = 3):

        # Returns a python object containing the requested resource from the diffbot api
        payload = {"url": url, "token": token}
        json_data = None # Initialize Json Data so that it returns a null value if the call is bad

        try:
            print "Requesting response from {0} for Post ID: {1} : {2}".format(self.base_url, post_id, time.asctime( time.localtime(time.time()) ))
            #response.raise_for_status() #Eventually include to check for HTML Server Response Errors TMT
            response = requests.get(self.format_url(api, version), params=payload)
            response.raise_for_status()
            json_data = response.json()

        except:
            print "Response failure from {0} : {1}".format(self.base_url, time.asctime( time.localtime(time.time()) ))

        # Eventually better error handling needs to be implemented

        # except requests.exceptions.ConnectTimeout as e:
        #     print "Connection timed out : {0}".format(time.asctime(time.localtime(time.time()) ))
        #
        # except requests.exceptions.HTTPError as e:
        #     print "HTTP Error {0} : {1}".format(time.asctime(e.message, time.localtime(time.time()) ))


        return json_data

    # Formats the url for use in the request.
    def format_url(self, api, version_number):

        # Formats the url for the api call

        version = 'v{}'.format(version_number)
        return '{}{}/{}'.format(self.base_url, version, api)

    # Returns the title of the article
    @staticmethod
    def get_article_title(json_data, post_id):

        if (json_data is not None):
            try:
                article_title = json_data['objects'][0]['title'] #Gets the article title from the list objects

            except:
                print "Error getting article title from Json for Post ID: {0} : {1}".format(post_id, time.asctime( time.localtime(time.time()) ))
                article_title = "ERROR: NO ARTICLE TITLE COULD BE RETRIEVED"

        else:
            article_title = "ERROR: NO ARTICLE TITLE COULD BE RETRIEVED"

        return article_title

    # This retuns the cleaned text from the html in the json that is returned from the response
    @staticmethod
    def get_article_text(json_data, post_id):

        #This method is to replace the elements in some string with a some other element, in our case 'p' with 'br'. That way we have line breaks between paragraphs
        def replace_with_newlines(element):
            text = ''
            for elem in element.recursiveChildGenerator():
                if isinstance(elem, types.StringTypes):
                    text += elem.strip()
                elif elem.name == 'br':
                    text += '\n'
            return text

        if (json_data is not None):
            try:
                article_html = json_data['objects'][0]['html'] #Gets the text parameter from the list objects

                soup = BeautifulSoup(article_html)

                formatted_output = ''

                #Concate each previous line with a new one containing a paragraph break
                for line in soup.findAll('p'):
                    line = replace_with_newlines(line)
                    formatted_output += line +'\n'+'\n' #We could remove the last two new lines from the output, but b/c I'm adding a message at the end of my comment, I like the extra space.

            except:
                print "Error getting article text from Json for Post ID: {0} : {1}".format(post_id, time.asctime( time.localtime(time.time()) ))
                formatted_output = None


        else:
            formatted_output = None

        return formatted_output

    # Returns the image url associated with an article
    @staticmethod
    def get_article_image_url(json_data, post_id):

        # This method fixes links that will be posted to reddit. Links that contain parentheses have issues as defined here: http://www.reddit.com/wiki/commenting
        def reddit_html_link_fixer(orig_string):

            fixed_link = ""

            for current_character in orig_string:

                if (current_character is '(') or (current_character is ')'):
                    fixed_link += ('\\' + current_character)

                else:
                    fixed_link += current_character

            return fixed_link

        try:

            article_image_url = json_data['objects'][0]['images'][0]['url'] #Gets the article title from the list objects

        except:

            print "Retrival of image tag failed for post with post ID: %s : %s" % \
            (post_id, time.asctime( time.localtime(time.time()) ))
            return None

        return reddit_html_link_fixer(article_image_url)
