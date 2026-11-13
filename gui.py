from src.loaders.catalog import Catalog
from src.ui.app import App

if __name__=="__main__":
    catalog= Catalog()
    catalog.load_all()
    App(catalog).mainloop()