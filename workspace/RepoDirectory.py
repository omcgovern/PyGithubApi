import os
import re
from enum import Enum
from githelpers.GitRepo import GitRepo


class BuildSystem(Enum):
    GRADLE_KOTLIN = "build.gradle.kts"
    GRADLE_JAVA = "build.gradle"
    MAVEN = "pom.xml"
    WEB = "package.json"
    PYTHON = "requirements.txt"
    UNKNOWN = "Unknown"


PLATFORM_SDK = "com.teckro.platform.sdk"
MAVEN_PUBLISH = "maven-publish"
MAVEN_PUBLISH_SNAPSHOT = "snapshot"
REGEX_DOCKER_FROM_IMAGE = r'^FROM\s(.*)$'

JAVA_VERSION_GRADLE_REGEX = r'^.*JavaVersion\.VERSION_(.*)$'

JAVA_VERSION_MAVEN_REGEX = r'<java.version>(.*)</java.version>'
JAVA_MAJOR_VERSION_MAVEN_REGEX = r'<java.major.version>(.*)</java.major.version>'

KOTLIN_TOOLCHAIN_VERSION_REGEX = r'jvmToolchain\((.*)\)'
KOTLIN_JVM_TARGET_REGEX = r'kotlinOptions.jvmTarget\s*=\s*"(.*)"'
KOTLIN_JVM_COMPATIBILITY_REGEX = r'this.targetCompatibility\s*=\s*"(.*)"'

GRADLE_VERSION_GRADLE_REGEX = r'gradle-(.*)-bin.zip'
KAFKA_REGEX = "kafka"


class RepoDirectory:
    def __init__(self, project_name, repo_path):
        self.project_name = project_name
        self.repo_path = repo_path
        self.repo_api = GitRepo(repo_path.parent, repo_path.name)
        self.metrics = {}

    def scan(self):
        # print(f"\t\tRepository : {self.repoPath.name}")
        gradle_ver = None
        java_ver = None
        kafka = None

        self.metrics["Project"] = self.project_name
        self.metrics["Repository"] = self.repo_path.name

        if self.repo_api.repo is not None and self.repo_api.repo.remotes is not None and \
                self.repo_api.repo.remotes.origin is not None and self.repo_api.repo.remotes.origin.urls is not None:
            urls = self.repo_api.repo.remotes.origin.urls
            self.metrics["CloneURL"] = next(urls)
        else:
            self.metrics["CloneURL"] = ""

        self.metrics["Dockerfile"] = self.has_file("Dockerfile")

        if self.metrics["Dockerfile"]:
            self.metrics["Dockerfile_BaseImage"] = self.search_files_regex("Dockerfile", REGEX_DOCKER_FROM_IMAGE)
        else:
            self.metrics["Dockerfile_BaseImage"] = None
        self.metrics["README.md"] = self.has_file("README.md")

        build_system = self.get_build_system()
        self.metrics["BuildSystem"] = self.get_build_system().name

        if build_system is not None:
            if build_system == BuildSystem.GRADLE_KOTLIN:
                java_ver = self.search_files_regex(BuildSystem.GRADLE_KOTLIN.value, JAVA_VERSION_GRADLE_REGEX)
                if java_ver is None:
                    java_ver = self.search_files_regex(BuildSystem.GRADLE_KOTLIN.value, KOTLIN_TOOLCHAIN_VERSION_REGEX)
                if java_ver is None:
                    java_ver = self.search_files_regex(BuildSystem.GRADLE_KOTLIN.value, KOTLIN_JVM_TARGET_REGEX)
                if java_ver is None:
                    java_ver = self.search_files_regex(BuildSystem.GRADLE_KOTLIN.value, KOTLIN_JVM_COMPATIBILITY_REGEX)
                gradle_ver = self.search_files_regex("gradle-wrapper.properties", GRADLE_VERSION_GRADLE_REGEX)
                kafka = self.search_files_regex(BuildSystem.GRADLE_KOTLIN.value, KAFKA_REGEX)
            elif build_system == BuildSystem.GRADLE_JAVA:
                java_ver = self.search_files_regex(BuildSystem.GRADLE_JAVA.value, JAVA_VERSION_GRADLE_REGEX)
                gradle_ver = self.search_files_regex("gradle-wrapper.properties", GRADLE_VERSION_GRADLE_REGEX)
                kafka = self.search_files_regex(BuildSystem.GRADLE_JAVA.value, KAFKA_REGEX)
            elif build_system == BuildSystem.MAVEN:
                java_ver = self.search_files_regex(BuildSystem.MAVEN.value, JAVA_VERSION_MAVEN_REGEX)
                if java_ver is None:
                    java_ver = self.search_files_regex(BuildSystem.MAVEN.value, JAVA_MAJOR_VERSION_MAVEN_REGEX)
                gradle_ver = ""
                kafka = self.search_files_regex(BuildSystem.MAVEN.value, KAFKA_REGEX)
            else:
                java_ver = None
                gradle_ver = ""
                kafka = ""

        if gradle_ver is None:
            gradle_ver = ""
        self.metrics["gradleVersion"] = gradle_ver

        if java_ver is None:
            java_ver = ""
        self.metrics["JavaVersion"] = java_ver.replace('_', '.')

        if kafka is not None and len(kafka) > 0:
            self.metrics["Kafka"] = True
        else:
            self.metrics["Kafka"] = False

        self.metrics["MavenPublish"] = self.search_files_string(self.get_build_system().value, MAVEN_PUBLISH)
        self.metrics["MavenPublishSnapshot"] = self.search_files_string(self.get_build_system().value,
                                                                        MAVEN_PUBLISH_SNAPSHOT)
        self.metrics["PlatformSDK"] = self.search_files_string(self.get_build_system().value, PLATFORM_SDK)
        self.metrics["hasLogbackFile"] = self.has_file("logback.xml")
        self.metrics["hasLogbackJacksonJsonLogger"] = self.findFilesRegExHasRegEx(".*logback.*\\.xml", "net.logstash.logback.encoder.LogstashEncoder")

        # "org.springframework.boot:spring-boot-dependencies:$springBootVersion"

        return self.metrics


    def build(self):
        buildSystem = self.metrics["BuildSystem"]

        if buildSystem == BuildSystem.MAVEN:
            print("Building Maven...")
        elif buildSystem == BuildSystem.GRADLE_JAVA or buildSystem == BuildSystem.GRADLE_KOTLIN:
            print("Building Gradle...")
        else:
            print("Skipping build...")


    def get_metrics(self):
        return self.metrics

    def to_csv(self):
        csv_row = ''
        first = True
        for key in self.metrics:
            value = self.metrics[key]
            if first:
                first = False
            else:
                csv_row = csv_row + ','

            if value is not None:
                csv_row = csv_row + ''.join([key, "=\"", str(value), "\""])
            else:
                csv_row = csv_row + ''.join([key, "=\"\""])

        return csv_row

    def get_build_system(self):
        for buildSystem in BuildSystem:
            if self.has_file(buildSystem.value):
                return buildSystem

        return BuildSystem.UNKNOWN

    def find_build_files(self):
        for buildSystem in BuildSystem:
            build_files = self.find_files(buildSystem.value)
            if len(build_files) > 0:
                return buildSystem.name + f"({len(build_files)}"
        return BuildSystem.UNKNOWN.name

    def findFilesRegEx(self, filenameRegEx):
        results = []
        for root, dirs, files in os.walk(self.repo_path):
            for somefile in files:
                if re.match(filenameRegEx, somefile):
                    results.append(os.path.join(root, somefile))
        return results

    def findFilesRegExHasRegEx(self, filenameRegEx, stringRegEx):
        for root, dirs, files in os.walk(self.repo_path):
            for somefile in files:
                if re.match(filenameRegEx, somefile):
                    if self.search_for_regex_within_file(os.path.join(root, somefile), stringRegEx):
                        return True
        return False

    def has_file(self, filename):
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file == filename:
                    return True
        return False

    @staticmethod
    def search_file_string(file, find_str):
        with open(file, "r") as fp:
            lines = fp.readlines()
            line_num = 0
            for row in lines:
                line_num = line_num + 1
                if row.find(find_str) != -1:
                    return line_num
        return -1

    def search_files_string(self, filename, find_str):
        for f in self.find_files(filename):
            if self.search_file_string(f, find_str) > -1:
                return True
        return False

    @staticmethod
    def search_for_regex_within_file(file, regex):
        with open(file, "r") as fp:
            lines = fp.readlines()
            for row in lines:
                groups = re.findall(regex, row)
                if len(groups) > 0:
                    return groups[0]
        return None

    @staticmethod
    def search_file_regex_multiple_results(file, regex):
        results = []

        with open(file, "r") as fp:
            lines = fp.readlines()
            for row in lines:
                groups = re.findall(regex, row)
                if len(groups) > 0:
                    results.append(groups)

        return results

    def search_files_regex(self, filename, regex):
        for f in self.find_files(filename):
            result = self.search_for_regex_within_file(f, regex)
            if result is not None:
                return result
        return None

    def find_files(self, filename):
        file_list = []
        for root, dirs, filelist in os.walk(self.repo_path):
            for some_file in filelist:
                if some_file == filename:
                    found_dir = os.path.join(root, some_file)
                    file_list.append(found_dir)
        return file_list
