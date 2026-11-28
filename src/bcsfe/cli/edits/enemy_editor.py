from __future__ import annotations
import os
import re
from typing import Optional
from bcsfe import core
from bcsfe.cli import color, dialog_creator
from bcsfe.cli.edits.cat_editor import SelectMode


class EnemyEditor:
    def __init__(self, save_file: core.SaveFile) -> None:
        self.save_file = save_file

    def unlock_enemy_guide(self, enemies: list[core.Enemy]):
        for enemy in enemies:
            enemy.unlock_enemy_guide(self.save_file)

        color.color_print_key("unlock_enemy_guide_success")

    def remove_enemy_guide(self, enemies: list[core.Enemy]):
        for enemy in enemies:
            enemy.reset_enemy_guide(self.save_file)

        color.color_print_key("remove_enemy_guide_success")

    def print_selected_enemies(self, enemies: list[core.Enemy]):
        if not enemies:
            return
        if len(enemies) > 50:
            color.color_print_key("total_selected_enemies", total=len(enemies))
        else:
            for enemy in enemies:
                color.color_print_key(
                    "selected_enemy",
                    id=enemy.id,
                    name=enemy.get_name(self.save_file),
                )

    def select(self, current_enemies: list[core.Enemy] | None):
        if current_enemies is None:
            current_enemies = []
        self.print_selected_enemies(current_enemies)

        new_enemies = dialog_creator.single_select_key(
            dialog_creator.Actions[Optional[list[core.Enemy]]]
            .new()
            .add_new_key("select_enemies_valid", lambda _: self.get_all_valid_enemies())
            .add_new_key("select_enemies_all", lambda _: self.get_all_enemies())
            .add_new_key("select_enemies_id", lambda _: self.select_id())
            .add_new_key("select_enemies_name", lambda _: self.select_name())
            .add_new_key("select_enemies_map", lambda _: self.select_map())
            .add_new_key(
                "select_enemies_invalid", lambda _: self.get_all_invalid_enemies()
            ),
            "select_enemies",
        )
        if new_enemies is None:
            return None

        if current_enemies:
            mode_id = dialog_creator.int_input_key(
                "and_mode_q", dialog_creator.MaxValue.always_cap(3)
            )
            if mode_id is None:
                mode = SelectMode.OR
            elif mode_id == 1:
                mode = SelectMode.AND
            elif mode_id == 2:
                mode = SelectMode.OR
            elif mode_id == 3:
                mode = SelectMode.REPLACE
            else:
                mode = SelectMode.OR
        else:
            mode = SelectMode.OR

        if mode == SelectMode.AND:
            return [enemy for enemy in new_enemies if enemy in current_enemies]
        if mode == SelectMode.OR:
            return list(set(current_enemies + new_enemies))
        if mode == SelectMode.REPLACE:
            return new_enemies
        return new_enemies

    def get_all_enemies(self) -> list[core.Enemy]:
        enemies: list[core.Enemy] = []
        for i in range(len(self.save_file.enemy_guide)):
            enemies.append(core.Enemy(i))
        return enemies

    def get_all_valid_enemies(self) -> list[core.Enemy] | None:
        valid_ids = core.EnemyDictionary(self.save_file).get_valid_enemies()
        if valid_ids is None:
            return None

        return [core.Enemy(id) for id in valid_ids]

    def get_all_invalid_enemies(self) -> list[core.Enemy] | None:
        invalid_ids = core.EnemyDictionary(self.save_file).get_invalid_enemies(
            len(self.save_file.enemy_guide)
        )
        if invalid_ids is None:
            return None

        return [core.Enemy(id) for id in invalid_ids]

    def select_id(self) -> list[core.Enemy] | None:
        enemy_ids = dialog_creator.range_multi_input_key(
            "enter_enemy_ids",
            dialog_creator.MaxValue.always_cap(len(self.save_file.enemy_guide) - 1),
        )
        if enemy_ids is None:
            return None
        enemy_ids = [enemy_id - 2 for enemy_id in enemy_ids]
        return self.get_enemies_by_id(enemy_ids)

    def get_enemies_by_id(self, ids: list[int]) -> list[core.Enemy]:
        enemies: list[core.Enemy] = []
        for enemy in self.get_all_enemies():
            if enemy.id in ids:
                enemies.append(enemy)
        return enemies

    def select_name(self) -> list[core.Enemy] | None:
        usr_name = dialog_creator.str_input_key("enter_enemy_name")
        if usr_name is None:
            return None
        enemies = self.get_enemies_by_name(usr_name)
        if not enemies:
            color.color_print_key("enemy_not_found_name", name=usr_name)
            return None

        enemy_names = [enemy.get_name(self.save_file) for enemy in enemies]
        new_enemy_names: list[str] = []
        for enemy_name in enemy_names:
            if enemy_name is None:
                return None

            new_enemy_names.append(enemy_name)

        enemy_option_ids = dialog_creator.multi_select_indexes_key(
            new_enemy_names, dialog="select_enemies"
        )
        if enemy_option_ids is None:
            return None
        enemies_selected: list[core.Enemy] = []
        for enemy_option_id in enemy_option_ids:
            enemies_selected.append(enemies[enemy_option_id])
        return enemies_selected

    def get_enemies_by_name(self, name: str) -> list[core.Enemy]:
        enemies: list[core.Enemy] = []
        for enemy in self.get_all_enemies():
            enemy_name = enemy.get_name(self.save_file)
            if enemy_name is None:
                continue
            if name.lower() in enemy_name.lower():
                enemies.append(enemy)
        return enemies

    def select_map(self) -> list[core.Enemy] | None:
        locations = self.get_enemy_locations()
        if not locations:
            color.color_print_key("enemy_locations_not_found")
            return None

        labels = [label for label, _ in locations]
        selected = dialog_creator.multi_select_indexes_key(labels, dialog="select_enemy_maps")
        if selected is None:
            return None

        enemies: list[core.Enemy] = []
        for index in selected:
            for enemy in locations[index][1]:
                if enemy not in enemies:
                    enemies.append(enemy)
        return enemies

    def get_enemy_locations(self) -> list[tuple[str, list[core.Enemy]]]:
        total = len(self.save_file.enemy_guide)
        locations: list[tuple[str, list[core.Enemy]]] = []

        story = [
            ("EoC Ch.1", r"^stageNormal0\.csv$"),
            ("EoC Ch.2", r"^stageNormal1_\d+\.csv$"),
            ("EoC Ch.3", r"^stageNormal2_\d+\.csv$"),
            ("ItF Ch.1", r"^stageSpace07_\d+\.csv$"),
            ("ItF Ch.2", r"^stageSpace08_\d+\.csv$"),
            ("ItF Ch.3", r"^stageSpace09_\d+\.csv$"),
            ("CotC Ch.1", r"^stageW04_\d+\.csv$"),
            ("CotC Ch.2", r"^stageW05_\d+\.csv$"),
            ("CotC Ch.3", r"^stageW06_\d+\.csv$"),
        ]
        for label, pattern in story:
            enemies = EnemyEditor.scan_stage_files(pattern, total)
            if enemies:
                locations.append((label, enemies))

        for map_id in range(49):
            enemies = EnemyEditor.scan_stage_files(
                r"^stageRN%03d_\d+\.csv$" % map_id, total
            )
            if enemies:
                locations.append(("SOL %03d" % map_id, enemies))

        return locations

    @staticmethod
    def scan_stage_files(pattern: str, total: int) -> list[core.Enemy]:
        dir = core.Path.get_data_folder().add("game_data")
        found: set[int] = set()

        versions = core.GameDataGetter.get_all_downloaded_versions()
        for cc in core.CountryCode.get_all():
            for version in versions.get(cc, []):
                data_local = (
                    dir.add(cc.get_code()).add(version.to_string()).add("DataLocal")
                )
                if not data_local.exists():
                    continue
                try:
                    file_names = os.listdir(data_local.path)
                except OSError:
                    continue
                for file_name in file_names:
                    if not re.match(pattern, file_name):
                        continue
                    path = data_local.add(file_name)
                    if not path.exists():
                        continue
                    data = path.read()
                    if data is None:
                        continue
                    found |= EnemyEditor.read_enemy_ids(data, total)

        return [core.Enemy(id) for id in sorted(found)]

    @staticmethod
    def read_enemy_ids(data, total: int) -> set[int]:
        found: set[int] = set()
        lines = data.to_str().split("\n")
        for i, line in enumerate(lines):
            if i > 60:
                break
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            cell = line.split(",")[0].strip()
            if not cell.isdigit():
                continue
            enemy_id = int(cell)
            if 0 <= enemy_id < total:
                found.add(enemy_id)
        return found

    @staticmethod
    def from_save_file(
        save_file: core.SaveFile,
    ) -> tuple[EnemyEditor | None, list[core.Enemy]]:
        enemy_editor = EnemyEditor(save_file)
        current_enemies = enemy_editor.select([])
        if current_enemies is None:
            return None, []
        return enemy_editor, current_enemies

    @staticmethod
    def edit_enemy_guide(
        save_file: core.SaveFile,
        current_enemies: list[core.Enemy] | None = None,
        enemy_editor: EnemyEditor | None = None,
    ):
        if enemy_editor is None or current_enemies is None:
            enemy_editor, current_enemies = EnemyEditor.from_save_file(save_file)
        if enemy_editor is None or not current_enemies:
            return

        dialog_creator.single_select_key(
            dialog_creator.Actions[None]
            .new()
            .add_new_key(
                "unlock_enemy_guide",
                lambda _: enemy_editor.unlock_enemy_guide(current_enemies),
            )
            .add_new_key(
                "remove_enemy_guide",
                lambda _: enemy_editor.remove_enemy_guide(current_enemies),
            ),
            "edit_enemy_guide",
        )
