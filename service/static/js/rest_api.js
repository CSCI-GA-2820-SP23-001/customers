$(function () {

    
    // *********************
    //  C O N S T A N T S
    // *********************
    const STATUS = {
        ACTIVE: 'ACTIVE',
        SUSPENDED: 'SUSPENDED'
    };
    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_first_name").val(res.first_name);
        $("#customer_last_name").val(res.last_name);
        $("#customer_email").val(res.email);
        $("#customer_password").val(res.password);
        $("#customer_status").val(res.status);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_first_name").val("");
        $("#customer_last_name").val("");
        $("#customer_email").val("");
        $("#customer_password").val("");
        $("#customer_status").val("STATUS.ACTIVE");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Customer
    // ****************************************

    $("#create-btn").click(function () {

        let first_name = $("#customer_first_name").val();
        let last_name = $("#customer_last_name").val();
        let email = $("#customer_email").val();
        let password = $("#customer_password").val();
        let status = $("#customer_status").val();

        let data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "status": status
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/customers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });