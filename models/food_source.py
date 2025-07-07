from models.sector import Sector

class FoodSource(Sector):
    def __init__(self, sector_name, food_id, name_en, name_id, unit, emisi):
        super().__init__(sector_name)
        self.food_id = food_id
        self.name_en = name_en
        self.name_id = name_id
        self.unit = unit
        self.emisi = emisi
    
    def to_dict(self):
        return {
            "id": self.food_id,
            "sector_id": self.sector_id,
            "name_en": self.name_en,
            "name_id": self.name_id,
            "unit": self.unit,
            "emisi": self.emisi
        }