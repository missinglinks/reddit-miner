"""
Subreddit Miner
a simple subreddit scraper

author: peter.muehleder@uni-leipzig.de
"""

import json
import requests
import pandas as pd
import os
from datetime import datetime

#subreddit url
REDDIT_URL = "https://www.reddit.com/r/{subreddit}/.json?after={page}&t=all"


class SubredditMiner:

    def __init__(self, subreddit):
        self.subreddit = subreddit
        self.threads = []

    def _getReplies(self, data):
        """recursively goes through every comment in a thread"""
        comments = []
        for reply in data["data"]["children"]:
            
            #check if reply is comment ("t1")
            if reply["kind"] == "t1":
                
                author = reply["data"]["author"]               
                distinguished = reply["data"]["distinguished"]
                created = reply["data"]["created"]
                comment_id = "t1_{}".format(reply["data"]["id"])
                parent = reply["data"]["parent_id"]
                text = reply["data"]["body"]

                comments.append({
                    "id": comment_id,
                    "author": author,
                    "parent_id": parent,
                    "distinguisehd": distinguished,
                    "created": created,
                    "text": text
                })

                if reply["data"]["replies"] != "":
                    comments += self._getReplies(reply["data"]["replies"])
        return comments

    def _getThread(self, url):
        """fetches subreddit thread provided by _url_"""
        comments = []
        
        results = requests.get("https://www.reddit.com"+url+".json?sort=new", headers = {'User-agent': 'your bot 0.1'})
        data = results.json()
        
        #get information of thead post and add it as first comment
        first = data[0]["data"]["children"][0]["data"]
        author = first["author"]
        distinguished = first["distinguished"]
        created = first["created"]
        comment_id = first["name"]
        text =  "{}\n{}".format(first["title"],first["selftext"])
        parent = ""
        comments.append({
            "id": comment_id,
            "author": author,
            "text": text,
            "parent_id": parent,
            "distinguished": distinguished,
            "created":created
        })
        
        #get all replys to post and add them as comments
        comments += self._getReplies(data[1])
        
        return comments

    def read(self):
        """reads out all available threads in a subreddit"""
        page = ""
        page_count = 0
        print("{} - {}".format(self.subreddit, datetime.now().isoformat()))
        while page != None:
            
            results = requests.get(REDDIT_URL.format(page=page, subreddit=self.subreddit), headers = {'User-agent': 'your bot 0.1'})
            data = results.json()
            page = data["data"]["after"]
            page_count += 1
            print("... fetching page {}".format(page_count))
            for entry in data["data"]["children"]:
                
                #get general information of the thread
                title = entry["data"]["title"]
                thread_id = entry["data"]["id"]
                permalink = entry["data"]["permalink"]
                domain = entry["data"]["domain"]
                url = entry["data"]["url"]
                author = entry["data"]["author"]
                thread_name = entry["data"]["name"]
                flair = entry["data"]["link_flair_text"]
                date = entry["data"]["created"]
                ups = entry["data"]["ups"]
                num_comments = entry["data"]["num_comments"]
                
                #get the whle tread via its permalink
                comments = self._getThread(permalink)
                
                self.threads.append({
                    "id": thread_id,
                    "thread_name": thread_name,
                    "permalink": permalink,
                    "flair": flair,
                    "title": title,
                    "author": author,
                    "created": date,
                    "ups": ups,
                    "num_comments": num_comments,
                    "comments": comments,
                    "url": url,
                    "domain":domain
                })

    def comments(self):
        pass

    def authors(self):
        pass
    
    def save(self, directory="./output/"):
        """saves subreddit threads as json file with timestamp"""

        path = "{}/{}/".format(directory, self.subreddit)
        if not os.path.exists(path):
            os.makedirs(path)
        filepath = "{}/{}.json".format(path, datetime.now().isoformat())
        with open(filepath,"w") as out_file:
            json.dump(self.threads, out_file)
