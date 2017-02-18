## Requesting changes
To avoid the repository from becoming a complete mess we **require** all changes
to be made using Pull Requests. All you have to do to contribute to the project
is to add a Pull Request with your new code and get it approved by at least one
of the other project members.

## Working with branches
So you want to make some changes to the repository, but don't feel completely
confident about how you go about doing it? Grab a coffe and read along to get up
to date on how to add your changes. :coffee:

**The 10,000 feet overview of the process of Pull Request is the following:**

(If you're not a project memeber, fork the repository to your own account
before proceeding with the steps below.)
* Clone the repo to your local computer and create a new branch.
* You work on your changes and commit them to your branch.
* When your satisfied with the changes you've made push your new branch to
GitHub.
* Create a Pull Request from your branch where you describe the changes that you
have made, and why you have made them. If you have fixed an open issue, here's
the place to leave a reference to it.
* Add a project member to review your changes.
* The project member will either approve the changes or leave feedback on what
has to be changed.
* If the changes are approved, go ahead and merge the changes. Otherwise, add
more commits according to the feedback recieved.

### Fork the repo to your own account
**If you're not a project member**; you need to fork the repository to your own
account before proceeding with the steps below. For instructions on how to fork
a repository on GitHub, check out [this](https://guides.github.com/activities/forking/)
guide.

### Clone the repo and create a branch
**If your a project member** - Clone the repo:
```
git clone https://github.com/kaszim/desktop-stream-viewer.git
```

**If your not a project member** - Clone your own fork!
```
git clone https://github.com/<your-github-name>/desktop-stream-viewer.git
```

Move into the newly cloned repo and create a new branch:
```
git checkout -b <your-branch-name>
```
where `<your-branch-name` is the name of your new branch.

**Pro Tip!** Add a descriptive name to your branch so it's easier to know what
it's all about.

### Make your changes
Make the small incremental changes that you want. Be sure to commit often with
well defined commits to the changes you've made. :+1:

### Push the branch to GitHub
When your satisfied with the changes and you're sure that everything is working
as it should, go ahead and push your branch to GitHub with:
```
git push -u origin <your-branch-name>
```

This will create a new branch on GitHub with the name `<your-branch-name>`.

### Create the Pull Request
* Open GitHub in a browser and switch to your new branch.
* Click on the `New pull request` button to open a new Pull Request.
* Write a descriptive Pull Request description.
* Request a review from one of the project members by adding that in the list on the right.

And you've done your part! Nicely done! :+1:
