from src.core.infra.database import init_db
from src.ui.app import App

if __name__ == '__main__':
    init_db()
    App().mainloop()
