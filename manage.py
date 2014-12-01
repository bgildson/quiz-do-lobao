# -*- coding: utf-8 -*-
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from quiz import app, db


migrate = Migrate(app, db)


manager = Manager(app)
#manager.add_command('run', app.run())
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()