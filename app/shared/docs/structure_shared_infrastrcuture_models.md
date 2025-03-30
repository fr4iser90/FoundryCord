# SQLAlchemy-Modelle für die HomeLab Discord Bot-Infrastruktur

Dieses Verzeichnis enthält die SQLAlchemy-ORM-Modelle, die als Brücke zwischen der Domänenschicht und der Datenbank dienen.

## Modell vs. Entität

In unserem DDD-Ansatz unterscheiden wir zwischen:

- **Domain-Entitäten** (`app/shared/domain/*/entities/`): Enthalten Geschäftslogik und -regeln
- **Infrastructure-Modelle** (`app/shared/infrastructure/models/`): Definieren Datenbankschema und -beziehungen

## Modell-Typ-Hierarchie

1. **Base Model** (`base.py`):
   - Grundlegende SQLAlchemy-Konfiguration
   - Gemeinsame Attribute (id, created_at, updated_at)
   - Meta-Konfiguration

2. **Subdomänen-Modelle**:
   - Jede Subdomäne hat ein eigenes Unterverzeichnis
   - Modelle sind nach ihrer domänenspezifischen Funktion benannt
   - Alle erben von der `Base`-Klasse

## Repository-Übersetzung

Die Repository-Implementierungen in `app/shared/infrastructure/repositories/` sind verantwortlich für:

1. Umwandlung von Domain-Entitäten zu Datenbank-Modellen (Speichern)
2. Umwandlung von Datenbank-Modellen zu Domain-Entitäten (Laden)
3. Ausführung von Datenbankabfragen

Beispiel:
```python
# Umwandlung SQLAlchemy → Domain-Entität
def _entity_to_domain(user_entity: AppUserEntity) -> User:
    return User(
        id=user_entity.id,
        username=user_entity.username,
        email=user_entity.email
    )

# Umwandlung Domain-Entität → SQLAlchemy
def _domain_to_entity(user: User) -> AppUserEntity:
    return AppUserEntity(
        id=user.id,
        username=user.username,
        email=user.email
    )
```

## Beziehung zur Clean Architecture

Diese SQLAlchemy-Modelle gehören zur äußersten Schicht der Clean Architecture - der **Infrastrukturschicht**. Sie haben keine Kenntnisse über die Geschäftslogik und Anwendungsfälle, sondern dienen nur der Datenpersistenz.
