var selectField = document.getElementById("SearchCat");
var inputField = document.getElementById("SearchBar");

selectField.addEventListener("change", filter);
inputField.addEventListener("keyup", filter);

function filter() {
    var input = inputField.value.toLowerCase();
    var table = document.getElementById("table-body");
    var tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
      var value = tr[i].querySelector('.' + selectField.value).innerText.toLowerCase();

      if (value.indexOf(input) > -1) {
          tr[i].style.display = "";
        }
      else {
          tr[i].style.display = "none";
        }
    }
}
