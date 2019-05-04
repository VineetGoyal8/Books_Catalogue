Books Catalogue WEB APPLICATION

This project is made for the Udacity FullStack Course.
This will help you to manage all your books which will particularly be displayed under the respective Author of the book.

.......................................................

Explanation of the contents of files:
=> This projects main file is project.py
=> The SQL database is stored in database_setup.py
=> The initial data is entered already in initial_data.py
=> All the templates used in this project are stored in Templates folder.
=> The background image and the CSS file is available in static folder.

.......................................................

PREREQUISITES:
=> Python
=> HTML
=> CSS
=> Flask
=> Postgresql

.......................................................

How To Run:

=> Launch the Vagrant VM from inside the vagrant folder with:
=> vagrant up
=> vagrant ssh
=> Then move inside the Item_catalogue folder:
=> cd /vagrant / Item_Catalogue
=> Then run the main file:
=> python project.py
=> After this command you are able to run the full flegded application at the URL:
=>  http://localhost:5000/

.......................................................


JSON:

The following are open to the public:

 /author/JSON - Return JSON for all the authors

 /author/<int:author_id>/JSON - Return JSON of all the books for a author

 /author/<int:author_id>/book/<int:book_id>/JSON - Return JSON for a book