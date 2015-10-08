/**
   * Generates a random string containing numbers and letters
   * @param  {number} length The length of the string
   * @return {string} The generated string
   */

   jQuery.support.core = true;

  var client_id = 'b4121f9ee2fe41ffbfafc9d8dd19e6e1';
  var redirect_uri = 'http://localhost:5000/callback';


function login(){
      var scope = 'user-read-private user-read-email playlist-modify-public';
      var url = 'https://accounts.spotify.com/authorize?response_type=code&client_id=' +
                            client_id + '&scope=' + scope + '&redirect_uri=' + redirect_uri;

      document.location.href = url;
  }

function duplicate_playlist(id, name){
    alert(name);
    alert(JSON.stringify({'id': id, 'name': name}));
    // $.post('/duplicate',
    //         data=JSON.stringify({'id': id, 'name': name}),
    //         dataType="json",
    //         success=function(data){window.location.href='/';}
    //       );
}