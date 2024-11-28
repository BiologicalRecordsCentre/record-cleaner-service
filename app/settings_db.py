from sqlmodel import Session, select

from app.sqlmodels import System


class DbSetting:
    """A descriptor for database settings.

    Refer to https://docs.python.org/3/howto/descriptor.html"""

    def __init__(self, default):
        # A default value to use if the setting is not yet in the database.
        self.default = default
        # A function to convert from database storage back to python type.
        if type(default) is bool:
            self.convert = lambda x: bool(int(x))
        elif type(default) is int:
            self.convert = lambda x: int(x)
        else:
            self.convert = lambda x: str(x)

    def __set_name__(self, owner, name):
        self.name = name
        self.obj_name = '_' + name

    def __get__(self, obj, objtype=None):
        value = getattr(obj, self.obj_name, None)
        if value is None:
            with Session(obj.engine) as session:
                response = session.exec(
                    select(System)
                    .where(System.key == self.name)
                ).one_or_none()
                if response is None:
                    value = self.default
                else:
                    value = self.convert(response.value)

            setattr(obj, self.obj_name, value)
        return value

    def __set__(self, obj, value):
        setattr(obj, self.obj_name, value)
        with Session(obj.engine) as session:
            response = session.exec(
                select(System)
                .where(System.key == self.name)
            ).one_or_none()
            if response is None:
                # Insert.
                session.add(System(key=self.name, value=value))
            else:
                # Update.
                response.value = value
                session.add(response)
            session.commit()


class DbSettings:
    maintenance_mode = DbSetting(False)
    maintenance_message = DbSetting('Normal operation.')
    rules_commit = DbSetting('')
    rules_updating = DbSetting(False)
    rules_updating_now = DbSetting('')
    rules_update_result = DbSetting(
        '{"ok": true, "data": "Rules not yet updated."}')

    def __init__(self, engine):
        self.engine = engine

    def list(self):
        """List all database settings."""
        result = {}
        # Loop through vars of DbSettings Class to find descriptors
        for name, var in vars(DbSettings).items():
            if isinstance(var, DbSetting):
                result[name] = getattr(self, name)

        return result
