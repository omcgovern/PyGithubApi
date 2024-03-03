import os
import sys
from pathlib import Path

from githelpers.GithubApi import GithubApi
from utils.PropertyFile import PropertyFile


class Main:

    def __init__(self, commands):
        self.commands = commands

        userhome = Path.home()
        config_file = os.path.join(userhome, "GitRepos.properties")
        if os.path.exists(config_file):
            print(f"Found Config File : {config_file}")
            properties = PropertyFile(config_file).get_properties()
            self.githubApi = GithubApi(properties, "github")
            self.configured = True
        else:
            f = open(config_file, "w")
            f.write("# Github settings\n\n")
            f.write("github.organisation=Teckro-Production\n")
            f.write("github.custom_hostname=\n")
            f.write("github.access_token=<github access token>\n")
            f.write("github.repoDir=" + os.path.join(userhome, "repositories", "github") + "\n")
            f.write("github.includeProjects=\n")
            f.write("github.excludeProjects=\n")
            f.write("github.includeRepos=\n")
            f.write("github.excludeRepos=\n\n")

            f.write("# General settings\n\n")
            f.write("general.throttleSleepSecs=0\n")

            f.close()
            print(f"ERROR: No configuration found, please configure file : {config_file}")
            self.configured = False

    def run(self):

        git_impl = self.githubApi           # Run against Github only
        git_impl.info()

        if self.commands is not None and len(self.commands) > 0:
            for command in self.commands:
                if command == 'clone':
                    print("Cloning...")
                    git_impl.clone()
                elif command == 'update':
                    print("Updating...")
                    git_impl.pull_or_clone()
                elif command == 'fupdate':
                    print("Updating...")
                    git_impl.fetch_or_clone()
                elif command == 'list':
                    print("Listing...")
                    git_impl.list()
                elif command == 'analyse':
                    print("Analysing...")
                    git_impl.analyse()
                elif command == 'build':
                    print("Building...")
                    git_impl.build()
                elif command == 'listWorkflowRuns':
                    print("List Builds...")
                    git_impl.scanrepo("be-multimedia-service")
                else:
                    print("Unknown command \"{command}\"")
        else:
            print("Usage: main.py <clone|update|analyse>")


if __name__ == '__main__':
    instance = Main(sys.argv[1:])
    if instance.configured:
        instance.run()
