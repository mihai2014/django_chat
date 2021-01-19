/*groups/users/etc list select update*/ 

const groups_select = document.getElementById("groups");
const switch_button = document.getElementById("group-name-select");
const group_name_input = document.querySelector('#group-name-input');

//update active groups/users/etc list (for incoming broadcast connexions data given by the server)
const dataSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/data/'
);


function removeOptions(selectElement) {
    var i, L = selectElement.options.length - 1;
    for(i = L; i >= 0; i--) {
       console.log(i, L); 
       selectElement.remove(i);
    }
 }

 function addOptions(selectElement,data){
    var result = Object.keys(data);
    for (var i = 0; i < result.length; i++) {
        key = result[i];
        val = data[key];

        var opt = document.createElement('option');
        opt.value = key;
        opt.innerHTML = val;
        selectElement.appendChild(opt);        
    }
 }


function init_select(target,data){
    removeOptions(target);
    addOptions(target,data);    
}

dataSocket.onmessage = function(e) {  //console.log(e.data)
    const data = JSON.parse(e.data);
    console.log(data);
    if (data.hasOwnProperty('socket_port')) {
        var socket_port = JSON.parse(data['socket_port']);
        window.socket_port = socket_port;
        document.getElementById("user_id").innerHTML =  socket_port;
    }
    if (data.hasOwnProperty('groups')) {    
        var groups = JSON.parse(data['groups']); 
        init_select(groups_select,groups);
    }
    if (data.hasOwnProperty('users1')) {    
        var users1 = JSON.parse(data['users1']); 
    }
    if (data.hasOwnProperty('users2')) {    
        var users1 = JSON.parse(data['users2']); 
    }
};

dataSocket.onclose = function(e) {
    alert("Connection closed! Reload page!");
};

/*end groups/users/etc list*/

/* new group defined => active switch */
group_name_input.oninput = function(e){
    var result = this.value.match(/^[A-Za-z0-9_]*$/); console.log(result);
    if (result == null) {
        switch_button.disabled = true;
        alert("Use only characters: A-Z a-z 0-9 _ and no whitespaces.");
    }else{
        switch_button.disabled = false;
    }
}
/* */

function switch_on(){  console.log("on")
   switch_button.checked = true; 
   var groupName = group_name_input.value;
   group_name_input.disabled = true;

   var ws = connect(groupName);
   window.ws = ws;   

}

function switch_off(){ console.log("off")
    switch_button.checked = false; 
    group_name_input.disabled = false;
    ws = window.ws;
    ws.close();    
}

/* select group -> deactivate input new group field */ 
switch_button.onclick = function(e) { 
    if(this.checked == true){
        switch_on();
    }else{
        switch_off();
    }
} 
/* end */ 

/* select group from list */

groups_select.onclick = function(e) { 
    var option_item = e.target
    var value = this.value;
    var index = this.selectedIndex;
    var itemName  = this.options[this.selectedIndex].innerHTML;
    //<option value="value">itemName</option>

    group_name_input.value = itemName;

    try {
        ws = window.ws;
        ws.close();           
    } catch (error) {}
    
    switch_on();
}    
  
/* end */

const display = document.querySelector('#chat-display');
const message_input = document.querySelector('#input');
const submit_button  = document.querySelector('#submit');

/* chat */

function connect(groupName){

    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/chat/'
        + groupName
        + '/'
        + userName    /*defined in base.html*/
        + '/'       
    );

    chatSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);   console.log(data)  
        display.value += (data.message + '\n');
        //scroll to end
        display.scrollTop = display.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed');
        display.value += "Connection closed!" + '\n';  
        //reset contact data panels(groups/users/etc)             
        group_name_input.disabled = false;
        switch_button.checked = false;     
    };

    message_input.focus();
    message_input.onkeydown = function(e) {
        if (e.keyCode === 13) {  // enter, return
            e.preventDefault();
            document.querySelector('#submit').click();
        }
    };

    document.querySelector('#submit').onclick = function(e) {
        //const messageInputDom = document.querySelector('#input');
        var message = message_input.value;
        chatSocket.send(JSON.stringify({
            'message': userName + "-" + window.socket_port + ": " + message,
        }));
        message_input.value = '';
    };



    return chatSocket;    
}
/* end chat*/