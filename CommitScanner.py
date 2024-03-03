import sys

from githelpers.GitRepo import GitRepo


class CommitScanner:

    def run(self):
        gitrepo = GitRepo("/Users/owen.mcgovern/Repositories/Github/Teckro", "be-site-activation-service")
        repo = gitrepo.getrepo()

        fifty_first_commits = list(repo.iter_commits("main", max_count=50))
        for commit in fifty_first_commits:
            commitOneLine = commit.message.replace('\n', ' ').replace('\r', ' ')
            print(f"{commit.hexsha}, {commit.author.name}, {commitOneLine}")

        # headcommit = repo.head.commit
        # assert len(headcommit.hexsha) == 40
        # assert len(headcommit.parents) > 0
        # assert headcommit.tree.type == "tree"
        # assert len(headcommit.author.name) != 0
        # assert isinstance(headcommit.authored_date, int)
        # assert len(headcommit.committer.name) != 0
        # assert isinstance(headcommit.committed_date, int)
        # assert headcommit.message != ""


        # heads = repo.heads
        # main = heads.main
        # mainreflog = main.log()
        # for reflog in mainreflog:
        #     print(reflog)


if __name__ == '__main__':
    instance = CommitScanner()
    instance.run()
