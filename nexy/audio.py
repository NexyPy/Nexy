class Audio:
    def __call__(self, *args: object, **kwargs: object) -> None:
        print("Audio called with args:", args, "and kwargs:", kwargs)