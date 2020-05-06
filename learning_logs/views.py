from django.shortcuts import render, redirect
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
from django.http import Http404

# Create your views here.

def index(request):
    #the home page for Learning Log
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics':topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    #juest like we did in MyShell.py
    topic = Topic.objects.get(id=topic_id)
    #make suer the topic belongs to the current user
    if topic.owner != request.user:
        raise Http404
    # foreign key can be accessed using '_set'
    entries = topic.entry_set.order_by('-date_added')   # -date_added is descending order
    context = {'topic':topic, 'entries':entries}

    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    #Dispaly a blank form using the new_topic.html template
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request,topic_id):
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)

        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            form.save()
            return redirect('learning_logs:topic',topic_id=topic_id)
    
    context = {'form': form, 'topic': topic}
    return render(request, 'learning_logs/new_entry.html', context) 

@login_required
def edit_entry(request, entry_id):
    #Edit an existing entry.
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        #This qrgument tells Django to create the form prefilled
        # with information from the existing entry object.
        form = EntryForm(instance=entry)
    else:
        #POST data submitted; process date.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)
    
    context = {'entry':entry, 'topic':topic, 'form':form}
    return render(request, 'learning_logs/edit_entry.html', context)