/* selection tabs actions */

const tab_authenticate = document.getElementById("tab_authenticate");
const tab_groups = document.getElementById("tab_groups");
const tab_users = document.getElementById("tab_users");

const select_tab_authenticate = document.getElementById("select_tab_authenticate");
const select_tab_groups = document.getElementById("select_tab_groups");
const select_tab_users = document.getElementById("select_tab_users");


select_tab_authenticate.onclick = function(e){
    select_tab_authenticate.className = "nav-link active";
    select_tab_groups.className = "nav-link";
    select_tab_users.className = "nav-link";

    tab_authenticate.style.display = "inline";
    tab_groups.style.display = "none";
    tab_users.style.display = "none";
}

select_tab_groups.onclick = function(e){
    select_tab_authenticate.className = "nav-link";
    select_tab_groups.className = "nav-link active";
    select_tab_users.className = "nav-link";

    tab_authenticate.style.display = "none";
    tab_groups.style.display = "inline";
    tab_users.style.display = "none";
}

select_tab_users.onclick = function(e){
    select_tab_authenticate.className = "nav-link";
    select_tab_groups.className = "nav-link";
    select_tab_users.className = "nav-link active";

    tab_authenticate.style.display = "none";
    tab_groups.style.display = "none";
    tab_users.style.display = "inline";
}


