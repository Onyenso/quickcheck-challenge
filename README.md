# Challenge

This challenge was created per the specifications [here](https://form.jotform.com/211856214308452).


# API

You'll be able to get and post items using this application's API.

In order to be able to post, update and delete items, you need to have an account. This is so that only the creator of an item can update or delete it.


The application supports the following routes:

## `GET /index_api`

Sending a GET request to `/index_api` will return a list of all the items
in the database in reverse chronological order, except if you specify
some GET parameters.

| GET parameter   | Description       |
| ---------------   | ----------        |
| type              | required, string - the type of item. One of "job", |
|                   | "story", "comment", "poll", "pollopt", "all". Use "all" to get all |
|                   | types.             |
| start             | optional, integer - the index from which to begin sliciing |
|                   | the list from. Deafult is 0 (get items from the beginning). |
| end               | optional, integer - the index at which to end slice. The list will |
|                   | include items up to but not including item at the specified |
|                   | index. |



All items have some of the following properties. Properties in bold are guaranteed to
always have a value:

**`id`**: An integer. The items unique id in our database.

`HN_id`: An integer. For an item that was synced from HN, this will be its id from HN's API. It will be null if item was not from HN's API.

**`got_from_HN`**: A boolean. True if the item was got from HN's API and False if from one of our application users.


`deleted`: A boolean. True if the item is deleted in HN's API.

**`type`**: A string. The type of item. One of "job", "story",
"comment", "poll", or "pollopt".


`by`: A string. The username of the item's author. If the item was created by
one of this application's users, this field will always have a value.

`time`: An integer. Creation date of the item, in Unix time.

`dead`: A boolean. True if the item is dead in HN's API.

`parent_id`:  An integer. The item's parent id.

`text`: A string. The comment, story or poll text. HTML.

`descendants`: An integer. In the case of stories or polls, the total comment count.

`score`: An integer. The story's score, or the votes for a pollopt.

`title`: A string. The title of the story, poll or job.

`url`: A string. The URL of the story.


 For example, if you send a GET request to `/index_api?type=all&end=2`, you might get a JSON response like the below (representing two items):
```
 [
     {  
        "id": 12,
        "HN_id": 8917,
        "got_from_HN": 1,
        "deleted": 0,
        "type": "comment",
        "by": "Alphadev",
        "time": 1207886576,
        "dead": 1,
        "parent_id": 67,
        "text": "Hello, there!"
    },
    {
        "id": 13,
        "HN_id": 8918,
        "got_from_HN": 0,
        "deleted": 1,
        "type": "story",
        "by": "Alphadev",
        "time": 1207886579,
        "dead": 1,
        "descendants": 12,
        "score": 2,
        "title": "Django Models",
        "url": "https://example.com"
    }
 ]
 ```

## POST /create_item

Making a POST request to this route creates an item in the application's database. When creating an item, your request must include the parameters marked as required, other parameters are optional but encouraged.

From the logic in posting a comment to `/create_item`, you cannot update (add comments to) any item got from HN. You can only update an item if the item was created with our API.

Also, you'll need to have an account and signed in to create a new item.


| POST parameter   | Description        |
| ---------------   | ----------        |
| type              | required, string - the type of item. One of "job", |
|                   | "story", "comment", "poll", "pollopt". |
| deleted           | optional, boolean - denoting whether to mark this item as deleted or|
|                   | not.               |
| dead              | optional, boolean - denoting whether to mark this item as dead or|
|                   | not.               |
| parent            | optional, integer - the unquie id of the item's parent in our ||                   | database, if it exits. |
| text              | optional, string - the comment, story or poll text. HTML |
| url               | optional, string - the URL of the story. |
| title             | optional, string - the title of the story, poll or job

On making a successful POST request to this route, a JSON like below with status 201 is returned:

```
{
    "Success": "Item 41 created!
}
```


## GET /items/<item_id>

Sending a GET request to `/items/<item_id>` where item_id is an integer id for an item in our database will return a JSON representation of the single item, like below:
```
{
  "id": 310,
  "HN_id": 28900364,
  "got_from_HN": true,
  "deleted": null,
  "type": "comment",
  "by": "mbrodersen",
  "time": 1634509729,
  "dead": null,
  "parent": null,
  "text": "Not understanding how your software fits in the overall system and not understanding what is important <i>is</i> a beginner mistake."
}
```


## PUT /items/<item_id>

The application also supports updating items by API. Making a PUT request to `/items/<item_id>` like below will update the item whose id is item_id:
```
fetch(`/item/${item_id}`, {
  method: 'DELETE',
  body: JSON.stringify({
      text: "Hey bro",
  })
})
.then(response => response.json())
.then(result => {
    // Print result
    console.log(result);
})
.catch(error => console.log(error))
```

The fields you can update by making this request are: deleted, dead, text, url and title. Of course, you can only update items you created and you cannot update items got from HN API. Upon successful update, a JSON like below will be returned:
```
{"Success": "Updated."}
```


## DELETE /items/<item_id>

You can also delete items by API by simply making a DELETE request to `/items/<item_id>`. As usual, you can only delete items you created and you cannot delete items got from HN API.


#### Good to know

From HN's API, there's a property called 'kids' which is an array of the
ids of the item's comments. The field was not implemented in this application, but the child comments of an item can be got by querying for all comments whose parent ids are that particular item.


NB: I acknowledge this code can be optimized in many ways. Seeing as I am timed for this challenge, I implemented a more brute-force than efficient solution. I do look forward to feedback, whether or not I get the role.
