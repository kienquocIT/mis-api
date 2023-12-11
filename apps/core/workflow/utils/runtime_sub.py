class WFSupportFunctionsHandler:

    @classmethod
    def get_manager_upper_group(cls, group):
        if group.parent_n:
            if group.parent_n.first_manager_id:
                return group.parent_n.first_manager_id
        return None
