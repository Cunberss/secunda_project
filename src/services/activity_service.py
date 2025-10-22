from src.repositories.activity_repo import ActivityRepository


class ActivityService:
    def __init__(self, repo: ActivityRepository):
        self.repo = repo
