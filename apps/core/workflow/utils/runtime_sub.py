class WFSupportFunctionsHandler:

    @classmethod
    def get_assignee_node_in_wf(cls, collab, doc_employee_inherit):
        if collab.in_wf_option == 1 and doc_employee_inherit:  # BY POSITION
            if not doc_employee_inherit.group:
                raise ValueError('Employee inherit does not have group')
            if collab.position_choice == 1:  # 1st manager
                if not doc_employee_inherit.group.first_manager_id:
                    raise ValueError('1st manager is not defined')
                if doc_employee_inherit.group.first_manager_id == doc_employee_inherit.id:
                    return cls.get_manager_upper_group(doc_employee_inherit.group)
                return doc_employee_inherit.group.first_manager_id
            elif collab.position_choice == 2:  # 2nd manager
                if not doc_employee_inherit.group.second_manager_id:
                    raise ValueError('2nd manager is not defined')
                return doc_employee_inherit.group.second_manager_id
            elif collab.position_choice == 3:  # Beneficiary (Document inherit)
                return doc_employee_inherit.id
        elif collab.in_wf_option == 2:  # BY EMPLOYEE
            return collab.employee_id
        raise ValueError('Can not find assignee for this node')

    @classmethod
    def get_manager_upper_group(cls, group):
        if group.parent_n:
            if group.parent_n.first_manager_id:
                return group.parent_n.first_manager_id
        raise ValueError('1st manager is not defined')
