from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class Sector:
    def __init__(self, sector_name):
        self.sector_id = self._get_next_id()
        self.sector_name = sector_name
        
    def _get_next_id(self):
        response = supabase.table("sector").select("sector_id").order("sector_id", desc=True).limit(1).execute()
        if response.data:
            return response.data[0]['sector_id'] + 1
        else:
            return 1
    
    def to_dict(self):
        return {
            "sector_id": self.sector_id,
            "sector_name": self.sector_name
        }