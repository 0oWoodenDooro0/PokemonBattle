import util


class Generation:
    def __init__(self, generation_id: int):
        self.id: int = generation_id
        self.generation_data: dict = util.fetch_json('generation', str(self.id))
        self.moves: list[int] = self.get_moves()
        self.pokemon_species: list[int] = self.get_pokemon_species()
        self.version_groups: list[int] = self.get_version_groups()

    def get_moves(self) -> list:
        return [util.url_to_id(data['url'], 'move') for data in self.generation_data['moves']]

    def get_pokemon_species(self) -> list:
        return [util.url_to_id(data['url'], 'pokemon-species') for data in self.generation_data['pokemon_species']]

    def get_version_groups(self) -> list:
        return [util.url_to_id(data['url'], 'version-group') for data in self.generation_data['version_groups']]
