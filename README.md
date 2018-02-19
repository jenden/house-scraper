# houseScraper

This application was made to pull data about Vancouver list housing prices and listing details from [REW.ca](www.rew.ca) and store the results in a database for evaluation. While selling prices are not listed, the number of listings, list prices, and duration of listing will be helpful metadata to assess the market.

### How it works

The application is given a set of areas to monitor. Once per day, the listings page for the area is crawled to find links for individual listings and the list price. The first time a property is encountered, the link for the full page is given to an extractor which parses the full page for property type, price, beds and baths, neighborhood, square footage, estimated taxes, strata fees, and various other features. Afterwards, only the listing and price are recorded to track how long the property is on the market.

The parsing process is expected to be run on a VM in AWS and data is saved to a DynamoDB NoSQL database.







