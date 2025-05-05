"""
Service layer for handling Dashboard Component Definitions.
"""
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.shared.interfaces.logging.api import get_web_logger
# Import the repository interface (Domain Layer)
from app.shared.domain.repositories.dashboards import DashboardComponentDefinitionRepository
# Import the repository implementation (Infrastructure Layer) for type hinting in factory/DI
from app.shared.infrastructure.repositories.dashboards import DashboardComponentDefinitionRepositoryImpl
# Import the ORM model
from app.shared.infrastructure.models.dashboards import DashboardComponentDefinitionEntity
# Import the Pydantic schemas for validation and response structuring
from app.web.interfaces.api.rest.v1.schemas.dashboard_component_schemas import (
    ComponentDefinitionSchema,
    ComponentMetadataSchema,
    ComponentConfigFieldSchema,
    PreviewHintsSchema
)

logger = get_web_logger()

class DashboardComponentService:
    """Service responsible for dashboard component definition logic."""

    def __init__(self, session: AsyncSession):
        """Initializes the service with an async session and repository."""
        self.session = session
        # Instantiate the repository implementation here
        self.repo: DashboardComponentDefinitionRepository = DashboardComponentDefinitionRepositoryImpl(session)
        logger.debug("DashboardComponentService initialized.")

    async def list_definitions(
        self,
        dashboard_type: Optional[str] = None,
        component_type: Optional[str] = None
    ) -> List[ComponentDefinitionSchema]:
        """Retrieves, parses, and validates component definitions."""
        logger.info(f"Service: Listing component definitions (dashboard_type={dashboard_type}, component_type={component_type})")
        
        # 1. Fetch raw entities from the repository
        db_definitions: List[DashboardComponentDefinitionEntity] = await self.repo.list_definitions(
            dashboard_type=dashboard_type,
            component_type=component_type
        )
        
        valid_definitions: List[ComponentDefinitionSchema] = []
        
        # 2. Iterate, parse JSON, validate with Pydantic, and build response schemas
        for entity in db_definitions:
            try:
                # Ensure definition is not None and is a dict (or parse from string)
                if entity.definition is None:
                    logger.warning(f"Skipping definition ID {entity.id} (key: {entity.component_key}) due to null definition.")
                    continue
                    
                definition_data: dict
                if isinstance(entity.definition, str):
                    definition_data = json.loads(entity.definition)
                elif isinstance(entity.definition, dict):
                    definition_data = entity.definition
                else:
                    logger.warning(f"Skipping definition ID {entity.id} (key: {entity.component_key}) due to unexpected definition type: {type(entity.definition)}.")
                    continue

                # Use Pydantic models to parse and validate the nested structure within the JSON
                # We assume the JSON structure directly matches our nested Pydantic schemas
                # Pydantic will raise ValidationError if the structure or types don't match
                validated_definition = ComponentDefinitionSchema(
                    id=entity.id,
                    component_key=entity.component_key,
                    dashboard_type=entity.dashboard_type,
                    component_type=entity.component_type,
                    # Pydantic automatically tries to parse nested dicts into sub-models
                    metadata=definition_data.get('metadata', {}),
                    config_schema=definition_data.get('config_schema', []),
                    preview_hints=definition_data.get('preview_hints', None) # Optional
                )
                
                valid_definitions.append(validated_definition)
                
            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to parse JSON definition for component ID {entity.id} (key: {entity.component_key}): {json_err}", exc_info=False)
            except ValidationError as validation_err:
                logger.error(f"Validation failed for component definition ID {entity.id} (key: {entity.component_key}): {validation_err}", exc_info=False)
            except Exception as e:
                logger.error(f"Unexpected error processing component definition ID {entity.id} (key: {entity.component_key}): {e}", exc_info=True)
        
        logger.info(f"Service: Returning {len(valid_definitions)} valid component definitions.")
        return valid_definitions 