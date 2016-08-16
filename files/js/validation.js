function validate_pwd(password) {
  if(password != $.trim(password)) {
    return false;
  }
  if(password.length < 6) {
    return false;
  }
  if(password.search(/ /) != -1) {
    return false;
  }

  return true;
}

function validate_user(user) {
  var RegularExpression = /[!@#$%^&*()_+-=,.<>/\?\\{}\[\]|]/;
  if(user != $.trim(user)) {
    return 1;
  }
  if(user.length < 6) {
    return 2;
  }
  if(user.search(/ /) != -1) {
    return 3;
  }
  if(user.search(RegularExpression) != -1) {
    return 4;
  }
  
  return true;
}

function validate_email(email) {
  var RegularExpression = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
  if(email != $.trim(email)) {
    return false;
  }
  
  if(email.search(RegularExpression) == -1) {
    return false;
  }
  
  return true; 
}