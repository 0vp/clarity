
<background>
- we are a brand reputation tracking platform, what we do is webscrape on trustpilot, their own website, yelp, google reviews, news, blogs, forums, etc and get the reviews in a day to day basis. 

we help brands to track their reputation and to be aware of discussions and information about their brand, allowing them to take action and respond to the information in real-time.
</background>

<tasks>
DATABASE:
- crease a database in the /be.
- structure the database like this:
    /be/brands/{brand_name}/day_{date_time}_data.json
    - store any data that you want to store in the database, at minimum, we need to store the date, the url/src of information, a score of how it will affect the brand reputation, and a summary of the information (max 1-2 sentences).
    - we need to store the data in a way that is easy to query and analyze. 

ENDPOINTS:
- ways to fetch the data from the database.
- ways to scrape the data from the internet for the brand, to create th entry in the database.
</tasks>

<technicals>
- tester.py - a script that showcases how we can use the browser.cash API to create a task and get the result.
- seperation of concerns, not everything should be in the /be directory, add sub folders and stuff. also keep the prompt in a prompt.py to ensure easy to read and modify.
</technicals>
