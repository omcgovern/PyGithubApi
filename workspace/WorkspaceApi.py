import os

from workspace.ProjectDirectory import ProjectDirectory


class WorkspaceApi:
    def __init__(self, baseDirectory):
        self.baseDirectory = baseDirectory

    def scan(self, skip_projects):
        workspace_metrics = []
        projects = os.scandir(self.baseDirectory)
        for entry in projects:
            if entry.is_dir():
                if entry.name not in skip_projects:
                    print(f"Scanning Project: {entry}")
                    for project_metric in ProjectDirectory(entry).scan():
                        workspace_metrics.append(project_metric)
        return workspace_metrics

    def to_csv(self, skip_projects):

        csv_file = open("repo_metrics.csv", "w")

        workspace_metrics = self.scan(skip_projects)
        first_metric = True

        for workspace_metric in workspace_metrics:
            if first_metric:
                first_metric = False
                first_key = True
                header = ""
                for key in workspace_metric.keys():
                    if first_key:
                        first_key = False
                        header = "\"" + key + "\""
                    else:
                        header = header + ",\"" + key + "\""
                csv_file.write(header + "\n")

            row = ""
            first_value = True
            for value in workspace_metric.values():
                if first_value:
                    first_value = False
                    row = "\"" + str(value) + "\""
                else:
                    row = row + ",\"" + str(value) + "\""
            csv_file.write(row + "\n")

        csv_file.close()



    def build(self, skip_projects):

        repoDirectories = self.scan(skip_projects)
        first_metric = True

        # RepoDirectory
        for repoDirectory in repoDirectories:
            repoDirectory.build()
