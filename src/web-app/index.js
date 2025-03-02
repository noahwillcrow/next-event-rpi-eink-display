let calendars = [];

async function loadCalendarsAsync() {
    calendars = await fetch('/calendars').then(response => response.json()).then(data => data.calendars);
}

async function updateCalendarsAsync(newCalendars) {
    calendars = await fetch('/calendars', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ calendars: newCalendars })
    }).then(response => response.json()).then(data => data.calendars);
}

function createCalendarListHeader() {
    return `
        <tr class="calendar-row">
            <th>Priority</th>
            <th id="calendar-name-header">Name</th>
            <th>Type</th>
            <th>Move up</th>
            <th>Move down</th>
            <th>Rename</th>
            <th>Delete</th>
        </tr>
    `;
}

function createCalendarListRow(calendar, priority) {
    return `
        <tr class="calendar-row">
            <td class="calendar-priority">${priority}</td>
            <td class="calendar-name"><input type="text" class="calendar-name-input" value="${calendar.name}" /></td>
            <td class="calendar-type">${calendar.type}</td>
            <td><button class="move-calendar-up-btn">^</button></td>
            <td><button class="move-calendar-down-btn">v</button></td>
            <td><button class="rename-calendar-btn">💾</button></td>
            <td><button class="remove-calendar-btn">x</button></td>
        </tr>
    `;
}

function displayCalendarsList() {
    var calendarsListTable = document.getElementById('calendars-list');
    calendarsListTable.innerHTML = createCalendarListHeader() + calendars.map(createCalendarListRow).join('');
}

$("#calendars-list").on("click", ".move-calendar-down-btn", function() {
    var row = $(this).closest("tr");
    var rowPriority = parseInt(row.find(".calendar-priority").text());
    if (rowPriority >= calendars.length - 1) {
        return;
    }

    var newCalendars = [];
    for (var i = 0; i < calendars.length; i++) {
        if (i == rowPriority + 1) {
            newCalendars[i] = calendars[rowPriority];
        } else if (i == rowPriority) {
            newCalendars[i] = calendars[rowPriority + 1];
        } else {
            newCalendars[i] = calendars[i];
        }
    }

    updateCalendarsAsync(newCalendars).then(() => displayCalendarsList());
});

$("#calendars-list").on("click", ".move-calendar-up-btn", function() {
    var row = $(this).closest("tr");
    var rowPriority = parseInt(row.find(".calendar-priority").text());
    if (rowPriority < 0) {
        return;
    }

    var newCalendars = [];
    for (var i = 0; i < calendars.length; i++) {
        if (i == rowPriority - 1) {
            newCalendars[i] = calendars[rowPriority];
        } else if (i == rowPriority) {
            newCalendars[i] = calendars[rowPriority - 1];
        } else {
            newCalendars[i] = calendars[i];
        }
    }

    updateCalendarsAsync(newCalendars).then(() => displayCalendarsList());
});

$("#calendars-list").on("click", ".rename-calendar-btn", function() {
    var row = $(this).closest("tr");
    var rowPriority = parseInt(row.find(".calendar-priority").text());
    var newName = row.find(".calendar-name-input").val();
    var newCalendars = calendars.map((calendar, index) => index === rowPriority ? { ...calendar, name: newName } : calendar);
    updateCalendarsAsync(newCalendars).then(() => displayCalendarsList());
});

$("#calendars-list").on("click", ".remove-calendar-btn", function() {
    var row = $(this).closest("tr");
    var rowPriority = parseInt(row.find(".calendar-priority").text());
    var newCalendars = calendars.filter((_, index) => index !== rowPriority);
    updateCalendarsAsync(newCalendars).then(() => displayCalendarsList());
});

$("#add-ics-calendar-btn").click(function() {
    var newCalendars = calendars.concat({ name: $("#new-ics-calendar-name").val(), type: 'ics-url', url: $("#new-ics-calendar-url").val() });
    updateCalendarsAsync(newCalendars).then(() => displayCalendarsList());
});

$(async function() {
    await loadCalendarsAsync();
    displayCalendarsList();
});