#diffbot_client.py
#a_soy_milkshake
#March 2015

#This is the diffbot client that sends requests to api.diffbot.com

import requests
import json
import types
import time
from diffbot_api_key import diffbot_api_token
from bs4 import BeautifulSoup

class diffbotClient(object):

    base_url = 'http://api.diffbot.com/'

    # Makes the request to the diffbot api
    def request(self, url, api, token = diffbot_api_token, version = 3):

        # Returns a python object containing the requested resource from the diffbot api
        payload = {"url": url, "token": token}

        try:
            print "Requesting response from {0} : {1}".format(self.base_url, time.asctime( time.localtime(time.time()) ))
            #response.raise_for_status() #Eventually include to check for HTML Server Response Errors TMT
            response = requests.get(self.format_url(api, version), params=payload)
            json_data = response.json()

        except:
            print "Response failure from {0} : {1}".format(self.base_url, time.asctime( time.localtime(time.time()) ))

        return json_data

    # Formats the url for use in the request.
    def format_url(self, api, version_number):

        # Formats the url for the api call

        version = 'v{}'.format(version_number)
        return '{}{}/{}'.format(self.base_url, version, api)

    # Returns the title of the article
    @staticmethod
    def get_article_title(json_data):

        article_title = json_data['objects'][0]['title'] #Gets the article title from the list objects
        return article_title

    # This retuns the cleaned text from the html in the json that is returned from the response
    @staticmethod
    def get_article_text(json_data):

        #This method is to replace the elements in some string with a some other element, in our case 'p' with 'br'. That way we have line breaks between paragraphs
        def replace_with_newlines(element):
            text = ''
            for elem in element.recursiveChildGenerator():
                if isinstance(elem, types.StringTypes):
                    text += elem.strip()
                elif elem.name == 'br':
                    text += '\n'
            return text

        #article_text = json_data['objects'][0]['text'] #Gets the text parameter from the list objects
        article_html = json_data['objects'][0]['html'] #Gets the text parameter from the list objects

        soup = BeautifulSoup(article_html)

        formatted_output = ''

        #Concate each previous line with a new one containing a paragraph break
        for line in soup.findAll('p'):
            line = replace_with_newlines(line)
            formatted_output += line +'\n'+'\n' #We could remove the last two new lines from the output, but b/c I'm adding a message at the end of my comment, I like the extra space.

        return formatted_output

    # Returns the image url associated with an article
    @staticmethod
    def get_article_image_url(json_data):

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

            print "Retrival of image tag failed : %s" % \
            (time.asctime( time.localtime(time.time()) ))
            return None

        return reddit_html_link_fixer(article_image_url)
