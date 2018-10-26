# REFREDDIT (i.e., REFresh REDDIT data)
A Python script to capture semi-real-time Reddit text data.

### Overview:
Documentation is somewhat lacking, so feel free to pull and push this README if you decide to play with the code. If you come up with a creative way to work with the resulting data, please share that also! This is just a text capture tool for now. Text capture is not particularly useful in subreddits that are mostly comprised of images and links, unless you are really interested in the comment text.

The ```refreddit.py``` script uses Reddit's PRAW library (so install that first) and connects you to the Reddit API (you must provide your own Reddit developer credentials for this). The process runs an endless data collection loop until you manually kill it. One of my implementations has been running consistently for 8+ months. This is a fun process to set-and-forget on a Raspberry Pi or similar low-maintenance, seldom-interfaced, usually-uptime Linux system (but remember to set up _crontab_ to re-start it on reboot).


### Behavior:
On first run, it will collect up to 1000 most-recent posts and associated comments that are available from the subreddits that you select - this takes some time due to API limits. After those data are captured, it will loop back and check for new posts. Then it systematically checks for updates to posts that were collected, so the output data will also include newer comments and edited text of previously captured posts.

### Data format:
Output subfolder structure is: (1) subreddit name, (2) post capture date as _YYYYMMDD_ format, (3) post ID, (4) comment ID and the comment ID that was responded to if the comment is a response (flattening but preserving comment thread structure). Text data are stored in .txt files within post and comment subfolders (file name is epoch datetime of the post or comment). Some metadata are also stored in .csv files within these folders (includes data capture timestamps, upvote minus downvote score, number of comments, etc.). Metadata are appended every time a post is checked for updates, so you can see some progression of post activity.


### Other technical notes:
The Reddit API is rate limited, so data refresh frequency is inversely related to the number of subreddits that you scour. Selecting many highly-active subreddits will slow the refresh rate, for sure. Choose wisely. 

The process relies on reviewing metadata output to know what new data needs collecting. If you move files or folders out of the established data output directories, it will assume that the data don't exist and waste time recollecting them. Posts older than 180 days are considered "retired" so those might be safe to move (but only if they preceed the 1000 most recent posts - there's some ambiguity around this in the code because I only just thought about it while typing this sentence). Relocate data output at your own risk!

This implementation includes an optional dependency on Sentry's Raven library so that errors can be re-broadcast to a Slack channel or other notification platform. I think that I managed to comment-out all of those dependencies in the code. 

