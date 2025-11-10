from enum import Enum
from typing import List, Dict

class StaticRole(Enum):
    USER_MANAGER = {"name": "UserManager", "description": "Manages users within organizations"}
    DEPARTMENT_MANAGER = {"name": "DepartmentManager", "description": "Manages departments within organizations"}
    CATEGORIES_MANAGER = {"name": "CategoriesManager", "description": "Manages categories within organizations"}

    @property
    def name_value(self) -> str:
        return self.value["name"]

    @property
    def description_value(self) -> str:
        return self.value["description"]

    @classmethod
    def all_roles(cls) -> List[Dict[str, str]]:
        return [{"name": role.name_value, "description": role.description_value} for role in cls]