from abc import abstractmethod
import os
from workspace.WorkspaceApi import WorkspaceApi


class AbstractGitRepo:
    def __init__(self, properties, property_prefix):
        self.repo_base_directory = properties[f"{property_prefix}.repoDir"]
        if not os.path.exists(self.repo_base_directory):
            os.makedirs(self.repo_base_directory, exist_ok=True)

        if properties.get(f"{property_prefix}.excludeProjects") is not None:
            self.exclude_projects = properties[f"{property_prefix}.excludeProjects"].split(",")
        else:
            self.exclude_projects = []

        if properties.get(f"{property_prefix}.includeProjects") is not None:
            self.include_projects = properties[f"{property_prefix}.includeProjects"].split(",")
        else:
            self.include_projects = []

        if properties.get(f"{property_prefix}.includeRepos") is not None:
            self.include_repos = properties[f"{property_prefix}.includeRepos"].split(",")
        else:
            self.include_repos = []

        if properties.get(f"{property_prefix}.excludeRepos") is not None:
            self.exclude_repos = properties[f"{property_prefix}.excludeRepos"].split(",")
        else:
            self.exclude_repos = []





        self.full_repo_list = []

    def get_repos(self):
        return self.full_repo_list

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def scan(self):
        pass

    # def filterRepos(self, repo):
    #     if self.include_projects is not None and repo.project in self.include_repos:

    # calc = lambda num: "Even number" if num % 2 == 0 else "Odd number"

    def filterRepos(self, repos):
        filtered = filter(lambda repo: repo >= 70, repos)


    def clone(self):
        self.scan()
        repo_instances = self.get_repos()

        print("project,name,clone_url,created_on,updated_on,description")
        for repo_instance in repo_instances:
            if repo_instance.project is not None and repo_instance.project not in self.exclude_projects:
                if repo_instance.name not in self.exclude_repos:
                    repo_instance.clone(self.repo_base_directory)
                else:
                    print(f"excluding repo: {repo_instance.name}")
            else:
                print(f"excluding project: {repo_instance.project}")

    def pull(self):
        self.scan()
        repo_instances = self.get_repos()

        for repo_instance in repo_instances:
            print(f"Updating {repo_instance.name}")
            if repo_instance.name not in self.exclude_repos:
                if repo_instance.project is not None and repo_instance.project not in self.exclude_projects:
                    if repo_instance.name not in self.exclude_repos:
                        repo_instance.pull()
                    else:
                        print(f"excluding repo: {repo_instance.name}")
                else:
                    print(f"excluding project: {repo_instance.project}")

    def pull_or_clone(self):
        self.scan()
        repo_instances = self.get_repos()

        for repo_instance in repo_instances:
            if repo_instance.name not in self.exclude_repos:
                if repo_instance.project is not None and repo_instance.project not in self.exclude_projects:
                    if repo_instance.name not in self.exclude_repos:
                        if repo_instance.exists() and repo_instance.is_not_empty():
                            repo_instance.pull()
                        else:
                            repo_instance.clone()
                    else:
                        print(f"excluding repo: {repo_instance.name}")
                else:
                    print(f"excluding project: {repo_instance.project}")

    def fetch_or_clone(self):
        self.scan()
        repo_instances = self.get_repos()

        for repo_instance in repo_instances:
            if repo_instance.name not in self.exclude_repos:
                if repo_instance.project is not None and repo_instance.project not in self.exclude_projects:
                    if repo_instance.name not in self.exclude_repos:
                        if repo_instance.exists() and repo_instance.is_not_empty():
                            repo_instance.fetch()
                        else:
                            repo_instance.clone()
                    else:
                        print(f"excluding repo: {repo_instance.name}")
                else:
                    print(f"excluding project: {repo_instance.project}")

    def analyse(self):
        workspace_api = WorkspaceApi(self.repo_base_directory)
        workspace_api.to_csv(self.exclude_projects)

    def build(self):
        workspace_api = WorkspaceApi(self.repo_base_directory)
        workspace_api.build(self.exclude_projects)

    def list(self):
        self.scan()
        repo_instances = self.get_repos()

        for repo_instance in repo_instances:
            print(f"Repo : {repo_instance.project}, {repo_instance.name}, {repo_instance.clone_url}")
