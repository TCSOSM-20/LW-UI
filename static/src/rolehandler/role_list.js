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
    
    $("#formEditRole").attr("action", url);
    

    $('#modal_edit_role').modal('show');
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
                dataType: "json",
                contentType: "application/json;charset=utf-8",
                success: function (result) {
                    //$('#modal_show_vim_body').empty();
                    dialog.modal('hide');
                    table.ajax.reload();
                },
                error: function (result) {
                    dialog.modal('hide');
                    bootbox.alert("An error occurred.");
                }
            });
        }
    })

}