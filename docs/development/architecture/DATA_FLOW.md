┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Data Collection │────▶│  Data Storage   │────▶│ Data Processing │
│    Services     │     │   (Database)    │     │    Services     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                               │
         │                                               ▼
┌─────────────────┐                           ┌─────────────────┐
│ Event Triggers  │◀──────────────────────────│  Data Access    │
│                 │                           │     Layer       │
└─────────────────┘                           └─────────────────┘
         │                                               │
         ▼                                               ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  UI Controller  │────▶│   View Models   │────▶│ Rendering Layer │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘

1. User clicks refresh button on dashboard
   │
   ▼
2. Button callback triggers refresh_dashboard method in controller
   │
   ▼
3. Controller calls service.get_dashboard_data() to fetch fresh data 
   │
   ▼
4. Service fetches data from repositories and transforms into view model
   │
   ▼
5. Controller gets template for dashboard type
   │
   ▼
6. Template renders data into embed
   │
   ▼
7. Controller updates message with new embed and view
   │
   ▼
8. Controller updates tracking data

## Related Documentation
- [Layer Definitions](./LAYERS.md) - Component layer organization
- [Dashboard Pattern](../patterns/DASHBOARD_PATTERN.md) - Dashboard implementation
- [Project Structure](../../ai/context/CORE.md) - Overall project organization
