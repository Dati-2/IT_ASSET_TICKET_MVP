# IT Asset & Ticket Management System — MVP Frontend

A lightweight frontend prototype built with HTML, CSS and vanilla JavaScript.

## Included modules
- Dashboard with asset and ticket summaries
- IT asset register: create, edit, delete, assign and filter
- Ticket management: create, edit status/priority, delete and search
- User management: create, edit, delete and search
- Responsive sidebar and modal forms

## Run the project
1. Extract the project folder.
2. Open `index.html` in a modern browser.
3. No package installation or build step is required.

You can also use the VS Code Live Server extension and select **Open with Live Server**.

## Demo data and storage
The app starts with sample records. Changes are stored in the browser's `localStorage` under `itDeskMvpData`. This is temporary frontend storage for demonstration only; it is not the final database.

To reset the demo data, open the browser developer console and run:
```js
localStorage.removeItem("itDeskMvpData");
location.reload();
```

## Planned next phase
- Build a Python Flask API
- Create SQLite tables for users, assets and tickets
- Replace localStorage operations with API requests
- Connect Flask to SQLite and test end-to-end flows

## Suggested database relationships
- `assets.assigned_to` references `users.id`
- `tickets.reported_by` references `users.id`

This is an MVP prototype, not a production-ready system. Authentication, access control, server-side validation, audit logging and backups are not included.
