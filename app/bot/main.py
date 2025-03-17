from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory

# After bot instantiation (assuming 'bot' is your HomelabBot instance)
bot.component_registry = ComponentRegistry()
bot.component_factory = ComponentFactory(bot.component_registry)
bot.register_default_components()  # Make sure this method exists on your bot instance 