from __future__ import annotations
import json
from bcsfe import core


class MaxValueHelper:
    def __init__(
        self,
        catfood: int,
        xp: int,
        normal_tickets: int,
        hundred_million_tickets: int,
        rare_tickets: int,
        platinum_tickets: int,
        legend_tickets: int,
        np: int,
        leadership: int,
        battle_items: int,
        catamins: int,
        catseyes: int,
        catfruit_old: int,
        catfruit_new: int,
        base_materials: int,
        labyrinth_medals: int,
        talent_orbs: int,
        treasure_level: int,
        stage_clear_count: int,
        itf_timed_score: int,
        event_tickets: int,
        treasure_chests: int,
    ):

        self.catfood = catfood
        self.xp = xp
        self.normal_tickets = normal_tickets
        self.hundred_million_tickets = hundred_million_tickets
        self.rare_tickets = rare_tickets
        self.platinum_tickets = platinum_tickets
        self.legend_tickets = legend_tickets
        self.np = np
        self.leadership = leadership
        self.battle_items = battle_items
        self.catamins = catamins
        self.catseyes = catseyes
        self.catfruit_old = catfruit_old
        self.catfruit_new = catfruit_new
        self.base_materials = base_materials
        self.labyrinth_medals = labyrinth_medals
        self.talent_orbs = talent_orbs
        self.treasure_level = treasure_level
        self.stage_clear_count = stage_clear_count
        self.itf_timed_score = itf_timed_score
        self.event_tickets = event_tickets
        self.treasure_chests = treasure_chests

    @staticmethod
    def default() -> MaxValueHelper:
        return MaxValueHelper.from_dict({})

    def as_dict(self) -> dict[str, int]:
        return {
            "catfood": self.catfood,
            "xp": self.xp,
            "normal_tickets": self.normal_tickets,
            "hundred_million_tickets": self.hundred_million_tickets,
            "rare_tickets": self.rare_tickets,
            "platinum_tickets": self.platinum_tickets,
            "legend_tickets": self.legend_tickets,
            "np": self.np,
            "leadership": self.leadership,
            "battle_items": self.battle_items,
            "catamins": self.catamins,
            "catseyes": self.catseyes,
            "catfruit_old": self.catfruit_old,
            "catfruit_new": self.catfruit_new,
            "base_materials": self.base_materials,
            "labyrinth_medals": self.labyrinth_medals,
            "talent_orbs": self.talent_orbs,
            "treasure_level": self.treasure_level,
            "stage_clear_count": self.stage_clear_count,
            "itf_timed_score": self.itf_timed_score,
            "event_tickets": self.event_tickets,
            "treasure_chests": self.treasure_chests,
        }

    @staticmethod
    def from_dict(data: dict[str, int]) -> MaxValueHelper:
        def get_val(key: str, default: int) -> int:
            val = data.get(key, default)
            if key in ("catfood", "xp") and val < 99999000:
                return 99999000
            if val < 200:
                return 200
            return val

        return MaxValueHelper(
            catfood=get_val("catfood", 99999000),
            xp=get_val("xp", 99999000),
            normal_tickets=get_val("normal_tickets", 2999),
            hundred_million_tickets=get_val("hundred_million_tickets", 9999),
            rare_tickets=get_val("rare_tickets", 299),
            platinum_tickets=get_val("platinum_tickets", 200),
            legend_tickets=get_val("legend_tickets", 200),
            np=get_val("np", 9999),
            leadership=get_val("leadership", 9999),
            battle_items=get_val("battle_items", 9999),
            catamins=get_val("catamins", 9999),
            catseyes=get_val("catseyes", 9999),
            catfruit_old=get_val("catfruit_old", 200),
            catfruit_new=get_val("catfruit_new", 998),
            base_materials=get_val("base_materials", 9999),
            labyrinth_medals=get_val("labyrinth_medals", 9999),
            talent_orbs=get_val("talent_orbs", 998),
            treasure_level=get_val("treasure_level", 9999),
            stage_clear_count=get_val("stage_clear_count", 9999),
            itf_timed_score=get_val("itf_timed_score", 9999),
            event_tickets=get_val("event_tickets", 9999),
            treasure_chests=get_val("treasure_chests", 9999),
        )

    @staticmethod
    def path() -> core.Path:
        return core.Path.get_config_folder().add("max_values.json")

    @staticmethod
    def from_file() -> MaxValueHelper:
        file_path = MaxValueHelper.path()
        if not file_path.exists():
            item = MaxValueHelper.default()
            item.save()
            return item
        try:
            item = MaxValueHelper.from_dict(
                core.JsonFile.from_data(file_path.read()).as_object()
            )
            item.save()
            return item
        except json.JSONDecodeError:
            item = MaxValueHelper.default()
            item.save()
            return item

    def save(self):
        path = MaxValueHelper.path()

        core.JsonFile.from_object(self.as_dict()).to_file(path)
