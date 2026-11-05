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

To add an event, click a day and choose **Add event**. The event form supports
daily, weekly, monthly, and yearly repeats, including an interval and an end
date or occurrence count. A series created with **Never** repeats for one year
to keep the in-memory calendar bounded. Individual occurrences or an entire
series can be deleted from the day details panel.

The download buttons generate the selected monthly calendar or weekly
schedule. If Poppler is not installed, the application downloads a PDF
fallback instead of failing.
