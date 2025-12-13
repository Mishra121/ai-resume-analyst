

def calendar_availability_tool(employee_ids: list):
    # MOCK DATA
    return {
        "availability": {
            "next_7_days": {
                "09:00-11:00": ["Mon", "Wed"],
                "14:00-16:00": ["Tue", "Thu"]
            }
        }
    }
