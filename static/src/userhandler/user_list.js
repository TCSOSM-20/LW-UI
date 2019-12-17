/*
   Copyright 2018 EveryUP srl

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an  BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

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
                        projects.push({ id: project['_id'], text: project['name'] })
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

function openModalEditUserCredentials(args) {
    var url = '/admin/users/' + args.user_id;
    var user_projects = args.projects ? args.projects.split(',') : [];
    $("#formEditUser").attr("action", url);
    $("#projects_old").val(user_projects.toString());
    $('#projects_edit').val(null).trigger('change');
    $('#default_project_edit').val(null).trigger('change');
    $('#edit_password').val('');
    if (user_projects.length > 0) {
        // Create a DOM Option and pre-select by default
        var newOption = new Option(user_projects[0], user_projects[0], true, true);
        // Append it to the select
        $('#default_project_edit').append(newOption).trigger('change');

        for (var d in user_projects) {
            var project = user_projects[d];
            // Create a DOM Option and pre-select by default
            var newOption = new Option(project, project, true, true);
            // Append it to the select
            $('#projects_edit').append(newOption).trigger('change');
        }

    }


    $('#modal_edit_user_credentials').modal('show');
}

function openModalEditUserRoleMap(user_id) {
    $("#formEditUserRoleMap").attr("action", '/admin/users/' + user_id);
    var dialog = bootbox.dialog({
        message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>',
        closeButton: false
    });
    $.ajax({
        url: '/admin/users/' + user_id + '/info',
        dataType: "json",
        contentType: "application/json;charset=utf-8",
        success: function (result) {
            dialog.modal('hide');
            resetMapGroup(result);
            $('#modal_edit_user_role_map').modal('show');
        },
        error: function (result) {
            dialog.modal('hide');
            bootbox.alert("An error occurred.");
        }
    });

}

function resetMapGroup(args) {
    var $formGroup = $('#modal_edit_proj_role_map_body');
    $formGroup.empty();
    $formGroup.append('<div class="proj-role-map-group-head">' +

        '<button type="button" class="btn btn-success btn-add btn-sm">+</button>' +
        '</div></br>');
    if (args['project_role_mappings'] && args['project_role_mappings'].length > 0) {

        for (i = 0; i < args['project_role_mappings'].length; ++i) {
            var mapping = args['project_role_mappings'][i];

            $formGroup.append('<div class="proj-role-map-group"> <div class="form-group">' +
                '<label  class="col-sm-2">Project* </label><div class="col-sm-3">' +
                '<input name="map_project_name" value="' + mapping.project_name + '" class="form-control input-sm" required></div>' +
                '<label class="col-sm-2">Role* </label>' +
                '<div class="col-sm-3">' +
                '<input name="map_role_name" value="' + mapping.role_name + '" class="form-control input-sm" required>' +
                '</div>' +
                '<button type="button" class="btn btn-danger btn-remove btn-sm">-</button></div></div>');
        }
    }




}

var addMapGroup = function (event) {
    event.preventDefault();

    var $formGroup = $('#modal_edit_proj_role_map_body');
    $formGroup.append('<div class="proj-role-map-group"> <div class="form-group">' +
        '<label  class="col-sm-2">Project* </label><div class="col-sm-3">' +
        '<input name="map_project_name" class="form-control input-sm" required></div>' +
        '<label class="col-sm-2">Role* </label>' +
        '<div class="col-sm-3">' +
        '<input name="map_role_name" class="form-control input-sm" required>' +
        '</div>' +
        '<button type="button" class="btn btn-danger btn-remove btn-sm">-</button></div></div>');

};

var removeMapGroup = function (event) {
    event.preventDefault();
    var $formGroup = $(this).closest('.proj-role-map-group');
    $formGroup.remove();
};

function deleteUser(user_id, name) {
    var delete_url = '/admin/users/' + user_id + '/delete';
    bootbox.confirm("Are you sure want to delete " + name + "?", function (confirm) {
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
                    table.ajax.reload();
                },
                error: function (result) {
                    dialog.modal('hide');
                    var data = result.responseJSON;
                    var title = "Error " + (data && data.code ? data.code : 'unknown');
                    var message = data && data.detail ? data.detail : 'No detail available.';
                    bootbox.alert({
                        title: title,
                        message: message
                    });
                }
            });
        }
    })

}

function validatePswOnCreate() {

    var confirm_password = document.getElementById("password2");
    if ($("#password").val() == $("#password2").val()) {
        $("#pwmatch").removeClass("glyphicon-remove");
        $("#pwmatch").addClass("glyphicon-ok");
        $("#pwmatch").css("color", "#00A41E");
        confirm_password.setCustomValidity("");
    } else {
        $("#pwmatch").removeClass("glyphicon-ok");
        $("#pwmatch").addClass("glyphicon-remove");
        $("#pwmatch").css("color", "#FF0004");
        confirm_password.setCustomValidity("Passwords Don't Match");
    }
}

function validatePswOnEdit() {

    var confirm_password = document.getElementById("edit_password2");
    if ($("#edit_password").val() == $("#edit_password2").val()) {
        $("#pwmatch_edit").removeClass("glyphicon-remove");
        $("#pwmatch_edit").addClass("glyphicon-ok");
        $("#pwmatch_edit").css("color", "#00A41E");
        confirm_password.setCustomValidity("");
    } else {
        $("#pwmatch_edit").removeClass("glyphicon-ok");
        $("#pwmatch_edit").addClass("glyphicon-remove");
        $("#pwmatch_edit").css("color", "#FF0004");
        confirm_password.setCustomValidity("Passwords Don't Match");
    }
}

$(document).ready(function () {
    $("#formEditUserRoleMap").submit(function (event) {
        event.preventDefault(); //prevent default action
        var post_url = $(this).attr("action"); //get form action url
        var request_method = $(this).attr("method"); //get form GET/POST method
        var form_data = new FormData(this); //Encode form elements for submission
        $.ajax({
            url: post_url,
            type: request_method,
            data: form_data,
            headers: {
                "Accept": 'application/json'
            },
            contentType: false,
            processData: false
        }).done(function (response, textStatus, jqXHR) {
            table.ajax.reload();
            $('#modal_edit_user_role_map').modal('hide');
        }).fail(function (result) {
            var data = result.responseJSON;
            var title = "Error " + (data.code ? data.code : 'unknown');
            var message = data.detail ? data.detail : 'No detail available.';
            bootbox.alert({
                title: title,
                message: message
            });
        });
    });

})