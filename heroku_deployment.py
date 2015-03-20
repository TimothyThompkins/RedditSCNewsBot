# heroku_deployment.py

# This is just an easy place to change if the app is being run locally or on heroku

class herokuDeployment(object):
    local_deployment = False

    @staticmethod
    def get_time_stamp(self):
        if local_deployment is True:
            return time.asctime( time.localtime(time.time()) )

        else:
            return ''
