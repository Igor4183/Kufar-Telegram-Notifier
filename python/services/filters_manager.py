import json

from pathlib import Path

from utils.logger import Logger


class FiltersManager:
    def __init__(self):
        self.path = Path(__file__).resolve().parents[2] / "data" / "filters.json"
        self.filters = self._load()

    def _load(self):
        try:
            with self.path.open("r", encoding="utf-8") as file:
                filters = json.load(file)

            if not isinstance(filters, dict):
                raise ValueError("Корень filters.json должен быть объектом.")

            # Logger.info(None, f"Файл фильтров загружен: {self.path}")
            return filters
        except FileNotFoundError:
            Logger.error(None, f"Файл фильтров не найден: {self.path}")
            raise
        except json.JSONDecodeError as error:
            Logger.error(None, f"Ошибка разбора файла фильтров {self.path}: {error}")
            raise
        except OSError as error:
            Logger.error(None, f"Ошибка чтения файла фильтров {self.path}: {error}")
            raise
        except ValueError as error:
            Logger.error(
                None, f"Некорректный формат файла фильтров {self.path}: {error}"
            )
            raise

    def get_regions(self):
        return self.filters.get("regions", [])

    def get_region(self, slug: str):
        for region in self.get_regions():
            if region.get("slug") == slug:
                return region
        return None

    def get_region_by_id(self, region_id: int):
        for region in self.get_regions():
            if region.get("id") == region_id:
                return region
        return None

    def get_areas(self, region_slug: str):
        region = self.get_region(region_slug)
        if region is None:
            return []
        return region.get("areas", [])

    def get_area_by_id(self, area_id: int):
        for region in self.get_regions():
            for area in region.get("areas", []):
                if area.get("id") == area_id:
                    return area
        return None

    def get_categories(self):
        return self.filters.get("categories", [])

    def get_category(self, slug: str):
        for category in self.get_categories():
            if category.get("slug") == slug:
                return category
        return None

    def get_category_by_id(self, category_id: int):
        for category in self.get_categories():
            if category.get("id") == category_id:
                return category
        return None

    def get_subcategory_by_id(self, category_id: int, subcategory_id: int):
        category = self.get_category_by_id(category_id)
        if category is None:
            return None
        for subcategory in category.get("subcategories", []):
            if subcategory.get("id") == subcategory_id:
                return subcategory
        return None

    def get_item_conditions(self):
        return self.filters.get("item_conditions", [])

    def get_item_condition_by_id(self, condition_id: int):
        for condition in self.get_item_conditions():
            if condition.get("id") == condition_id:
                return condition
        return None

    def get_seller_types(self):
        return self.filters.get("seller_types", [])

    def get_seller_type_by_id(self, seller_type_id: int):
        for seller_type in self.get_seller_types():
            if seller_type.get("id") == seller_type_id:
                return seller_type
        return None

    def get_sort_types(self):
        return self.filters.get("sort_types", [])

    def get_sort_type_by_id(self, sort_type_id: int):
        for sort_type in self.get_sort_types():
            if sort_type.get("id") == sort_type_id:
                return sort_type
        return None

    def get_query_fields(self):
        return self.filters.get("query_options", {}).get("fields", [])

    def get_query_field(self, slug: str):
        for field in self.get_query_fields():
            if field.get("slug") == slug:
                return field
        return None
