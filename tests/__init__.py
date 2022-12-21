import sys


# Для корректных импортов собственных модулей (db, ...) в conftest.py
sys.path = ["", ".."] + sys.path[1:]
