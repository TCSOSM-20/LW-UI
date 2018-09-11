function openModalCreateUser(args) {

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

function openModalEditUser(args) {
    var url = '/admin/users/'+args.user_id;
    console.log(url)
    $("#formEditUser").attr("action", url);
    select2_groups = $('#projects_edit').select2({
        placeholder: 'Select Projects',
        width: '100%',
        ajax: {
            url: '/projects/list',
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

    select2_single = $('#default_project_edit').select2({
        placeholder: 'Select Default Project',
        width: '100%',
        ajax: {
            url: '/projects/list',
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

    $('#modal_edit_user').modal('show');
}

function deleteUser(user_id, name) {
    var delete_url = '/admin/users/'+user_id+'/delete';
    bootbox.confirm("Are you sure want to delete "+name+"?", function (confirm) {
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