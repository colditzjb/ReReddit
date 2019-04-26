# REFREDDIT (i.e., REFresh REDDIT data)
Here is a Python script to capture real-time Reddit text data. This code was initially developed for the [Center for Research on Media, Technology, and Health](http://mth.pitt.edu/) at the University of Pittsburgh. We're primarily interested in Reddit discussions about recovery from problematic alcohol, smoking/vaping, and other substance use. If you are interested in collaborating along this line of research, you can contact us at crmth@pitt.edu

### Overview:
This documentation is somewhat lacking in details and examples, so feel free to fork and pull request this README if you decide to play with the code. If you come up with a creative way to work with the resulting data, please share that also! This is just a text and metadata capture tool for now. Text capture is not particularly useful in subreddits that are mostly comprised of images and links, unless you are really interested in the comment text.

The ```refreddit.py``` script uses Reddit's [PRAW](https://github.com/praw-dev/praw) library (so install that first) and connects you to the [Reddit API](https://www.reddit.com/dev/api/) (you need to [obtain your own Reddit developer credentials](https://redditclient.readthedocs.io/en/latest/oauth/) for this). The process runs an endless data collection loop until you manually kill it. One of my implementations has been running consistently for 8+ months. This is a fun process to set-and-forget on a Raspberry Pi or similar low-maintenance, seldom-interfaced, usually-uptime Linux system (you may want to [set up _crontab_ to start it on reboot](https://learn.pimoroni.com/tutorial/sandyj/running-scripts-at-boot)).

### Behavior:
Initially, REFREDDIT will collect up to 1000 most-recent posts and associated comments that are available from the subreddits that you choose - this can be time consuming due to API limits. After those data are captured, it will regularly loop back and check for new posts. It systematically checks for updates to posts that were captured so the output data will also include new comments, edited text of previously captured posts (saved as separate text files), and whether a post was removed by moderators or deleted by the original poster. The update process is intelligent and streamlined only insomuch as it prioritizes newer posts, is aware of post edits and removals, and reacts to comment count increases in the post metadata.

### Data format:
Output subfolder structure is: (1) subreddit name, (2) post capture date as _YYYYMMDD_ format, (3) post ID, (4) comment ID and the comment ID that was responded to if the comment was a response (flattening but preserving network edge structure as folder names). Text data are stored in .txt files within post and comment subfolders (file name is epoch datetime of the post/comment - post time, not collection time). Some metadata are also stored in .csv files within these folders (includes data capture timestamps, upvote minus downvote score, number of comments, etc.). Metadata are appended every time a post is checked for updates, so you can see some progression of post activity. 

_Note:_ Because the data consist of many small files, a file system with a small cluster size is ideal so that the output doesn't take up too much disk space. For example, if you are backing up a large amount of data to a dedicated flash drive, you might want to format it as NTFS with 512 byte cluster allocation size (this option is standard but not default when formatting in Windows). In one use case, this reduced the overall storage size by a 1:5 magnitude.  

### Other technical notes:
The Reddit API is rate limited, so data refresh frequency is inversely related to the number of subreddits that you scour. Selecting many highly-active subreddits will slow the refresh rate, for sure. Choose wisely. 

The process relies on reviewing metadata output to know what new data needs collecting. If you remove files or folders from the established data output directories, it will assume that the data don't exist and waste time recollecting them. Posts older than 180 days are "locked" by Reddit so those _might_ be safe to move (but only if they preceed the 1000 most recent posts - there's some ambiguity around this in the code because I only just thought about it while typing this sentence). The current refresh settings _probably_ ignore posts that are older than 30 days, because I picked an arbitrary number to reduce API call overhead. Change the refresh settings and relocate output data at your own risk!

This implementation includes an optional dependency on Sentry's Raven library so that errors can be re-broadcast to a Slack channel or other notification platform. I think that I managed to comment-out all of those dependencies in the code. 

### Wishlist for future code:
An obvious limitation of this code is that it doesn't actually do anything with the data after they are collected. I am up for including additional scripts in this repository if they are useful for broad use cases. A few examples of useful functions might be:

* Creating text corpora of all collected posts and/or comments from selected subreddits. This would need to be customizable, so that others could easily pass arguments to define some output parameters (e.g., select only posts or only comments, filter by post date, minimum or maximum text length, prefer original vs. edited content, etc.).
* Re-create the original thread structure (i.e., comments and response nesting) in tree format, or compiling comment output in some semblance of thread structure for discourse analysis. 
* Evaluating descriptive stastictics of subreddits (e.g., post frequency, number of comments per post, most/least active days or times for posting).
* Other stuff is welcome too - use your imagination!
