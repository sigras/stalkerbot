from pattern.vector import words, count
import operator
import reddit

class Stalkerbot(object):
    def __init__(self, username=None, password=None):
        self.r = reddit.Reddit(user_agent='testing')

        if username and password:
            self.r.login(username, password)
            print self.r

    def get_victim(self, popular=False, username=None):
        """
        Returns randomly chosen victim and its original comment
        """
        # TODO: Add minimum comment karma requirement if popular == True
        # TODO: Add option to manually input username
        # TODO: Add mechanism to avoid getting same victim in a 24 hour span.
        if popular:
            submission = list(self.r.get_subreddit('all').get_top(limit=1))
            comment = submission[0].comments[0]
            username = comment.author.__str__()
            return username, comment
        else:
            comments = list(self.r.get_all_comments())
            username =  comments[0].author
            return username, comments[0]

    def get_comment_history(self, username):
        user = self.r.get_redditor(username)
        comment_history = list(user.get_comments())
        return comment_history

    def get_keywords(self, comment_history):
        comments = [str(x) for x in comment_history]
        keywords = count(words(comments.__str__()))
        sorted_keywords = sorted(keywords.iteritems(), key=operator.itemgetter(1), reverse=True)
        print sorted_keywords
        return sorted_keywords

    def get_favorite_subreddits(self, comment_history, username=None):
        if username and not comment_history:
            comment_history = self.get_comment_history(username)

        subreddit = {}
        for comment in comment_history:
            if comment.subreddit.__str__() in subreddit:
                subreddit[comment.subreddit.__str__()] += 1
            else:
                subreddit[comment.subreddit.__str__()] = 1

        sorted_subreddits = sorted(subreddit.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sorted_subreddits 
    
    def get_info(self, username):
        user = self.r.get_redditor(username)
        data = user._get_json_dict()
        return data['has_mail'], data['created'], data['link_karma'], \
            data['comment_karma'], data['is_gold'], data['is_mod']

    def reply(self, comment, text):
        return comment.reply(text)

    def check_inbox(self):
        pass

    def reply_inbox(self):
        pass

def run():
    bot = Stalkerbot('ImNotStalkingYou', 'notthepasswordyourelookingfor')
    username, comment = bot.get_victim(popular=True)
    comment_history   = bot.get_comment_history(username)
    keywords          = bot.get_keywords(comment_history)
    subreddits        = bot.get_favorite_subreddits(comment_history)
    has_mail, created, link_karma, comment_karma, \
    is_gold, is_mod   = bot.get_info(username)

    # This isn't working correctly.
    # Need to remove spaces in order to get table layout on Reddit.
    text = """
           *%s* user data
           subject|data
           :---|:--:|---:
           keywords in user's comment history | %s, %s, %s
           subreddits this user frequently visist | %s, %s, %s
           email address linked to Reddit? | %s
           link karma | %s
           comment karma | %s
           has Reddit Gold? | %s
           is a moderator of a subreddit? | %s
           """ % (username, keywords[0][0], keywords[1][0], keywords[2][0], subreddits[0][0], subreddits[1][0], \
               subreddits[2][0], has_mail, link_karma, comment_karma, is_gold, is_mod)
    print text

    # For testing purposes, in case information returned is incorrect.
    # Should stay until bot is working properly.
    decision = raw_input("Reply? ")
    if decision == 'yes':
        comment.reply(text)
    else:
        run()

    print 'Successfully replied...'

if __name__ == "__main__":
    run()
