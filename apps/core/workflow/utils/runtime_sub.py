from apps.core.workflow.models import RuntimeLog


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
            if collab.position_choice == 2:  # 2nd manager
                if not doc_employee_inherit.group.second_manager_id:
                    raise ValueError('2nd manager is not defined')
                return doc_employee_inherit.group.second_manager_id
            if collab.position_choice == 3:  # Beneficiary (Document inherit)
                return doc_employee_inherit.id
        if collab.in_wf_option == 2:  # BY EMPLOYEE
            return collab.employee_id
        raise ValueError('Can not find assignee for this node')

    @classmethod
    def get_manager_upper_group(cls, group):
        if group.parent_n:
            if group.parent_n.first_manager_id:
                return group.parent_n.first_manager_id
        raise ValueError('1st manager is not defined')

    @classmethod
    def update_runtime_when_error(cls, runtime_obj):
        runtime_obj.state = 2  # finish
        runtime_obj.status = 2
        runtime_obj.save(update_fields=['state', 'status'])
        return True

    @classmethod
    def log_get_assignee_error(cls, stage_obj, is_system):
        return RuntimeLog.objects.create(
            runtime=stage_obj.runtime,
            stage=stage_obj,
            kind=1,  # in doc
            action=0,
            msg='Update data at zone',
            is_system=is_system,
        )
