$(function() {
  var bgDim = $("#backgroundDim");
  var searchBar = $("#SearchBar");
  searchBar.on("focus", function(){
        bgDim.css('display', 'block');
        searchBar.animate({width:"480px"}, 300);
  });
  searchBar.on("blur", function(){
        bgDim.hide();
        searchBar.animate({width:"300px"}, 300);
  });
});
