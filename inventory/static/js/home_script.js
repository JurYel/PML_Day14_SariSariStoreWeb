let id_;
let age_check = (id) => {
     //document.querySelector("#temp_field").value = id;
     id_ = id;
     let qty = $('input[name="qty-bought"]').val();
     $("#temp_field").val(id);
     $("#AgeCheckerModal").modal("show");
     $("#add-to-cart-form").attr('action', 'check_age/' + id + "/" + qty);
}

