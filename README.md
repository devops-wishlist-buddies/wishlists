![github actions](https://github.com/devops-wishlist-buddies/wishlists/actions/workflows/workflow.yml/badge.svg)
[![codecov](https://codecov.io/gh/devops-wishlist-buddies/wishlists/branch/main/graph/badge.svg?token=DQRGYGIC60)](https://codecov.io/gh/devops-wishlist-buddies/wishlists)

# Wishlists

This repo is for the Wishlists squad in DevOps Fall 2021 class.

## Development process

1. Select an issue from the top of the "Sprint Backlog" column on the board, assign it to yourself, and move into the In Progress column (you can always put it back).
2. On your machine create a new branch naming it following the format `{issue number}__{summary-of-what-youre-doing}` (ex. 13__setting-up-vagrant-file).
3. Implement requested features and tests.
4. Commit your changes. Keep commit messages informative, would be really great if you prepend the commit message with the issue number.
5. Push local branch to remote, and create a pull request to `main` branch. Add everyone else as reviewers. Move the issue to the "Review" column.
6. When there is at least one approval on your pull request, have someone else merge your changes (the idea here is to have several pairs of eyes on the code to avoid mistakes). Then move your issue to the "Done" column.
7. Success!

## How to perform unit tests

Once the vagrant is up and you are inside the ```/vagrant``` folder, type the following command inside your terminal.

```
python -m unittest tests.test_product
```

Please replace the ```tests.test_product``` with the module name you want to test. The followings are available at this time.

```
python -m unittest tests.test_product
python -m unittest tests.test_wishlist
```

## How to invoke nosetests

Once the vagrant is up and you are inside the ```/vagrant``` folder, type the following command inside your terminal.

```
nosetests --with-spec --spec-color
```

## How to perform BDD testing

Once the vagrant is up and you are inside the ```/vagrant``` folder, make sure you have a ```.env``` file inside the ```/vagrant``` folder. Otherwise, execute the following command inside your terminal.

```
cp dot-env-example .env
```

Execute the following command to start the service with ```honcho```.

```
honcho start &
```
Execute the following command to perform BDD testing with ```behave```.
```
behave
```
Once the BDD testing is done, execute the following command to bring the service back to the foreground.
```
fg
```
Then, press ```CTRL+C``` to stop the service if necessary.


## How to run the flask service

Once the vagrant is up and you are inside the ```/vagrant``` folder.

```
FLASK_APP=service:app flask run -h 0.0.0.0 -p 3000
```

Or, one can invoke ```honcho``` to start the application with the following command.

```
honcho start
```
Make sure to create a local ```.env``` file based on the information in ```dot-env-example```. Otherwise, the ```honcho start``` may not work properly.
