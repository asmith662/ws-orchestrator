from src.models.general.config import logger
from src.models.general.users import Users


class App:
    def __init__(self):
        # start logger
        self.logging_enabled = bool(logger())

        # get logged-in users
        self.users = Users()
        if len(self.users.users) != 1:
            print(f'Multiple logged on users detected: ' + ', '.join([u.name for u in self.users.users]))
            prompt = \
                input()
        # authentication starts app
        self.is_authenticated

    # Classmethods -----------------------------------------------------------------------------------------------------


    # Methods ----------------------------------------------------------------------------------------------------------

