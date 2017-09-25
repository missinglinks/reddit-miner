import sys
from scraper.subredditminer import SubredditMiner

if __name__ == "__main__":
    subreddit = sys.argv[1]
    reddit = SubredditMiner(subreddit)
    reddit.read()
    reddit.save()