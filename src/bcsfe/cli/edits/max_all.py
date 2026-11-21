from __future__ import annotations

from typing import Any, Callable

from bcsfe import core
from bcsfe.cli import color, dialog_creator


def max_catfood(save_file: core.SaveFile):
    orig = save_file.catfood
    save_file.catfood = core.core_data.max_value_manager.catfood
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.catfood - orig, core.ManagedItemType.CATFOOD
        )
    )


def max_rare_tickets(save_file: core.SaveFile):
    orig = save_file.rare_tickets
    save_file.rare_tickets = core.core_data.max_value_manager.rare_tickets
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.rare_tickets - orig, core.ManagedItemType.RARE_TICKET
        )
    )


def max_plat_tickets(save_file: core.SaveFile):
    orig = save_file.platinum_tickets
    save_file.platinum_tickets = core.core_data.max_value_manager.platinum_tickets
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.platinum_tickets - orig, core.ManagedItemType.PLATINUM_TICKET
        )
    )


def max_plat_shards(save_file: core.SaveFile):
    save_file.platinum_shards = 10 * core.core_data.max_value_manager.platinum_tickets


def max_legend_tickets(save_file: core.SaveFile):
    orig = save_file.legend_tickets
    save_file.legend_tickets = core.core_data.max_value_manager.legend_tickets
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.legend_tickets - orig, core.ManagedItemType.LEGEND_TICKET
        )
    )


def max_xp(save_file: core.SaveFile):
    save_file.xp = core.core_data.max_value_manager.xp


def max_np(save_file: core.SaveFile):
    save_file.np = core.core_data.max_value_manager.np


def max_100_million_ticket(save_file: core.SaveFile):
    save_file.hundred_million_ticket = (
        core.core_data.max_value_manager.hundred_million_tickets
    )


def max_leadership(save_file: core.SaveFile):
    save_file.leadership = core.core_data.max_value_manager.leadership


def max_battle_items(save_file: core.SaveFile):
    for item in save_file.battle_items.items:
        item.amount = core.core_data.max_value_manager.battle_items


def max_catseyes(save_file: core.SaveFile):
    for id in range(len(save_file.catseyes)):
        save_file.catseyes[id] = core.core_data.max_value_manager.catseyes


def max_treasure_chests(save_file: core.SaveFile):
    for id in range(len(save_file.treasure_chests)):
        save_file.treasure_chests[id] = core.core_data.max_value_manager.treasure_chests


def max_catamins(save_file: core.SaveFile):
    for id in range(len(save_file.catamins)):
        save_file.catamins[id] = core.core_data.max_value_manager.catamins


def max_labyrinth_medals(save_file: core.SaveFile):
    for id in range(len(save_file.labyrinth_medals)):
        save_file.labyrinth_medals[id] = (
            core.core_data.max_value_manager.labyrinth_medals
        )


def max_normal_tickets(save_file: core.SaveFile):
    save_file.normal_tickets = core.core_data.max_value_manager.normal_tickets


def max_catfruit(save_file: core.SaveFile):
    if save_file.game_version < 110400:
        return

    max_catfruit = core.core_data.max_value_manager.catfruit_new
    for id in range(len(save_file.catfruit)):
        save_file.catfruit[id] = max_catfruit


def _value_range(values: list[int]) -> str:
    if not values:
        return "0"
    low, high = min(values), max(values)
    if low == high:
        return str(low)
    return f"{low}..{high}"


MAX_ALL_OPTIONS: list[
    tuple[str, Callable[[core.SaveFile], None], Callable[[core.SaveFile], str]]
] = [
    ("catfood", max_catfood, lambda sf: str(sf.catfood)),
    ("xp", max_xp, lambda sf: str(sf.xp)),
    ("normal_tickets", max_normal_tickets, lambda sf: str(sf.normal_tickets)),
    ("rare_tickets", max_rare_tickets, lambda sf: str(sf.rare_tickets)),
    ("platinum_tickets", max_plat_tickets, lambda sf: str(sf.platinum_tickets)),
    ("legend_tickets", max_legend_tickets, lambda sf: str(sf.legend_tickets)),
    ("platinum_shards", max_plat_shards, lambda sf: str(sf.platinum_shards)),
    ("np", max_np, lambda sf: str(sf.np)),
    ("leadership", max_leadership, lambda sf: str(sf.leadership)),
    (
        "battle_items",
        max_battle_items,
        lambda sf: _value_range([item.amount for item in sf.battle_items.items]),
    ),
    ("catfruit", max_catfruit, lambda sf: _value_range(list(sf.catfruit))),
    ("catseyes", max_catseyes, lambda sf: _value_range(list(sf.catseyes))),
    ("catamins", max_catamins, lambda sf: _value_range(list(sf.catamins))),
    (
        "labyrinth_medals",
        max_labyrinth_medals,
        lambda sf: _value_range(list(sf.labyrinth_medals)),
    ),
    (
        "100_million_tickets",
        max_100_million_ticket,
        lambda sf: str(sf.hundred_million_ticket),
    ),
    (
        "treasure_chests",
        max_treasure_chests,
        lambda sf: _value_range(list(sf.treasure_chests)),
    ),
]


def localize_or(key: str, fallback: str, **kwargs: Any) -> str:
    text = core.localize(key, **kwargs)
    if text != key:
        return text
    if kwargs:
        return fallback.format(**kwargs)
    return fallback


def max_all(save_file: core.SaveFile):
    names = [core.localize(key) for key, _, _ in MAX_ALL_OPTIONS]
    selected = dialog_creator.multi_select_indexes_key(
        names, localize_or("max_all_dialog", "Select the items to max out:")
    )
    if not selected:
        return

    before = [MAX_ALL_OPTIONS[id][2](save_file) for id in selected]
    for id in selected:
        MAX_ALL_OPTIONS[id][1](save_file)
    after = [MAX_ALL_OPTIONS[id][2](save_file) for id in selected]

    color.color_print(
        localize_or("max_all_success", "Successfully maxed the selected items")
    )
    color.color_print(localize_or("max_all_summary", "Change summary:"))
    for id, old, new in zip(selected, before, after):
        color.color_print(
            localize_or(
                "max_all_summary_line",
                "  {name}: {before} to {after}",
                name=names[id],
                before=old,
                after=new,
            )
        )
