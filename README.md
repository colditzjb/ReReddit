# refreddit

Documentation is mostly lacking, so feel free to pull and update this if you figure out how to use it. Also, if you come up with a useful way to work with the resulting data, please share that. This is just a text capture tool for now. It's not particularly useful in subreddits that are mostly images and links (unless you are interested in the comment text).


The ```refreddit.py``` script uses Reddit's PRAW library (so install that first) and connects you to the Reddit API (you must provide your own Reddit developer credentials). It runs on an endless loop until you turn it off. One of my implementations has been running consistently for 8+ months. This is a fun tool to put on a Raspberry Pi and promply forget about (be sure to set up crontab to re-start it on reboot).


Also: The Reddit API is rate limited, so your data refresh frequency is inversely related to the number of subreddits that you scour. 


### Behavior
On first run, it will collect all past posts and replies that are available from the subreddits that you select. I think this is limited to 100 or-so historic posts? After that is done, it will loop back and check for new posts. Then it checks for updates to the posts that were collected, so the output data will include new replies and any edits to the original post. 

### Data format
Folder structure is: (1) subreddit name, (2) post capture date as YYYYMMDD format, (3) post ID, (4) comment ID and comment ID that was responded to. Text data are stored in .txt files within folders (file name includes epoch datetime of the post or comment). Metadata are stored in .csv files within folders (includes  data capture timestamps, current upvotes and downvotes, etc.). 

