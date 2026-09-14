class DomainError(Exception):
    pass


class PostNotFoundError(DomainError):
    def __init__(self, post_id: int) -> None:
        super().__init__(f"post {post_id} not found")
        self.post_id = post_id
