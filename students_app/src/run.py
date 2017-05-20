"""
    Запуск вебсервера Flask.
"""

import os
import sys

sys.path.append(os.getcwd())

from src import app

if __name__ == "__main__":
    app.run(debug=True)
    # app.run()
