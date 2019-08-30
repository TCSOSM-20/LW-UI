/*
   Copyright 2019 EveryUP srl

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

function openModalCreateRole(args) {

    $('#modal_new_role').modal('show');
}

function openModalEditRole(args) {
    var url = '/admin/roles/' + args.role_id;
    var url_update = '/admin/roles/' + args.role_id+'/update';
    var dialog = bootbox.dialog({
        message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>',
        closeButton: false
    });
    $.ajax({
        url: url,
        type: 'GET',
        headers: {
            "Accept": 'application/json'
        },
        contentType: false,
        processData: false
    })
    .done(function (response,textStatus, jqXHR) {
        dialog.modal('hide');
        $("#formEditRole").attr("action", url_update);
        $('#modal_edit_role').modal('show');
        $('#edit_rolename').val(response['name'])
        $('#edit_permissions').val(JSON.stringify(response['permissions']))
        if(response['root'] === true){
            $("#edit_root").attr("checked", true);
        }
        else {
            $("#edit_root").attr("checked", false);
        }
    }).fail(function(result){
        dialog.modal('hide');
        var data  = result.responseJSON;
        var title = "Error " + (data.code ? data.code: 'unknown');
        var message = data.detail ? data.detail: 'No detail available.';
        bootbox.alert({
            title: title,
            message: message
        });
    });
    
}

function deleteRole(role_id, name) {
    var delete_url = '/admin/roles/' + role_id + '/delete';
    bootbox.confirm("Are you sure want to delete " + name + "?", function (confirm) {
        if (confirm) {
            var dialog = bootbox.dialog({
                message: '<div class="text-center"><i class="fa fa-spin fa-spinner"></i> Loading...</div>',
                closeButton: false
            });
            $.ajax({
                url: delete_url,
                type: 'GET',
                headers: {
                    "Accept": 'application/json'
                },
                contentType: false,
                processData: false
            })
            .done(function (response,textStatus, jqXHR) {
                bootbox.alert({
                    title: "Result",
                    message: "Role deleted.",
                    callback: function () {
                        dialog.modal('hide');
                        table.ajax.reload();
                    }
                });
            }).fail(function(result){
                dialog.modal('hide');
                var data  = result.responseJSON;
                var title = "Error " + (data.code ? data.code: 'unknown');
                var message = data.detail ? data.detail: 'No detail available.';
                bootbox.alert({
                    title: title,
                    message: message
                });
            });
        }
    })

}