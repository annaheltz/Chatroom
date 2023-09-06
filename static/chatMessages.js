let timeoutID;
let timeout = 1000;

function setup() 
{
    //add event listener to the post button
    document.getElementById("theButton").addEventListener("click", makePost);
    //set timeout 
    timeoutID = window.setTimeout(poller, timeout);
}

//old thought on how to tell the user that their room was deleted
function sendDeletedMessage()
{
    document.getElementById("delete").style.visibility = "visible";
}

//adding a new post
function makePost() {
    //getting the new post
    const chat = document.getElementById("message").value
    
    fetch("/new_chat", {
            method: "post",
            headers: { "Content-type": "application/x-www-form-urlencoded; charset=UTF-8" },
            body: `chat=${chat}`
        })
        .then((response) => {
            return response.json();
        })
        .then((result) => {
            //only adding one new post, so call updateFeedNew
            updateFeedNew(result);
            //clear input field
            clearInput();
        })
        .catch(() => {
            console.log("Error adding the new chat");
        });
}

//checking if other people made posts
function poller() {
    console.log("Polling for new items");
    fetch("/chats")
        .then((response) => {
            if(!response.ok && response.status === 404)//this means their room was deleted, so we need to tell them to leave the room
            {
                //make the message visible and dont show them the chats
                document.getElementById('delete').style.visibility = "visible";
                document.getElementById("chatTable").style.visibility = "hidden";
                document.getElementById("chat1").style.visibility = "hidden";
            }
            else
            {
                return response.json();
            }
            
        })
        .then((result) => {
            //there are new chats from other users, so call updateFeed
            updateFeed(result);
        })
        .catch(() => {
            console.log("Error fetching the new chats");
        });
}

//this updates the messages from other users into the chat room
function updateFeed(result) {

    const tab = document.getElementById("chatTable");

    //delete rows from chatroom messages
    while (tab.rows.length > 0) {
        tab.deleteRow(0);
    }

    for (var i = 0; i < result.length; i++) {
        addRow(result[i]);
    }
    timeoutID = window.setTimeout(poller, timeout);
}

//this updates the single new chat added from this user
function updateFeedNew(result) {
    for (var i = 0; i < result.length; i++)
    {
        addRow(result[i]);
    }
    timeoutID = window.setTimeout(poller, timeout);
}

//add row to table
function addRow(row) {
    const tableRef = document.getElementById("chatTable");
    const newRow = tableRef.insertRow();
    const newText = document.createTextNode(row);
    newRow.appendChild(newText);

}

//clear input from the text box
function clearInput() 
{
    document.getElementById("message").value = "";
}

window.addEventListener("load", setup); //call set up on load

