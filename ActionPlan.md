┌─────────────────┐   ┌───────────────────┐   ┌────────────────────┐
│ Dashboard       │   │ Dashboard Factory │   │ Dashboard Registry │
│ Controller      │◄──┤ Creates from DB   │◄──┤ Stores definitions │
└─────────────────┘   └───────────────────┘   └────────────────────┘
        ▲                      ▲                        ▲
        │                      │                        │
        │                      │                        │
┌─────────────────┐   ┌───────────────────┐   ┌────────────────────┐
│ View Components │   │ Component Factory │   │ Component Registry │
│ (UI Elements)   │◄──┤ Creates from DB   │◄──┤ Stores components  │
└─────────────────┘   └───────────────────┘   └────────────────────┘