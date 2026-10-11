Install from GitHub with pipx:
```
pipx install git+https://github.com/schlopshow/hsm-calender
```

Start the local web app on port 5000:
```
hacksmarter-calendar
```

The calendar opens at http://localhost:5000.

The initial calendar includes four weekly series, each scheduled for 13
occurrences (three months). Click any calendar day to view every event and its
details for that day.

The download buttons generate the selected monthly calendar or weekly
schedule. If Poppler is not installed, the application downloads a PDF
fallback instead of failing.
