from django.shortcuts import render, redirect

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from .forms import UserRegisterForm, LoginForm
from django.contrib import messages as flash_message
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
import requests
from .models import Story, Comment, Job, Pollopt, Poll, Base
from django.views.decorators.csrf import csrf_exempt
import json
from time import sleep
from datetime import datetime


# Route for signing up
def register(request):

    if request.method == "GET":
        form = UserRegisterForm()
        return render(request, "quickcheck_challenge/signup.html", {"form": form})

    elif request.method == "POST":

        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            flash_message.success(request, 'Account created! Please log in.')
            return HttpResponseRedirect(reverse("qc-login"))
        else:
            flash_message.warning(request, 'Please fix issues with your input!', "danger")
            return render(request, "quickcheck_challenge/signup.html", {"form": form})





# Route for logging in
def login_view(request):

    if request.method == "GET":
        logout(request) # Logout existing user
        form = LoginForm()
        return render(request, "quickcheck_challenge/login.html", {"form": form})

    elif request.method == "POST":

        value_next= request.POST.get('next') # Get redirect URL

        form = LoginForm(request.POST)

        # If form inputs are valid
        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            # Authenticate user
            user = authenticate(request, username=username, password=password)

            # Check if authentication was successful
            if user is not None:
                login(request, user)
                flash_message.success(request, 'Logged In!')
                if value_next:
                    return redirect(value_next)
                return HttpResponseRedirect(reverse("qc-index"))
            # Authentication failed
            else:
                flash_message.warning(request, 'Invalid Username and/or Password!', "danger")
                return render(request, "quickcheck_challenge/login.html", {"form": form})
        # Form inputs are not valid
        else:
            flash_message.warning(request, 'Please fix issues with your input!')
            return render(request, "quickcheck_challenge/login.html", {"form": form})





# Home page
def index(request):
    return render(request, "quickcheck_challenge/index.html")




# API route for getting items from our database
def index_api(request):

    # What I did here is a preferencial descision. I chose
    # to send the current items in our database first and then
    # sync in the background by making AJAX calls from the front-end.
    # The advantage is that the user won't have to wait a long time
    # before the page loads. Some might choose to sync first
    # before rendering which has an advantage of always being
    # up to date with HN. These are tradeoffs.

    # Get GET parameters
    start = request.GET.get("start")
    end = request.GET.get("end")
    type = request.GET.get("type")

    # Try to convert start and end to integers
    if start:
        try:
            start = int(start)
        except:
            return JsonResponse({"Error": "Please provide a vaild integer for 'start' query. See README.md for details."})
    if end:
        try:
            end = int(end)
        except:
            return JsonResponse({"Error": "Please provide a vaild integer for 'end' query. See README.md for details."})

    # If type is not any of the following
    if type not in ["all", "job", "story", "comment", "poll", "pollopt"]:
        return JsonResponse({"Error": "Please provide a vaild string for 'type' query. See README.md for details."})

    if type == "all":
        items = Base.objects.all().order_by("-time", "-HN_id")[start:end] # descending order from start  to send
    else:
        items = Base.objects.filter(type=type).order_by("-time", "-HN_id")[start:end] # descending order from start  to send

    # Artificially sleep for 2 secs so as to see effect of
    # infinte scroll on front-end.
    sleep(2)
    print(items.count())
    return JsonResponse([item.serialize() for item in items], safe=False)




# API route for creating (POSTing) new items to our database
@csrf_exempt
def create_item(request):

    # Only accept POST requests
    if not request.method == "POST":
        return JsonResponse({"Error": "Only POST requests allowed for this route."}, status=400)

    # User needs to be logged in before POSTing to our API
    if not request.user.is_authenticated:
        return JsonResponse({"Error": "You have to be logged in before POSTing."}, status=401)

    else:
        item = json.loads(request.body)

        got_from_HN = False
        deleted = item.get("deleted")
        type = item.get("type")
        by = request.user.username
        time = datetime.timestamp(datetime.now()) #In Unix time
        dead = item.get("dead")

        parent = item.get("parent")
        text = item.get("text")
        url = item.get("url")
        title = item.get("title")

        if type not in ["job", "story", "comment", "poll", "pollopt"]:
            return JsonResponse({"Error": "Please provide a vaild string for 'type' field. See README.md for details."}, status=400)

        if item["type"] == "job":

            Job.objects.create(
                got_from_HN = got_from_HN,
                deleted = deleted,
                type = type,
                by = by,
                time = time,
                dead = dead,
                
                text = text,
                url = url,
                title = title
            )

        elif item["type"] == "story":

            Story.objects.create(
                got_from_HN = got_from_HN,
                deleted = deleted,
                type = type,
                by = by,
                time = time,
                dead = dead,

                url = url,
                title = title
            )

        elif item["type"] == "comment":

            if parent:
            
                # Get the comment's parent: either another comment or the relevant story.
                parent_story = Base.objects.filter(id=int(parent), type="story").first()
                parent_comment = Base.objects.filter(id = int(parent), type="comment").first()

                if not parent_comment and not parent_story:
                    return JsonResponse({"Error": "Invalid parent. See README.md for details."}, status=400)

                parent =  parent_story if parent_story is not None else parent_comment 
                # Note: It is also possible that the parent could not be got
                # from our database. Since we synced from the latest 100 items,
                # the parent could be before the latest 100 items, which we do
                # not have. In this case the parent field will be null.

                if parent.got_from_HN:
                    return JsonResponse({
                        "Error": "You can only update or add comments to items that are not from HN."
                    }, status=401)

            Comment.objects.create(
                got_from_HN = got_from_HN,
                deleted = deleted,
                type = type,
                by = by,
                time = time,
                dead = dead,

                parent = parent,
                text = text
            )

        elif item["type"] == "poll":

            Poll.objects.create(
                got_from_HN = got_from_HN,
                deleted = deleted,
                type = type,
                by = by,
                time = time,
                dead = dead,

                title = title,
                text = text
            )

        elif item["type"] == "pollopt":

            # Get the pollopt's parent: a poll.
            if not parent:
                return JsonResponse({"Error": "Please provide parent id for the pollopt item."}, status=400)
            
            # Get the comment's parent: either another comment or the relevant story.
            parent_pollopt = Base.objects.filter(id=int(parent), type="poll").first()
        

            if not parent_pollopt:
                return JsonResponse({"Error": "Invalid parent. See README.md for details."}, status=400)


            if parent_pollopt.got_from_HN:
                return JsonResponse({
                    "Error": "You can only update or add pollopts to items that are not from HN."
                }, status=401)

            Pollopt.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                parent = parent_pollopt,
            )
    item = Base.objects.filter(by=request.user.username).last()

    return JsonResponse({"Success": f"Item {item.id} created!"}, status=201)



# Single item page
def item(request, item_id):
    return render(request, "quickcheck_challenge/item.html", {"item_id": item_id})




# Route for updating and deleting an item
@csrf_exempt
def item_api(request, item_id):

    # Only accept "PUT", "DELETE", "GET" requests
    if request.method not in ["PUT", "DELETE", "GET"]:
        return JsonResponse({"Error": "Only GET, PUT or DELETE requests allowed for this route."}, status=400)


    # Query for requested item
    try:
        item = Base.objects.get(id=item_id)
        if item.type == "job":
            item = Job.objects.get(id=item_id)
        elif item.type == "story":
            item = Story.objects.get(id=item_id)
        elif item.type == "comment":
            item = Comment.objects.get(id=item_id)
        elif item.type == "poll":
            item = Poll.objects.get(id=item_id)
        elif item.type == "pollopt":
            item = Pollopt.objects.get(id=item_id)
    except Base.DoesNotExist:
        return JsonResponse({"Error": "Item not found."}, status=404)

    
    if request.method == "PUT":
        # User needs to be logged in before updating or deletion
        if not request.user.is_authenticated:
            return JsonResponse({"Error": "You have to be logged in."}, status=401)

        if not item.by == request.user.username:
            return JsonResponse({"Error": "You can only update items you create."}, status=401)

        data = json.loads(request.body)

        if not data: return JsonResponse({"Error": "No data for update."}, status=400)
        # Don't update items got from HN.
        if item.got_from_HN:
            return JsonResponse({"Error": "You can't update an item got from HN."}, status=400)

        # Try and get PUT parameters and update the item
        if data.get("deleted") is not None:
            item.deleted = data["deleted"]

        if data.get("dead") is not None:
            item.dead = data["dead"]

        if data.get("text") is not None:
            item.text = data["text"]

        if data.get("url") is not None:
            item.url = data["url"]
            
        if data.get("title") is not None:
            item.title = data["title"]

        item.save()

        return JsonResponse({"Success": "Updated."}, status=201)

    elif request.method == "DELETE":
        # User needs to be logged in before updating or deletion
        if not request.user.is_authenticated:
            return JsonResponse({"Error": "You have to be logged in."}, status=401)
        if not item.by == request.user.username:
            return JsonResponse({"Error": "You can only update items you create."}, status=401)
        # Don't delete items got from HN
        if item.got_from_HN:
            return JsonResponse({"Error": "You can't delete an item got from HN."}, status=400)
        
        item.delete()

        return JsonResponse({"Success": "Item deleted."})

    elif request.method == "GET":

        # For some reason, the serialize() method doesn't work
        # for items who have parent_ids
        try:
            return JsonResponse(item.serialize())
        except:
            return JsonResponse(Base.serialize(item))


# Route for recurring sync, called every 5mins from front-end
def sync(request):

    # Get latest item id from HN
    try:
        maxid = requests.get("https://hacker-news.firebaseio.com/v0/maxitem.json?print=pretty")
    except:
        return JsonResponse({"Error": "Sorry, an error occured1"}, status=400)
    maxid = maxid.json()

    # Get last synced item from our database
    last_synced_item = Base.objects.exclude(HN_id=None).last()
    # Get last synced item id
    last_synced_item_id = last_synced_item.HN_id

    # Sync from last synced to latest item in HN
    for index in range(last_synced_item_id + 1, maxid):

        print(f"Getting item {index}...")
        try:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{index}.json?print=pretty")
        except:
            return JsonResponse({"Error": "Sorry, an error occured2"}, status=400)
        item = item.json()

        if Base.objects.filter(HN_id=int(item["id"])).exists():
            continue

        if item["type"] == "job":

            Job.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),
                
                text = item.get("text"),
                url = item.get("url"),
                title = item.get("title")
            )

        elif item["type"] == "story":

            Story.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                descendants = item.get("descendants"),
                score = item.get("score"),
                title = item.get("title"),
                url = item.get("url")
            )

        elif item["type"] == "comment":
            
            if item.get("parent") != None:
                # Get the comment's parent: either another comment or the relevant story.
                parent_story = Base.objects.filter(HN_id=int(item.get("parent")), type="story").first()
                parent_comment = Base.objects.filter(HN_id = int(item.get("parent")), type="comment").first()

            parent =  parent_story if parent_story is not None else parent_comment 
            # Note: It is also possible that the parent could not be got
            # from our database. Since we synced from the latest 100 items,
            # the parent could be before the latest 100 items, which we do
            # not have. In this case the parent field will be null.
            Comment.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                parent = parent,
                text = item.get("text")
            )

        elif item["type"] == "poll":

            Poll.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                descendants = item.get("descendants"),
                score = item.get("score"),
                title = item.get("title"),
                text = item.get("text")
            )

        elif item["type"] == "pollopt":

            # Get the pollopt's parent: a poll.
            if item.get("parent") != None:
                parent_pollopt = Pollopt.objects.filter(HN_id = int(item.get("parent"))).first()

            Pollopt.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                parent = parent_pollopt,
                score = item.get("score")
            )

    return JsonResponse({"Success": "Synced."})






# Route for initial sync (getting the latest 100 posts from HN after which we'd now
# begin syncing every 5 mins).
# I only had to call this once, but you can visit this route to
# clear the database first, get latest 100 items from HN and 
# start syncing from there.
def initial_sync(request):

    # Delete all entries in database
    Job.objects.all().delete()
    Story.objects.all().delete()
    Comment.objects.all().delete()
    Poll.objects.all().delete()
    Pollopt.objects.all().delete()
    Base.objects.all().delete()

    # Get latest item id from HN
    maxid = requests.get("https://hacker-news.firebaseio.com/v0/maxitem.json?print=pretty")
    maxid = maxid.json()

    # For each item, starting from latest item - 100 up to latest item
    for index in range(maxid - 100, maxid):

        print(f"Getting item {index}...")
        try:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{index}.json?print=pretty")
        except:
            return JsonResponse({"Error": "Sorry, an error occured3"}, status=400)
        item = item.json()

        if Base.objects.filter(HN_id=int(item["id"])).exists():
            continue

        # If item type is "job"
        if item["type"] == "job":

            # Save item to Job table
            Job.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),
                
                text = item.get("text"),
                url = item.get("url"),
                title = item.get("title")
            )
        
        # If item type is "story"
        elif item["type"] == "story":

            # Save item to Story table
            Story.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                descendants = item.get("descendants"),
                score = item.get("score"),
                title = item.get("title"),
                url = item.get("url")
            )

        # If item type is "comment"
        elif item["type"] == "comment":
            
            # If comment has a parent
            if item.get("parent") != None:
                # Get the comment's parent: either another comment or the relevant story.
                parent_story = Base.objects.filter(HN_id=int(item.get("parent")), type="story").first()
                parent_comment = Base.objects.filter(HN_id = int(item.get("parent")), type="comment").first()

            # Note: It is also possible that the parent could not be got
            # from our database. Since we synced from the latest 100 items,
            # the parent could be before the latest 100 items, which we do
            # not have. In this case the parent field will be null.
            parent =  parent_story if parent_story is not None else parent_comment 

            # Save item to Comment table
            Comment.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                parent = parent,
                text = item.get("text")
            )

        # If item type is "poll"
        elif item["type"] == "poll":

            # Save item to Poll table
            Poll.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                descendants = item.get("descendants"),
                score = item.get("score"),
                title = item.get("title"),
                text = item.get("text")
            )
        
        # If item type is "pollopt"
        elif item["type"] == "pollopt":

            # Get the pollopt's parent: a poll.
            if item.get("parent") != None:
                parent_pollopt = Pollopt.objects.filter(HN_id = int(item.get("parent"))).first()
            
            # Save item to Pollopt table
            Pollopt.objects.create(
                HN_id=item["id"],
                got_from_HN = True,
                deleted = item.get("deleted"),
                type = item.get("type"),
                by = item.get("by"),
                time = item.get("time"),
                dead = item.get("dead"),

                parent = parent_pollopt,
                score = item.get("score")
            )

    return HttpResponse("Done.")
