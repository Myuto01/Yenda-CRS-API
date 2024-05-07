<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1>Edit Bus Information</h1>
    <form action="" method="post" id="edit-bus-form">
        <!-- Display bus information for editing -->
        <label for="bus-type">Bus Type:</label>
        <input type="text" id="bus-type" name="bus_type" value="{{ bus.bus_type }}"><br>

        <label for="number-plate">Number Plate:</label>
        <input type="text" id="number-plate" name="number_plate" value="{{ bus.number_plate }}"><br>

        <label for="total-seats">Total Seats:</label>
        <input type="number" id="total-seats" name="total_seats" value="{{ bus.total_seats }}"><br>

        <label for="status">Status:</label>
        <select id="status" name="status">
            <option value="active" {% if bus.status == 'active' %}selected{% endif %}>Active</option>
            <option value="inactive" {% if bus.status == 'inactive' %}selected{% endif %}>Inactive</option>
        </select><br>

        <button type="submit" id="saveChangesButton">Save Changes</button>
    </form>
</body>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
<script>
    $(document).ready(function() {
        const accessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1NDkxMzMxLCJpYXQiOjE3MTM3NjMzMzEsImp0aSI6IjgxM2E5MWI4MTFlODRkNTZhMWVjZTllNGJlMjk0MmY0IiwidXNlcl9pZCI6OX0.HHv0PIPifk1CupzjBVnlFKVoMWtxbLd1qie7hTa4WRw";

        // Retrieve the value of 'selectedBusId' from localStorage
    const selectedBusId = localStorage.getItem('selectedBusId');

$("#edit-bus-form").submit(function(e) {
    e.preventDefault();

    // Construct the payload object
    var payload = {
        bus_id: selectedBusId,
        bus_type: $("input[name='bus_type']").val(),
        total_seats: $("input[name='total_seats']").val(),
        number_plate: $("input[name='number_plate']").val(),
        status: $("#status").val(),
        // Adjust this line according to your actual field for features
        features: $("#features").val() || [], // Get selected features
    };

    // Send AJAX request
    $.ajax({
        url: 'http://127.0.0.1:8000/api/v1/edit_bus/',
        type: 'POST',
        data: JSON.stringify(payload),
        contentType: 'application/json',
        beforeSend: function(xhr) {
            xhr.setRequestHeader("Authorization", "JWT " + accessToken);
        },
        success: function(response) {
            console.log('Success:', response);
            // Remove the item with key 'selectedBusId' from localStorage
           localStorage.removeItem('selectedBusId');
        },
        error: function(xhr, status, error) {
            console.error('Error:', error);
        }
    });
});
});
</script>
</html>