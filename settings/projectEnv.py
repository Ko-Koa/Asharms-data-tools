import os


class ProjectEnv:
    projectPath = os.path.dirname(os.path.dirname(__file__))
    cachePath = os.path.join(projectPath, ".cache")
    outPath = os.path.join(projectPath, "dist")
