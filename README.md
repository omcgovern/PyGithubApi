# Repository Analyser

This is a command line Python script to clone the Teckro Github repos and analyse them 
to extract metadata and dump it to a CSV file for analyse in Excel.

# To Install

    python -m venv my_env
    source my_env/bin/activate
    pip install -r requirements.txt

# To configure

The script will attempt to read the configuration file ~/GitRepos.properties
If the property file does not exist I create a blank version e.g.

    # GitHub settings

    github.organisation_name=Teckro-Production    
    github.custom_hostname=
    github.access_token=<your Github Access token>
    github.skipProjects=Interviews,PaxHeader,Performance,Platform_Infrastructure,Validation
    github.skipRepos=
    github.repoDir=/Users/<your OS username>/Repositories/Github
    
    # Generic
    general.throttleSleepSecs=0


# Generating a Github access token

Login to Github via your Onelogin link as normal, ending up in https://github.com/orgs/Teckro-Production/repositories
Click on your user profile icon on the right hand side.
Select "Settings"
Go down to the end to "Developer Settings"
Select "Personal access tokens"
I just selected the "Tokens (classic)" option, but you may want to limit the API access with "Fine-grained tokens"
Select "Generate new token" -> "Generate new token(classic)"
Add a name of your token in "Note", eg. "Owens Token 2023"
Select the expiration, and select all the access scopes you think you'll need.
At a minimum I imagine that will be 
- repo
  - repo:status
- admin:org
  - read:org
- project
  - read:project

After clicking "generate token" you MUST copy your access token... otherwise it will disappear.

Now... go back to the list of your personal access tokens and see that it there.
You now need to click on "Configure SSO" beside your token and click on the "Authorize" button beside the 
"Teckro-Production" Github organisation.


# Initial run - basically a git clone all the repos not explicitly listed above for skipping

This will iterate through all the repos not to be skipped and clone them to the local directory specified in repoDir in your BitBucket.properties configuration files.
Run the following to iterate through your local git repos and pull the latest code from master.

> *Warning : Bitbucket/Github may throttle requests. So I allow 3 retry attempts before failing*

    python main.py clone

# Periodic Update - basically a git pull.  It will fail if you have local changes

> *Warning : It appears that BitBucket may be throttling requests. So I allow 3 retry attempts before failing*

    python main.py update

# Analyse

Run this to generate repo_metrics.csv within your current directory which you can then import into Ms. Excel.

    python main.py analyse

# To add more metrics

See RepoDirectory.py, the scan() method.
I've a number of handy methods to analyse an individual Git repo directory.

| Method                                            | Returns                                            | Example                                                      | Description                                                                                                                      |
|---------------------------------------------------|----------------------------------------------------|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| RepoDirectory.has_file(filename)                  | True/False                                         | repo.has_file("Dockerfile")                                  | Recurse through the repo and returns true if it finds at least one matching file                                                 |                                               
| RepoDirectory.search_files_regex(filename, regEx) | string                                             | repo.search_files_regex("Dockerfile", r'^FROM\s(.*)$')       | Searches for a file and returns the first matching RegEx expression.  Eg. here the base docker image                             |
| RepoDirectory.get_build_system()                  | GRADLE_KOTLIN,GRADLE_JAVA,MAVEN,WEB,PYTHON,UNKNOWN | repo.get_build_system()                                      | Based on the presence of build specific files. Returns an enum whose value contains the filename we found eg. "build_gradle.kts" |
| RepoDirectory.search_files(filename, find_str)    | True/False                                         | repo.search_files(self.get_build_system().value, "snapshot") | Simple string searching of a file, not RegEx.                                                                                    |


# For Corporate VPNS

If you get invalid SSL certs connecting to GitHub add the following environment variable
which should point to your own companies SSL root certificate

REQUESTS_CA_BUNDLE=/Users/owen.mcgovern/tk-root-ca_ca.pem

# If you get a warning when running 

    /Users/owen.mcgovern/PycharmProjects/BitBucketAPI/venv/lib/python3.9/site-packages/urllib3/__init__.py:34: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(

Then run
    brew install openssl@1.1

alternatively... downgrade your urllib3 library ie.

    pip uninstall urllib3
    pip install 'urllib3<2.0'



    