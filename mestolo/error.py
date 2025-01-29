class MestoloError(Exception):
    """Base class for exceptions in Mestolo."""

class MenuError(MestoloError):
    """Errors relating to menus."""

class RecipeInternalError(MestoloError):
    """Errors that come from inside the recipe trying to run."""
