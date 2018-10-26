# refreddit

Documentation is somewhat lacking, so feel free to pull and update this if you figure out how to use the code. If you come up with a creative way to work with the resulting data, please share that also! This is just a text capture tool for now. It's not particularly useful in subreddits that are mostly composed of images and links, unless you are really interested in the comment text.

The ```refreddit.py``` script uses Reddit's PRAW library (so install that first) and connects you to the Reddit API (you must provide your own Reddit developer credentials for this). The process runs on an endless loop until you manually kill it. One of my implementations has been running consistently for 8+ months. This is a fun script to run on a Raspberry Pi and promply forget about (remember to set up crontab to re-start it on reboot).


### Behavior
On first run, it will collect historic posts and comments that are available from the subreddits that you select - this takes some time. I think historic data is limited to 1000 or-so posts. After that is done, it will loop back and check for new posts. Then it checks for updates to posts that were collected, so the output data will include new replies and edited versions of post text. 

### Data format
Output folder structure is: (1) subreddit name, (2) post capture date as YYYYMMDD format, (3) post ID, (4) comment ID and the comment ID that was responded to, if the comment is a response. Text data are stored in .txt files within folders (file name includes epoch datetime of the post or comment). Some metadata are stored in .csv files within folders (includes data capture timestamps, upvote minus downvote score, number of comments, etc.). 


### Other technical notes:
The Reddit API is rate limited, so data refresh frequency is inversely related to the number of subreddits that you scour. Choose wisely. 

The process relies on reviewing metadata output to know what new data needs collecting. So, if you move files or folders out of the established data output directories, it will assume that the data don't exist and waste time recollecting them. Posts older than 180 days are considered "retired" so those might be safe to move (but only if they preceed the 1000 most recent posts - there's some ambiguity around this in the code because I only just thought about it while typing this sentence). 

This implementation includes an optional dependency on Sentry's Raven library (so that errors can be broadcast to a Slack channel). I think that I managed to comment-out all of those dependencies in this code. 

