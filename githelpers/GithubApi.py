from github.Branch import Branch

from githelpers.AbstractGitRepo import AbstractGitRepo
from githelpers.GitRepo import GitRepo
from github import Auth
from github import Github


class GithubApi(AbstractGitRepo):
    def __init__(self, properties, property_prefix="github"):
        super().__init__(properties, property_prefix)
        self.access_token = properties[f"{property_prefix}.access_token"]
        self.custom_hostname = properties[f"{property_prefix}.custom_hostname"]
        self.organization = properties[f"{property_prefix}.organization"]

        self.auth = Auth.Token(self.access_token)
        if self.custom_hostname is None or len(self.custom_hostname) == 0:
            # Public Web Github
            self.githubApi = Github(auth=self.auth)
        else:
            # Github Enterprise with custom hostname
            self.githubApi = Github(auth=self.auth, base_url="https://{custom_hostname}/api/v3")

        # self.fieldList = 'next,values.slug,values.created_on,values.updated_on,values.description,values.links,' \
        #                  'values.project'
        # self.next_page_url = 'https://api.github.org/2.0/repositories/%s?pagelen=100&fields=%s' % (
        #     self.team, self.fieldList)
        #     print(repo.name)
        #     print(dir(repo))

    def info(self):
        print(f"Github user : {self.githubApi.get_user().name}")

    def scan(self):
        teckroOrg = self.githubApi.get_organization(self.organization)
        for repo in teckroOrg.get_repos():
            print(f"Reading {repo.name}")

            if repo.description is not None:
                description = repo.description.replace('\n', ' ').replace('\r', ' ')
            else:
                description = ""

            if repo.organization is not None and repo.organization.name is not None:
                orgname = repo.organization.name
            else:
                orgname = "Default"

            self.full_repo_list.append(
                GitRepo(base_directory=self.repo_base_directory,
                        name=repo.name,
                        project=orgname,
                        # clone_url=repo.clone_url,   # The https URL for cloning
                        clone_url=repo.ssh_url,  # The git ssh URL for cloning
                        description=description,
                        created_on=repo.created_at,
                        updated_on=repo.updated_at)
            )
            # to see all the available attributes and methods
            # print(dir(repo))

    def scanrepo(self, repoName):

        teckroOrg = self.githubApi.get_organization(self.organization)
        repo = teckroOrg.get_repo(repoName)
        print(f"Found Repo:  {repo.name}")

        main_branch = repo.get_branch("main")

        runs = repo.get_workflow_runs(branch=main_branch, event="push")
        for run in runs:
            status = run.conclusion
            commit = run.head_commit
            commiter = commit.author.name
            # commiter = commit.committer.name
            message = commit.message.replace('\n', ' ').replace('\r', '')

            print(f" - {status} {run.name}, {run.run_number}, {run.run_started_at}, {commiter}, {message}")
            # print(f" - {run.name}, {run.run_number}, {run.run_started_at}, {commiter}")

