# Anchor

It can be assumed that the values ​​you receive are valid

Values ​​entered as "double" are converted to "float" - this has been done for convincing (python has float not double)

In the database file, there are 2 lines of code that you need to uncomment for the first time (you can comment on it after the first run)

Make sure you have all the import installed:
* sqlalchemy
* sqlalchemy.orm
* unittest
* typing
* fastapi
* flask_sqlalchemy.session
* json
* pydantic

You can't lookup from one spreadsheet to another

In the Debug configuration, in the Scripts parameter, I had this for debugging:
"app:app --reload"

Also, I startet the app via the terminal like this:
"uvicorn main:app --reload"

I didn't had time to do the integration test (Im in Thailand :) )
Hope you will find it's working for you

If you have any questions, please send a message or call :)

Thanks
