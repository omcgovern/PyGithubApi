import os
from pathlib import Path

from workspace.RepoDirectory import RepoDirectory


class ProjectDirectory:
    def __init__(self, projectPath):
        self.projectPath = projectPath

    def scan(self):
        projectMetrics = []

        projects = sorted(os.scandir(self.projectPath), key=lambda e: e.name)
        for entry in projects:
            if entry.is_dir():
                print(f"\tScanning Repo: {entry}")
                projectMetrics.append(RepoDirectory(self.projectPath.name, Path(entry.path)).scan())

        return projectMetrics

