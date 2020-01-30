var selectField = document.getElementById("SearchCat");

selectField.addEventListener("change", function() {
  if (selectField.value=='name') {
    alert('name');
  }

  else if (selectField.value=='brand') {
    alert('brand');
  }

  else if (selectField.value=='sub-category') {
    alert('sub-category');
  }

  else if (selectField.value=='serial-no') {
    alert('serial-no');
  }

  else if (selectField.value=='price') {
    alert('price');
  }

  else if (selectField.value=='quantity') {
    alert('quantity');
  }

  else {
    alert('none');
  }
});
