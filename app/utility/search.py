class Search:

    @staticmethod
    def get_search_name(name: str) -> str:
        return (
            name
            .lower()
            .replace(' ', '')
            .replace('-', '')
            .replace('(', '')
            .replace(')', '')
        )
