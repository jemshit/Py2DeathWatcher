## Py2DeathWatcher

### Setup

1. `cd workspaceDirectory`
2. `git clone https://github.com/jemshit/Py2DeathWatcher.git`
3. `cd Py2DeathWatcher`
4. Create file `files/twitter_api_secrets.toml` with content:

```
TWITTER_API_KEY_PY2WATCHER = 'twitter developer api key'
TWITTER_API_SECRET_KEY_PY2WATCHER = 'twitter developer api secret key'
```
5. App uses OS-User default `crontab` file to schedule jobs. If you want to use custom crontab file:

   a. Replace `CronTab(user=True)` with `CronTab(user=None, tabfile=TAB_FILE)`

   b. `USER_CRONTAB_ENABLED = True`

   c. Replace `self.cron.write_to_user()` with `self.cron.write(TAB_FILE)`
   
   d. In terminal, `crontab workspaceDirectory/Py2DeathWatcher/files/cron_jobs.tab`

6. `pip3 install virtualenv`
7. `virtualenv venv`
8. `source venv/bin/activate`
8. `pip3 install -r requirements.txt`
9. `chmod +x src/app.py` (to create files)
10. `python3 src/app.py`

If everything goes well, it will send first tweet and schedule the next tweet job. 
