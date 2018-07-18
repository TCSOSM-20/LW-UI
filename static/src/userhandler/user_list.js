function openModalCreateUser(args) {
    console.log(args)
    // load projects list
    select2_groups = $('#projects').select2({
        placeholder: 'Select Projects',
        width: '100%',
        ajax: {
            url: args.projects_list_url,
            dataType: 'json',
            processResults: function (data) {
                projects = [];
                if (data['projects']) {
                    for (d in data['projects']) {
                        var project = data['projects'][d];
                        projects.push({id: project['_id'], text: project['name']})
                    }
                }

                return {
                    results: projects
                };
            }
        }
    });

    $('#modal_new_user').modal('show');
}

function deleteUser(delete_url) {
    bootbox.confirm("Are you sure want to delete?", function (confirm) {
        if (confirm) {
            var dialog = bootbox.dialog({
                message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>',
                closeButton: false
            });
            $.ajax({
                url: delete_url,
                dataType: "json",
                contentType: "application/json;charset=utf-8",
                success: function (result) {
                    //$('#modal_show_vim_body').empty();
                    dialog.modal('hide');
                    location.reload();
                },
                error: function (result) {
                    dialog.modal('hide');
                    bootbox.alert("An error occurred.");
                }
            });
        }
    })

}