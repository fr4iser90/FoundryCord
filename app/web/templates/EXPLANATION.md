# Template Structure

## Overview
The templates directory contains all HTML templates using Jinja2 templating engine. It follows a hierarchical structure:

```
templates/
├── layouts/       # Base templates that define the overall structure
├── components/    # Reusable UI components
├── views/         # Page-specific templates
└── debug/         # Debug-related templates
```

## Component Types

### 1. Layouts (`/layouts`)
- Base templates that other templates extend
- Define common structure (header, footer, navigation)
- Handle common assets and meta tags
Example:
```html
<!-- base_layout.html -->
<!DOCTYPE html>
<html>
  <head>{% block head %}{% endblock %}</head>
  <body>
    {% include "components/navbar.html" %}
    {% block content %}{% endblock %}
    {% include "components/footer.html" %}
  </body>
</html>
```

### 2. Components (`/components`)
- Reusable UI elements
- Included in other templates
- Self-contained functionality
Examples:
- `navbar.html` - Navigation bar
- `server_selector.html` - Server selection dropdown
- `footer.html` - Common footer

### 3. Views (`/views`)
- Page-specific templates
- Extend base layouts
- Organized by feature area:
  - `/views/auth/` - Authentication pages
  - `/views/bot/` - Bot management pages
  - `/views/owner/` - Owner control pages

### 4. Debug (`/debug`)
- Development and testing templates
- Not used in production
- Debugging tools and views

## Best Practices

1. **Template Inheritance**
   - All templates should extend a base layout
   - Use blocks for customizable sections
   ```html
   {% extends "layouts/base_layout.html" %}
   {% block content %}
     <!-- Page content here -->
   {% endblock %}
   ```

2. **Component Reuse**
   - Break common elements into components
   - Use includes for components
   ```html
   {% include "components/server_selector.html" %}
   ```

3. **Naming Conventions**
   - Use lowercase with underscores
   - Suffix with `.html`
   - Group related templates in subdirectories

4. **Asset References**
   - Use `url_for()` for static assets
   ```html
   <link href="{{ url_for('static', path='css/style.css') }}" rel="stylesheet">
   ```

5. **Template Organization**
   - Keep templates close to their related views
   - Match directory structure to URL structure
   - Group related templates together

## Common Issues to Avoid

1. **Logic in Templates**
   - ❌ Complex logic in templates
   - ❌ Database queries in templates
   - ✅ Pass processed data from views

2. **Duplicate Code**
   - ❌ Copy-pasted template sections
   - ✅ Use components and includes
   - ✅ Use macros for repeated patterns

3. **Inconsistent Structure**
   - ❌ Mixed naming conventions
   - ❌ Templates in wrong directories
   - ✅ Follow directory structure

4. **Asset Management**
   - ❌ Hardcoded asset paths
   - ❌ Missing asset references
   - ✅ Use url_for() for all assets
