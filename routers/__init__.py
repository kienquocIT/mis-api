# Routers use db when event call hit DB (default always use)
# define DB map apps
DB_ROUTERS_LOG_APP_LABELS = ("hr",)
DB_ROUTERS_LOG_MAP_MODELS = {
    "hr": ("Employee",),
}


# class config
class LogRouter:
    db_config = "hr"
    route_app_labels = DB_ROUTERS_LOG_APP_LABELS
    route_app_labels_models = DB_ROUTERS_LOG_MAP_MODELS

    def __init__(self):
        pass

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            # print('Read log: ', model._meta.app_label)
            return self.db_config
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            # print('Write log: ', model._meta.app_label)
            return self.db_config
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.route_app_labels
                and obj2._meta.app_label in self.route_app_labels
        ) or (
                obj1._meta.app_label not in self.route_app_labels
                and obj2._meta.app_label not in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            if db == self.db_config:
                # print('Allow: ', app_label, model_name, db)
                return True
        else:
            if db == "default":
                return True
        # print('Denied: ', app_label, model_name, db)
        return False
