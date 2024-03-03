import os
import time
from git import Repo, RemoteProgress, InvalidGitRepositoryError


# Python Git Library docs : https://gitpython.readthedocs.io/en/stable/tutorial.html

class GitRepo:
    def __init__(self, base_directory, name, project=None, clone_url=None, description=None, created_on=None,
                 updated_on=None):
        self.name = name
        self.project = project
        self.description = description
        self.clone_url = clone_url
        self.created_on = created_on
        self.updated_on = updated_on
        self.base_directory = base_directory
        self.project_dir = None
        self.repo_dir = self.get_repo_directory(base_directory)

        if self.project_dir is not None and not os.path.exists(self.project_dir):
            os.mkdir(self.project_dir)

        if os.path.exists(self.repo_dir):
            try:
                self.repo = Repo(self.repo_dir)
            except InvalidGitRepositoryError as N:
                print(f"WARN: Cannot open git repository {self.repo_dir}")
                self.repo = None
        else:
            self.repo = None

    def exists(self):
        return os.path.exists(self.repo_dir)

    def is_not_empty(self):
        return any(os.scandir(self.repo_dir))

    def remotes(self):
        return self.repo.remotes

    def get_repo_directory(self, base_directory):
        if self.project is not None:
            self.project_dir = os.path.join(base_directory, self.project.replace(' ', '_'))
            repo_dir = os.path.join(self.project_dir, self.name.replace(' ', '_'))
        else:
            repo_dir = os.path.join(base_directory, self.name.replace(' ', '_'))
        return repo_dir

    def master(self):
        self.repo.master()

    def list(self):
        print(f"{self.project},{self.name},{self.clone_url},{self.created_on},{self.updated_on},\"{self.description}\"")

    def clone(self):
        if self.clone_url is None:
            raise Exception("No clone url for repo ${self.name}")

        if not os.path.exists(self.repo_dir):
            os.mkdir(self.repo_dir)
            print(f"Git clone {self.clone_url} to ${self.repo_dir}")
            try:
                self.repo = Repo.clone_from(self.clone_url, self.repo_dir)  # s, progress=CloneProgress())
            except Exception as e:
                try:
                    print(f"\tCloning Retry 1 - {self.project}, {self.name} - {e}")
                    time.sleep(10)
                    self.repo = Repo.clone_from(self.clone_url, self.repo_dir)  # s, progress=CloneProgress())
                except Exception as e:
                    try:
                        print(f"\tCloning Retry 2 - {self.project}, {self.name} - {e}")
                        time.sleep(20)
                        self.repo = Repo.clone_from(self.clone_url, self.repo_dir)  # s, progress=CloneProgress())
                    except Exception as e:
                        try:
                            print(f"\tCloning Retry 3 - {self.project}, {self.name}- {e}")
                            time.sleep(30)
                            self.repo = Repo.clone_from(self.clone_url, self.repo_dir)  # s, progress=CloneProgress())
                        except Exception as e:
                            print(f"ERROR: Cloning {self.project}, {self.name} - {e}")

    def read(self):
        if self.repo is None:
            if not os.path.exists(self.repo_dir):
                print(f"WARN: Repo ${self.name} not found in ${self.repo_dir}")
            else:
                print(f"WARN: Repo ${self.name} not initialised")
            return

        if self.repo.bare:
            print(f"WARN: Repo {self.name} is bare")
        else:
            print(f"INFO: Repo {self.name} is not bare")

        if self.repo.is_dirty():
            print(f"WARN: Repo {self.name} is dirty")
        else:
            print(f"INFO: Repo {self.name} is not dirty")

        print(f"Repo {self.name} is on branch {self.repo.heads[0].name}, remote is {self.repo.remotes.origin}")

        for url in self.repo.remotes.origin.urls:
            print(f"\tURL : {url}")

    def pull_or_clone(self):
        if not os.path.exists(self.repo_dir) or len(os.listdir(self.repo_dir)) == 0:
            self.clone()
        else:
            self.pull()

    def fetch_or_clone(self):
        if not os.path.exists(self.repo_dir) or len(os.listdir(self.repo_dir)) == 0:
            self.clone()
        else:
            self.pull()

    def pull(self):
        if self.repo is not None and self.repo.remotes is not None and self.repo.remotes.origin is not None:
            print(f"Updating {self.project}, {self.name}")
            try:
                self.repo.remotes.origin.pull()
                return 1
            except Exception as e:
                try:
                    print(f"\tUpdating Retry 1 - {self.project}, {self.name} - {e}")
                    time.sleep(10)
                    self.repo.remotes.origin.pull()
                    return 1
                except Exception as e:
                    try:
                        print(f"\tUpdating Retry 2 - {self.project}, {self.name} - {e}")
                        time.sleep(20)
                        self.repo.remotes.origin.pull()
                        return 1
                    except Exception as e:
                        try:
                            print(f"\tUpdating Retry 3 - {self.project}, {self.name} - {e}")
                            time.sleep(30)
                            self.repo.remotes.origin.pull()
                            return 1
                        except Exception as e:
                            print(f"ERROR: Updating {self.project}, {self.name} - {e}")
                            return -1
        else:
            print(f"Skipping {self.project}, {self.name}")
            return 0

    def fetch(self):
        if self.repo is not None and self.repo.remotes is not None and self.repo.remotes.origin is not None:
            print(f"Fetching {self.project}, {self.name}")
            try:
                self.repo.remotes.origin.fetch()
                return 1
            except Exception as e:
                try:
                    print(f"\tFetching Retry 1 - {self.project}, {self.name} - {e}")
                    time.sleep(10)
                    self.repo.remotes.origin.fetch()
                    return 1
                except Exception as e:
                    try:
                        print(f"\tFetching Retry 2 - {self.project}, {self.name} - {e}")
                        time.sleep(20)
                        self.repo.remotes.origin.fetch()
                        return 1
                    except Exception as e:
                        try:
                            print(f"\tFetching Retry 3 - {self.project}, {self.name} - {e}")
                            time.sleep(30)
                            self.repo.remotes.origin.fetch()
                            return 1
                        except Exception as e:
                            print(f"ERROR: Fetching {self.project}, {self.name} - {e}")
                            return -1
        else:
            print(f"Skipping {self.project}, {self.name}")
            return 0

    def archive(self, target_directory):
        with open(os.path.join(target_directory, f"{self.name.replace(' ', '_')}.tar"), "wb") as fp:
            self.repo.archive(fp)

    def getrepo(self):
        return self.repo


class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message='NO MESSAGE'):
        if message:
            print(
                op_code,
                cur_count,
                max_count,
                cur_count / (max_count or 100.0),
                message,
            )
