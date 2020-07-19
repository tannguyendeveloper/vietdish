# VietDish

[https://vietdish.herokuapp.com](https://vietdish.herokuapp.com/)

VietDish is a web application that allows users to search for, review, and favorite authentic Vietnamese and fusion recipes. VietDish was built with Python, Flask, PostgresDB, HTML, CSS, JavaScript and jQuery and is powered by the Spoonacular API.

## Features:

- Login with Google for easy and convenient user account creating
- Search for recipes by recipe title or ingredients
- Review recipes. Registered users can rate and write reviews for recipes.
- Favorite recipes. Registered users can bookmark their favorite recipes for quick access when they log back in.
- View review breakdowns. Hovering over the number of reviews will reveal a popup that shows a breakdown of the recipe&#39;s reviews by user ratings.
- Filter and order reviews of recipes by date or rating.

## Spoonacular API:

VietDish uses the Spoonacular API to source recipes and search results. This API has some noted deficiencies:

- VietDish uses a free access account to Spoonacular which limits the amount of requests VietDish can make. To remedy this, the application caches search results to an SQLite database and stores that data for an hour max to comply with Spoonacular&#39;s terms of use.
- Search results don&#39;t always come out how we would expect. Although, there is a parameter in their documentation that searches for recipes by the title, sometimes there are no results even if the title is typed out exactly.
